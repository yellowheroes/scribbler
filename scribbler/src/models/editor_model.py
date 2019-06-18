'''
Created on 04 June 2019

@author: Robert
'''
import os
import sys
from datetime import date, datetime
import re
from libs.database import db
from models import crud_model

class EditorModel:
            
    def process_content(self, article_id = None, posted_content = ""):   
        # declare variables
        article_title = ""
        article_content = ""
        tags = ""
        
        if posted_content != {}:
            content = self.convert(posted_content)  # we need to convert bytes literals dictionary data to string
            
            '''
            Save new article
            '''
            if article_id == None:
                if 'content' in content:
                    article_content = content['content'][0]
                    article_content = self.htmlspecialchars(article_content) # important, foremost for "'" in article_content, as these warp editor.value = '{{tbody}}'; as it already uses enclosing ' '
                    article_content = " ".join(article_content.split()) # remove all whitespaces, newline characters
                if 'title' in content:
                    article_title = content['title'][0]
                else:
                    article_title = "No Title"
                if 'tags[]' in content:
                    tags = self.list_to_comma_sep_string(content['tags[]'])             
                
                crud = crud_model.CrudModel()
                row_id = crud.insert_record(title = article_title, content = article_content, tags = tags)
                return ['new', row_id]
            
            else:
                '''
                Save existing article: update (use existing article 'id')
                '''
                if 'content' in content:
                    article_content = content['content'][0]
                    article_content = self.htmlspecialchars(article_content) # important, foremost for "'" in article_content, as these warp editor.value = '{{tbody}}'; as it already uses enclosing ' ' 
                    article_content = " ".join(article_content.split()) # remove all whitespaces, newline characters
                if 'title' in content:
                    article_title = content['title'][0]
                else:
                    article_title = "No Title"
                if 'tags[]' in content:
                    tags = self.list_to_comma_sep_string(content['tags[]'])             
                
                crud = crud_model.CrudModel()
                row_id = crud.update_record(id = article_id, title = article_title, content = article_content, tags = tags)
                return ['existing', row_id]
        else:
            return
        
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
        