'''
Created on 27 May 2019

@author: Robert
'''

'''
invoke: UrlParse(environ)
instance variables:
script_name = name of currently executing python script
path_info = path up to ?
path = a list of seperate path strings without /'s
query_string = the query string
NOT YET AVAILABLE: params = the key-value pairs of the query string - e.g. ?name=john&age=36

'''
class UrlParse:
    def __init__(self, environ = None):
        self.environ = environ # environ is a dictionary
        #path = environ['PATH_INFO'] 
        #print('path : ' + path)
        #print('path variable type : ', type(path))
        #split_path = path.split('/')
        self.parse()
        
    def parse(self):       
        self.script_name = self.environ.get('SCRIPT_NAME', '') # where are we now
        self.path_info = self.environ['PATH_INFO']
        self.path = self.path_info.split('/') # split path in constituent parts - returns a list of strings
        self.path = list(filter(None, self.path)) # remove empty strings from path and prepend a slash
        if self.environ.get('QUERY_STRING'): 
            self.query_string = self.environ['QUERY_STRING'] # get query string
