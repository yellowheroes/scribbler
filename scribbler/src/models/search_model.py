'''
Created on 04 June 2019

@author: Robert
'''
import os
import sys
from datetime import date, datetime
from libs.database import db
from models import crud_model

class SearchModel:
            
    def process_content(self, posted_content = ""):   
        
        if posted_content != {}:
            content = self.convert(posted_content)  # we need to convert bytes literals dictionary data to string
            
            if 'search' in content:
                search_content = content['search'][0]
                print('search_content string in Model before whitespace strip:', search_content)
                #strip any whitespace(s)
                search_content = search_content.replace(" ", "")
                #turn it into a tag list
                tag_list = search_content.split(",")
                '''
                Build a query with the following format e.g.:
                "SELECT * FROM comments WHERE tags LIKE '%sometag%' OR tags LIKE '%someothertag%'"
                
                We cycle through all the tags in the tag_list (user input in the search-box),
                so the sql query captures all of them seperated by OR
                
                We run the sql statement on the column 'tags' (i.e. WHERE tags LIKE... OR tags LIKE)
                in the 'comments' (i.e. FROM comments) database
                '''
                count = 0
                tags = ""
                for tag in tag_list:
                    count += 1
                    if count == 1:
                        tags += "'%" + tag + "%'"
                    else:
                        tags += " OR tags LIKE '%" + tag + "%'"
                '''
                Now use the built query to retrieve the matches in the database
                '''
                sql = "SELECT * FROM comments WHERE tags LIKE " + tags
                crud = crud_model.CrudModel()
                rows = crud.select_all(sql)
                return rows
            else:
                return false
            
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
        