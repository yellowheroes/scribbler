'''
Created on 04 June 2019

@author: Robert
'''
from models import crud_model

class AdminModel:
            
    def process_content(self, posted_content = ""):   
        # declare variables
        if posted_content != {}:
            content = self.convert(posted_content)  # we need to convert bytes literals dictionary data to string
            
            '''
            Theme select
            '''
            if 'theme' in content:
                theme = content['theme'][0]
                db_table = "admin"
                # prepared statement
                sql = 'UPDATE ' + db_table + ' SET theme = ?'
                # data to inject
                data = (theme,) 
                crud = crud_model.CrudModel()
                row_id = crud.update_record(db_table = db_table, sql = sql, data = data)
            return {'theme': theme}
            
        else:
            return
    
    def to_trashcan(self, article_id = None):
        crud = crud_model.CrudModel() 
        ''' first make a copy of the to-be-deleted article to trashcan '''
        row = crud.select_record(id = article_id)
        #debug
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(row)
        id = row[0][0]
        title = row[0][1]
        content = row[0][2]
        tags = row[0][3]
        created = row[0][4]
        updated = row[0][5]
        deleted = crud.get_date()
        db_table = 'trashcan'
        # prepared statement
        sql = 'INSERT INTO ' + db_table + '(id, title, content, tags, created, updated, deleted) VALUES(?,?,?,?,?,?,?)'
        # data to inject
        data = (id, title, content, tags, created, updated, deleted)
        row_id = crud.insert_record(db_table = 'trashcan', sql = sql, data = data)
        print('copied file to trashcan...')
        
        ''' then delete article from comments database '''
        row = crud.delete_record(id = article_id)
        
        return
        
    def get_theme(self):
        db_table = "admin"
        id = str(1) # table admin only has 1 row
        # prepared statement
        sql = 'SELECT * FROM ' + db_table + ' WHERE id = ' + id
        try:
            crud = crud_model.CrudModel()
            row = crud.select_record(db_table = db_table, sql = sql)
            return row # return the result, e.g.  [(1, 'solar')]
        except:
            print('Status: error retrieving theme')
        
    '''
    We need to convert bytes literals in POST data back to normal 'string' literals.
    Surely, we only need dictionary conversion here, as the POST content is
    a dictionary, but we leave the other type conversions for possible future use
    POST dictionary before conversion: bytes-literals:    {b'content': [b'<p>start</p>']}
    POST dictionary after conversion: string-literals:    {'content': ['<p>start</p>']}
    '''
    def convert(self, data=None):
        if isinstance(data, bytes):      return data.decode()
        if isinstance(data, (str, int)): return str(data)
        if isinstance(data, dict):       return dict(map(self.convert, data.items()))
        if isinstance(data, tuple):      return tuple(map(self.convert, data))
        if isinstance(data, list):       return list(map(self.convert, data))
        if isinstance(data, set):        return set(map(self.convert, data))
        return data

    def list_to_comma_sep_string(self, a_list):
        seperator = ", "
        result = seperator.join(a_list) # turn list it into a comma seperated string
        #debug
        #print('result:', result) # show (in CLI) the result (comma seperated string)
        #print('length :', len(result)) # show length of the string
        return result
    
    """
    https://www.ascii.cl/htmlcodes.htm
    """
    def htmlspecialchars(self, text = ""):
        return(text.replace("'", "&#039;"))
        