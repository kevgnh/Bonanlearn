import sqlite3

with open("test.html",'r',encoding="utf-8") as dt:
    d=dt.read()

conn=sqlite3.connect("variation.db")
curseur=conn.cursor()
curseur.execute("insert into quiz (page,answer) values(?,?)",(d,2))
conn.commit()
conn.close() 