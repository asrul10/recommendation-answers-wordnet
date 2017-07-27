from dbConn.db import Connect
from autoAnswer.nlp import RakeTags

db = Connect().dbOpen()
sql = db.cursor()
rt = RakeTags()

print('Limit default by 10000 data')
offset = input('Enter offset: ')
sql.execute("""SELECT id, score, content, tags FROM question LIMIT %s OFFSET %s""", (10000, int(offset)))
i = 1
count = sql.rowcount
for id, score, content, tags in sql.fetchall():
    print("Progress : %.2f %%" % float(format((float(i)/count)*100)), end = "\r")
    content = content.replace('\n', "")
    sql.execute("UPDATE question SET tags = %s WHERE id = %s", (rt.generate(content), id))
    db.commit()
    i += 1
print('Progress : Complete')