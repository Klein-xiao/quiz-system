from fastapi import FastAPI, UploadFile, File, Depends, Query, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import database as db
from pdf_parser import parse_pdf_questions
import datetime
import json
import asyncio
import io
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 1. 题库上传（进度流）
@app.post("/api/upload-pdf-progress")
async def upload_pdf_progress(
        file: UploadFile = File(...),
        clear_old: bool = Query(True),
        session: Session = Depends(db.get_db)
):
    async def generate_progress():
        if clear_old:
            session.query(db.WrongQuestion).delete()
            session.query(db.Question).delete()
            session.commit()
            yield f"data: {json.dumps({'status': 'info', 'message': '已清空旧数据库...', 'percent': 5})}\n\n"

        content = await file.read()
        yield f"data: {json.dumps({'status': 'info', 'message': '开始解析 PDF 文件...', 'percent': 15})}\n\n"
        await asyncio.sleep(0.1)

        questions = parse_pdf_questions(content)
        total = len(questions)
        yield f"data: {json.dumps({'status': 'info', 'message': f'成功切分出 {total} 道题目，开始入库...', 'percent': 30})}\n\n"

        count = 0
        for i, q in enumerate(questions):
            item = db.Question(q_num=q["q_num"], content=q["content"])
            session.add(item)
            count += 1
            if count % 5 == 0 or count == total:
                percent = 30 + int((count / total) * 65)
                msg = f"已入库 [{count}/{total}] 题 (题号: #{q['q_num']})"
                yield f"data: {json.dumps({'status': 'processing', 'message': msg, 'percent': percent})}\n\n"
                await asyncio.sleep(0.01)

        session.commit()
        yield f"data: {json.dumps({'status': 'completed', 'message': f'🎉 全部导入完成！共计 {count} 道题目', 'percent': 100})}\n\n"

    return StreamingResponse(generate_progress(), media_type="text/event-stream")


# 2. 需求 2：导入正确答案接口（支持 Excel/CSV 文件）
@app.post("/api/upload-answers")
async def upload_answers(
        file: UploadFile = File(...),
        session: Session = Depends(db.get_db)
):
    contents = await file.read()
    filename = file.filename.lower()

    try:
        # 使用 pandas 读取 csv 或 excel
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        # 兼容列名 (找包含 No / 题号 的列以及包含 Real Answer / 答案 的列)
        q_col = next((c for c in df.columns if any(k in str(c).lower() for k in ['no', '题号', 'number'])),
                     df.columns[0])
        ans_col = next(
            (c for c in df.columns if any(k in str(c).lower() for k in ['real', 'answer', '正确答案', '答案'])),
            df.columns[-1])

        updated_count = 0
        for _, row in df.iterrows():
            q_num = str(row[q_col]).strip().split('.')[0]  # 转字符串并抹去小数点
            real_ans = str(row[ans_col]).strip().upper()

            if q_num and real_ans in ['A', 'B', 'C', 'D']:
                question = session.query(db.Question).filter_by(q_num=q_num).first()
                if question:
                    question.real_answer = real_ans
                    updated_count += 1

        session.commit()
        return {"status": "success", "message": f"成功更新 {updated_count} 道题目的标准答案！"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")


# 3. 批量输入错题
@app.post("/api/mark-wrong-batch")
def mark_wrong_batch(q_nums: list[str] = Body(..., embed=True), session: Session = Depends(db.get_db)):
    cleaned_nums = [str(n).strip() for n in q_nums if str(n).strip()]
    matched_questions = session.query(db.Question).filter(db.Question.q_num.in_(cleaned_nums)).all()

    added_count = 0
    for q in matched_questions:
        record = session.query(db.WrongQuestion).filter_by(question_id=q.id).first()
        if record:
            record.wrong_count += 1
            record.is_mastered = False
        else:
            record = db.WrongQuestion(question_id=q.id)
            session.add(record)
        added_count += 1

    session.commit()
    return {"status": "success", "message": f"成功匹配并添加 {added_count} 道错题！"}


# 4. 获取题目列表
@app.get("/api/questions")
def get_questions(session: Session = Depends(db.get_db)):
    return session.query(db.Question).all()


# 5. 获取错题集
@app.get("/api/wrong-questions")
def get_wrong_questions(session: Session = Depends(db.get_db)):
    results = session.query(db.Question, db.WrongQuestion) \
        .join(db.WrongQuestion, db.Question.id == db.WrongQuestion.question_id) \
        .filter(db.WrongQuestion.is_mastered == False) \
        .order_by(db.WrongQuestion.wrong_count.desc()).all()

    return [{
        "id": q.id,
        "q_num": q.q_num,
        "content": q.content,
        "real_answer": q.real_answer,
        "wrong_count": w.wrong_count
    } for q, w in results]


# 6. 单个标错与消灭错题
@app.post("/api/mark-wrong/{question_id}")
def mark_wrong(question_id: int, session: Session = Depends(db.get_db)):
    record = session.query(db.WrongQuestion).filter_by(question_id=question_id).first()
    if record:
        record.wrong_count += 1
        record.is_mastered = False
    else:
        record = db.WrongQuestion(question_id=question_id)
        session.add(record)
    session.commit()
    return {"status": "success"}


@app.post("/api/master-question/{question_id}")
def master_question(question_id: int, session: Session = Depends(db.get_db)):
    record = session.query(db.WrongQuestion).filter_by(question_id=question_id).first()
    if record:
        record.is_mastered = True
        session.commit()
    return {"status": "success"}


@app.post("/api/clear-all")
def clear_all_data(session: Session = Depends(db.get_db)):
    session.query(db.WrongQuestion).delete()
    session.query(db.Question).delete()
    session.commit()
    return {"status": "success", "message": "题库与错题记录已完全清空！"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)