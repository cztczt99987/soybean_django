# 临时脚本: 检查 db.sqlite3 内容, 用完即删
import sqlite3

con = sqlite3.connect("db.sqlite3")
cur = con.cursor()
tables = sorted(
    r[0] for r in cur.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")
)
print(f"共 {len(tables)} 张表")
for t in tables:
    try:
        cnt = cur.execute(f'select count(*) from "{t}"').fetchone()[0]
        print(f"  {t}: {cnt} 行")
    except Exception as e:
        print(f"  {t}: 读取失败 {e}")
