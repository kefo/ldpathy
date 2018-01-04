import sqlite3
from flask import g

class DB:
    _config = {}
    _db = ""
    _app = ""
    
    def __init__(self, app, DBNAME):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DBNAME)
        self._db = db
        self._app = app
        return
        
    def init_db(self, schemaloc):
        with self._app.app_context():
            with self._app.open_resource(schemaloc, mode='r') as f:
                self._db.cursor().executescript(f.read())
            self._db.commit()
            return True
    
    def resources(self):
        sqlquery = "SELECT * FROM resources;"
        call = self._db.execute(sqlquery)
        results = call.fetchall()
        call.close()
        return results if results else None
            
    def query(self, sqlquery, values=()):
        if len(values) > 0:
            call = self._db.execute(sqlquery, values)
        else:
            call = self._db.execute(sqlquery)
        results = call.fetchall()
        call.close()
        return results if results else None
        
    def update(self, sqlquery, values=()):
        call = self._db.cursor()
        if len(values) > 0:
            call.execute(sqlquery, values)
        else:
            call.execute(sqlquery)
        self._db.commit()
        if "DELETE FROM" in sqlquery:
            rows_id = call.rowcount
        else:
            rows_id = call.lastrowid
        call.close()
        return rows_id
    