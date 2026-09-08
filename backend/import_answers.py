import database as db


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
        # 解析题号和答案
        answer_map = {}

        for line in ANSWER_DATA.strip().splitlines():

            parts = line.strip().split()

            if len(parts) != 2:
                continue

            q_num, answer = parts

            q_num = str(q_num).strip()
            answer = str(answer).strip().upper()

            if q_num and answer:
                answer_map[q_num] = answer

        print(f"准备导入 {len(answer_map)} 道题目的正确答案...")
        print("-" * 50)

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

            updated.append(
                f"{q_num} -> {answer}"
            )

        session.commit()

        print()
        print("✅ 正确答案导入完成！")
        print("=" * 50)

        print(f"输入答案数量：{len(answer_map)}")
        print(f"成功更新：{len(updated)}")
        print(f"题库中未找到：{len(not_found)}")

        if not_found:
            print()
            print("⚠️ 以下题号在题库中没有找到：")
            print(", ".join(not_found))

        print()
        print("部分导入结果：")

        for item in updated[:20]:
            print(f"  {item}")

        if len(updated) > 20:
            print(f"  ... 其余 {len(updated) - 20} 道已成功更新")

    except Exception as e:

        session.rollback()

        print()
        print("❌ 导入失败：")
        print(str(e))

    finally:
        session.close()


if __name__ == "__main__":
    import_answers()
