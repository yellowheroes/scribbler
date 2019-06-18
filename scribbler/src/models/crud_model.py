import os
import sys
from datetime import date, datetime
from libs.database import db

class CrudModel:
    
    dblite = None               # a DbLite() object
    db_name = "comments.db"
    db_table = "comments"
    conn = None                 # a SQLite database connection handle
    
    def __init__(self):
        self.dblite = db.DbLite()
        self.conn = self.connect_to_database(self.db_name, self.dblite)    
    
    '''
    usage from e.g. app.py:
    crud = crud_model.CrudModel()
    rows = crud.select_all()
    '''
    def select_all(self, sql = "", db_table = None):
        if db_table == None: db_table = self.db_table
        #read all
        if sql == "": sql = 'SELECT * FROM ' + db_table + ' ORDER BY created DESC'
        rows = self.dblite.read(self.conn, sql)
        return rows
    
    '''
    usage from e.g. app.py:
    crud = crud_model.CrudModel()
    row = crud.select_record(id=59)
    '''
    def select_record(self, id = None, db_table = None, sql = None, data = None):
        if db_table == None: db_table = self.db_table
        if sql == None:
            # prepared statement
            sql = 'SELECT * FROM ' + db_table + ' WHERE id = ?'
            # data to inject
            data = (id)
        try:
            row = self.dblite.read(self.conn, sql, id)
        except:
            print('Status: error reading record')
        return row
    
    '''
    usage from e.g. app.py:
    crud = crud_model.CrudModel()

    '''
    def insert_record(self, id = None, title = "", content = "", tags = "", created = "", updated = "", deleted = "", db_table = None, sql = None, data = None):
        if db_table == None: db_table = self.db_table
        if sql == None:
            created = self.get_date()
            updated = ""
            # prepared statement
            sql = 'INSERT INTO ' + db_table + '(title, content, tags, created, updated) VALUES(?,?,?,?,?)'
            # data to inject
            data = (title, content, tags, created, updated)
        try:
            row_id = self.dblite.create(self.conn, sql, data)
            print('Status: successfully saved new article')
            return row_id
        except:
            print('Status: error saving new article')
    
    def update_record(self, id = None, title = "", content = "", tags = "", db_table = None, sql = None, data = None):
        if db_table == None: db_table = self.db_table
        if sql == None:
            updated = self.get_date()
            # prepared statement
            sql = 'UPDATE ' + db_table + ' SET title = ?, content = ?, tags = ?, updated = ? WHERE id = ?'
            # data to inject
            data = (title, content, tags, updated, id)
        try:
            row_id = self.dblite.update(self.conn, sql, data)
            print('Status: successfully updated existing article (id:', id, ')')
            return id
        except:
            print('Error: failed updating existing article')
    
    def delete_record(self, id = None, db_table = None):
        if db_table == None: db_table = self.db_table
        # prepared statement
        sql = 'DELETE FROM ' + db_table + ' WHERE id = ?'
        # data to inject
        data = (id)
        try:
            row_id = self.dblite.delete(self.conn, sql, data)
            print('Status: successfully deleted article (id:', id, ')')
            return row_id
        except:
            print('Error: failed deleting article')
    
    def connect_to_database(self, file_name = "", dblite = None):
        #database = db.DbLite() # use our SQLite-db-transactions Class DbLite
        base_dir = self.base_dir()
        db_name = base_dir + "/libs/database/dbfiles/" + file_name
        try:
            #conn = database.connect(db_name) # connect to existing or create and connect to new db
            conn = dblite.connect(db_name) # connect to existing or create and connect to new db
            print('connected to database ', db_name)
            return conn # return connection handle
        except:
            print('Error: could not connect to database ', db_name)
            return False
        
    '''
    base_directory is the path to \src in our project
    '''
    def base_dir(self):
        pathname = os.path.dirname(sys.argv[0])        
        base_dir = os.path.abspath(pathname)
        return base_dir
    
    def get_date(self):
        now = datetime.now() # e.g. 2019-06-04 15:56:19.545652
        return now