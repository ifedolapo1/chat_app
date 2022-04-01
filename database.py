import sqlite3
from sqlite3 import Error
import datetime


class Database:
    def __init__(self) -> None:
        self.db = sqlite3.connect('database.db')
        self.cur = self.db.cursor()

    def sql_query(self, sql, *params):
        self.cur.execute(sql, params)
        self.cur.commit()

    def insert(self, row):
        self.cur.execute('insert into {} (t1, i1) values (?, ?)'.format(
            self._table), (row['t1'], row['i1']))
        self.cur.commit()

    def retrieve(self, key):
        cursor = self._db.execute(
            'select * from {} where t1 = ?'.format(self._table), (key,))
        return dict(cursor.fetchone())

    def update(self, row):
        self._db.execute(
            'update {} set i1 = ? where t1 = ?'.format(self._table),
            (row['i1'], row['t1']))
        self._db.commit()

    def delete(self, key):
        self._db.execute(
            'delete from {} where t1 = ?'.format(self._table), (key,))
        self._db.commit()

    def __del__(self):
        self.db.close()
