import database as db

# 要导入的错题题号
WRONG_Q_NUMS = """
847
848
849
853
854
856
857
861
863
864
869
873
875
879
891
892
897
898
908
912
913
915
916
918
919
924
933
942
945
946
952
955
961
967
978
981
986
987
990
993
994
996
997
999
1000
1001
1002
1005
1006
1007
1008
1015
1019
1020
1023
1026
1027
1034
1038
1039
1041
1046
1052
1057
1060
1063
1068
1069
1070
1071
1072
1073
1076
1078
1079
1080
1082
1089
1091
1096
1099
1101
1103
1107
1118
1120
1121
1122
1123
1130
1132
1136
1139
1147
1150
1153
1156
1165
1170
1175
1176
1181
1183
1193
1194
1200
1205
1213
1215
1216
1218
1223
1225
1231
1235
1238
1247
1256
1259
1262
1264
1266
1267
1275
1279
1281
1285
1292
1294
1297
1312
1315
1322
1343
1349
1351
1352
1357
1359
1360
1364
1366
1369
1370
1375
1379
1380
1388
1389
1395
1396
1398
1407
1409
1410
1411
""".strip().split()


def import_wrong_questions():
    session = db.SessionLocal()

    try:
        # 去重
        q_nums = list(dict.fromkeys(
            str(n).strip()
            for n in WRONG_Q_NUMS
            if str(n).strip()
        ))

        print(f"准备导入 {len(q_nums)} 道错题...")
        print("-" * 50)

        # 查询题目
        questions = (
            session.query(db.Question)
            .filter(db.Question.q_num.in_(q_nums))
            .all()
        )

        # 建立题号 -> Question 映射
        question_map = {
            str(q.q_num).strip(): q
            for q in questions
        }

        added = []
        already_exists = []
        not_found = []

        for q_num in q_nums:

            question = question_map.get(q_num)

            # 题库不存在这个题号
            if not question:
                not_found.append(q_num)
                continue

            # 查看是否已经在错题集
            record = (
                session.query(db.WrongQuestion)
                .filter_by(question_id=question.id)
                .first()
            )

            if record:
                # 已经存在，不重复增加错误次数
                already_exists.append(q_num)
            else:
                # 新增错题
                record = db.WrongQuestion(
                    question_id=question.id,
                    wrong_count=1,
                    is_mastered=False
                )

                session.add(record)
                added.append(q_num)

        session.commit()

        print("\n导入完成！")
        print("=" * 50)

        print(f"输入题号数量：{len(q_nums)}")
        print(f"成功新增：{len(added)}")
        print(f"原本已存在：{len(already_exists)}")
        print(f"题库中未找到：{len(not_found)}")

        if not_found:
            print("\n⚠️ 以下题号在题库中没有找到：")
            print(", ".join(not_found))

        if added:
            print("\n✅ 成功加入错题集的题号：")
            print(", ".join(added))

        if already_exists:
            print("\nℹ️ 以下题号原本已经是错题，不重复增加次数：")
            print(", ".join(already_exists))

    except Exception as e:
        session.rollback()
        print("\n❌ 导入失败：")
        print(str(e))

    finally:
        session.close()


if __name__ == "__main__":
    import_wrong_questions()
