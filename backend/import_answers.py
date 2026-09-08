import csv
import os
import database as db

CSV_FILE_PATH = ""

ANSWER_DATA = """
847 A
848 D
849 C
853 B
854 A
856 D
857 D
861 A
863 A
864 B
869 C
873 BAC
875 D
879 B
891 A
892 C
897 CE
898 A
908 A
912 A
913 B
915 C
916 D
918 B
919 C
924 B
933 A
942 D
945 C
946 D
952 D
955 C
961 C
967 D
978 C
981 BE
986 C
987 D
990 A
993 C
994 C
996 A
997 A
999 D
1000 A
1001 D
1002 A
1005 D
1006 D
1007 B
1008 D
1015 A
1019 B
1020 C
1023 C
1026 B

1027 C
1034 B
1038 B
1039 C
1041 B
1046 D
1052 C
1057 A
1060 C
1063 A
1068 A
1069 B
1070 C
1071 B
1072 D
1073 B
1076 B
1078 B
1079 D
1080 C
1082 A
1089 C
1091 A
1096 B
1099 A
1101 C
1103 D
1107 B
1118 B
1120 C
1121 D
1122 C
1123 B
1130 A
1132 D
1136 A
1139 DCAB
1147 C
1150 A
1153 A
1156 A
1165 D
1170 D
1175 C
1176 C
1181 B
1183 C
1193 A
1194 D
1200 AB
1205 A
1213 D
1215 B
1216 BCE
1218 B
1223 B
1225 BD
1231 A
1235 B
1238 C
1247 B
1256 CD
1259 DBCA
1262 A
1264 B
1266 ACE
1267 A
1275 C
1279 D
1281 C
1285 C
1292 D
1294 C
1297 C
1312 CBAD
1315 BCAD
1322 B
1343 C
1349 C
1351 D
1352 C
1357 B
1359 CDAB
1360 A
1364 B
1366 A
1369 B
1370 D
1375 D
1379 A
1380 EBADC
1388 AC
1389 D
1395 B
1396 D
1398 BC
1407 C
1409 A
1410 A
1411 C
"""


def import_answers():
    session = db.SessionLocal()

    try:
        answer_map = {}

        # -------------------------------------------------------------
        # 1. 从 CSV 文件中读取 1 - 846 范围内的题号和答案
        # -------------------------------------------------------------
        csv_count = 0
        if os.path.exists(CSV_FILE_PATH):
            print(f"📖 正在读取 CSV 文件: {CSV_FILE_PATH}")
            with open(CSV_FILE_PATH, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    q_num_str = str(row.get("q_num", "")).strip()
                    answer_str = str(row.get("real_answer", "")).strip().upper()

                    # 转成整数校验 1-846 范围
                    if q_num_str.isdigit():
                        q_num_int = int(q_num_str)
                        if 1 <= q_num_int <= 846 and answer_str:
                            answer_map[str(q_num_int)] = answer_str
                            csv_count += 1
            print(f"✅ 从 CSV 中提取到 1-846 范围内的题目答案共 {csv_count} 条")
        else:
            print(f"⚠️ 未找到 CSV 文件: {CSV_FILE_PATH}，将跳过 CSV 导入。")

        # -------------------------------------------------------------
        # 2. 从 ANSWER_DATA 文本中补充 847 - 1417 范围内的答案
        # -------------------------------------------------------------
        text_count = 0
        for line in ANSWER_DATA.strip().splitlines():
            parts = line.strip().split()
            if len(parts) != 2:
                continue

            q_num_str, answer_str = parts
            q_num_str = q_num_str.strip()
            answer_str = answer_str.strip().upper()

            if q_num_str.isdigit():
                q_num_int = int(q_num_str)
                if 847 <= q_num_int <= 1417 and answer_str:
                    answer_map[str(q_num_int)] = answer_str
                    text_count += 1

        print(f"✅ 从文本中提取到 847-1417 范围内的补充答案共 {text_count} 条")
        print(f"📊 准备将总计 {len(answer_map)} 道题目的答案更新至数据库...")
        print("-" * 50)

        # -------------------------------------------------------------
        # 3. 更新至数据库
        # -------------------------------------------------------------
        updated = []
        not_found = []

        for q_num, answer in answer_map.items():
            question = (
                session.query(db.Question)
                .filter_by(q_num=q_num)
                .first()
            )

            if not question:
                not_found.append(q_num)
                continue

            question.real_answer = answer
            updated.append(f"{q_num} -> {answer}")

        session.commit()

        print("\n✅ 正确答案导入完成！")
        print("=" * 50)
        print(f"总处理数量：{len(answer_map)}")
        print(f"成功更新数量：{len(updated)}")
        print(f"数据库未匹配到：{len(not_found)}")

        if not_found:
            print("\n⚠️ 以下题号在数据库 Question 表中没有找到：")
            print(", ".join(not_found))

        print("\n部分更新日志 (前20条)：")
        for item in updated[:20]:
            print(f"  {item}")

        if len(updated) > 20:
            print(f"  ... 其余 {len(updated) - 20} 道题目已更新完成")

    except Exception as e:
        session.rollback()
        print("\n❌ 导入失败：")
        print(str(e))

    finally:
        session.close()


if __name__ == "__main__":
    import_answers()