'''
Created on 23 May 2019

@author: Robert
'''
#from wsgiref.simple_server import make_server

import sys
import os
import pprint
import cherrypy
from urllib.parse import parse_qs
from jinja2 import Template
from bs4 import BeautifulSoup
from libs import parseurl
from libs.database import db
from models import editor_model
from models import admin_model
from models import search_model
from models import crud_model

class App:
    
    def __call__(self, environ, start_response):
        '''
        New Request
        '''
        print('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
        print('new request')
        print('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
        
        #debug environ
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(environ)
        
        
        #declare / initialize variables
        app_name = "| Scribbler |"
        
        redirect = False
        status = ""
        response_headers = []
        response_body = bytes("", encoding='utf-8')  # response_body must be a bytes literal
        
        home_html = ""
        editor_html = ""
        comments_html = ""
        read_html = ""
        search_html = ""
        admin_html = ""
        content = ""
        html = ""
        title = ""
        body = ""
        tags = ""
        requested_view = ""
        
        '''
        get theme from db
        '''
        print('getting theme...')
        m_admin = admin_model.AdminModel()
        row = m_admin.get_theme()
        theme = row[0][1]
        
        
        ''' get base dir '''        
        pathname = os.path.dirname(sys.argv[0])        
        base_directory = os.path.abspath(pathname)  # e.g. D:\pydev\scribbler\src
        
        '''
        parse the request
        '''
        views = self.get_views()  # retrieve available views
        request = str(environ['PATH_INFO'])
        requested_view = "/" + request.split('/')[1]
        params = request.split('/')[2:]
        article_id = None
        try:
            article_id = params[0] # is an article id present?
        except:
           pass
        
        #debug
        print("user requested view :", requested_view)
        print('params :', params)
        print('article-id :', article_id)
        
        '''
        Requested view exists - invoke the correct view logic and render view
        '''
        if requested_view in views:
            if requested_view == "/shutdown":
                self.shut_down_server()
            if requested_view == "/": requested_view = "/home"
            
            '''
            View-page: /search
            '''
            if requested_view == '/search':
                
                search_content = self.get_search_content(environ)
                if search_content != {}:
                    content = self.convert(search_content)  # we need to convert bytes literals dictionary data to string
                    if 'search' in content and content['search'][0] != "":
                        print('content search 0 :', content['search'][0])
                        ''' process the search in SearchModel '''
                        m_search = search_model.SearchModel()
                        ''' all matches are returned by process_content() - we store them in 'rows' here '''
                        rows = m_search.process_content(search_content)
                        noa = len(rows) # number of articles
                        
                        ''' enable quick html build '''
                        bs_container_open = '''<div class='row'><div class='col'><hr />'''
                        bs_block_open = '''<div class='row'><div class='col'>'''
                        bs_block_close = '''</div></div>'''
                        bs_container_close = '''</div></div>'''
                        
                        content = ""
                        ''' header '''
                        content += bs_container_open
                        content += bs_block_open
                        content += "<h1 class='text-center'>Your Search Result</h1>"
                        content += bs_block_close
                        content += bs_container_close
                        
                        count = 0
                        ''' rows contains all the articles that matched the search (based on tags)'''
                        for row in rows:
                            count += 1
                            article_ratio = str(count) + "/" + str(noa) # to show 1/5, 2/5, 3/5 etc. with each article in the list
                            id = str(row[0])
                            title = row[1]
                            htmltotext = BeautifulSoup(row[2], features="html.parser")
                            article_body_content = htmltotext.get_text()
                            teaser = article_body_content.split()[:15] # show only first 15 words as teaser
                            teaser = " ".join(teaser) # turn list into string, each word seperated by " "
                            create_date = row[4][:10] # only date, not time
                            update_date = row[5][:10] # only date, not time
                            ''' create list with all available articles '''
                            content += bs_container_open
                            content += bs_block_open
                            content += "<h1><a href = '/read/" + id + "'>" + title + "</a></h1>"
                            content += "<div class='row'>"
                            content += "<div class='col-3 text-left'>created: " + create_date + "</div>" + "<div class='col-9 text-right'>" + article_ratio + "</div>"
                            content += "</div>"
                            if update_date != "": content += "<div style='font-size: 0.8em; font-style: italic;'>(updated: " + update_date + ")</div>"
                            content += bs_block_close
                            content += bs_block_open
                            content += "<div style='font-size: 1em; font-style: italic;'><br />" + teaser + "..." + "</div>" 
                            content += bs_block_close
                            content += bs_block_open
                            content += "<p class='text-right'>"
                            content += "<a href = '/read/" + id + "'>" + "read" + "</a>"
                            content += "<span style='margin-left: 20px;'><!-- dummy space --></span><a href = '/editor/" + id + "'>" + "edit" + "</a>"
                            content += "<span style='margin-left: 20px;'><!-- dummy space --></span><a href = '/delete/" + id + "'>" + "delete" + "</a></p>"
                            content += bs_block_close
                            content += bs_container_close
                
                        search_html = self.get_search_html(base_directory, "/views/search.html", content) # put article-search-hits-list html into variable 'search_html'
            
                        
                    else:
                        print('no search terms found')
            
            '''
            View-page: /home
            '''
            if requested_view == '/home':
                bs_container_open = '''<div class='row'><div class='col'><hr />'''
                bs_block_open = '''<div class='row'><div class='col'>'''
                bs_block_close = '''</div></div>'''
                bs_container_close = '''</div></div>'''
                msg = "A lightweight 'typewriter' for heavyweigth scribes"
                content = ""    
                content += bs_container_open
                content += bs_block_open
                content += "<h1>Scribbler</h1>"
                content += bs_block_close
                content += bs_block_open
                content += "<div style='font-size: 1em; font-style: italic;'><br />" + msg + "</div>" 
                content += bs_block_close
                content += bs_container_close
                
                home_html = self.get_home_html(base_directory, "/views/home.html", content) # put article-list html into variable 'comments_html'
            
            '''
            View-page: /comments
            '''
            if requested_view == '/comments':
                crud = crud_model.CrudModel()
                rows = crud.select_all()
                noa = len(rows) # number of articles
                bs_container_open = '''<div class='row'><div class='col'><hr />'''
                bs_block_open = '''<div class='row'><div class='col'>'''
                bs_block_close = '''</div></div>'''
                bs_container_close = '''</div></div>'''
                
                content = ""
                ''' header '''
                content += bs_container_open
                content += bs_block_open
                content += "<h1 class='text-center'>Your Article Repository</h1>"
                content += bs_block_close
                content += bs_container_close
                
                count = 0
                id = None
                for row in rows:
                    count += 1
                    article_ratio = str(count) + "/" + str(noa) # to show 1/5, 2/5, 3/5 etc. with each article in the list
                    id = str(row[0])
                    title = row[1]
                    #extract = row[2].split()[:10] # first 30 words
                    htmltotext = BeautifulSoup(row[2], features="html.parser")
                    article_body_content = htmltotext.get_text()
                    teaser = article_body_content.split()[:15] # show only first 15 words as teaser
                    teaser = " ".join(teaser) # turn list into string, each word seperated by " "
                    create_date = row[4][:10] # only date, not time
                    update_date = row[5][:10] # only date, not time
                    ''' create list with all available articles '''
                    content += bs_container_open
                    content += bs_block_open
                    content += "<h1><a href = '/read/" + id + "'>" + title + "</a></h1>"
                    content += "<div class='row'>"
                    content += "<div class='col-3 text-left'>created: " + create_date + "</div>" + "<div class='col-9 text-right'>" + article_ratio + "</div>"
                    content += "</div>"
                    if update_date != "": content += "<div style='font-size: 0.8em; font-style: italic;'>(updated: " + update_date + ")</div>"
                    content += bs_block_close
                    content += bs_block_open
                    content += "<div style='font-size: 1em; font-style: italic;'><br />" + teaser + "..." + "</div>" 
                    content += bs_block_close
                    content += bs_block_open
                    content += "<p class='text-right'>"
                    content += "<a href = '/read/" + id + "'>" + "read" + "</a>"
                    content += "<span style='margin-left: 20px;'><!-- dummy space --></span><a href = '/editor/" + id + "'>" + "edit" + "</a>"
                    content += "<span style='margin-left: 20px;'><!-- dummy space --></span><a href = '/delete/" + id + "'>" + "delete" + "</a></p>"
                    content += bs_block_close
                    content += bs_container_close
                
                comments_html = self.get_comments_html(base_directory, "/views/comments.html", content) # put article-list html into variable 'comments_html'
            
            '''
            View-page: /editor
            '''
            if requested_view == '/editor':
                title = body = ""
                tags = []
                ''' if existing article, inject editor with existing content, and set existing title and tag-list in form fields '''
                if article_id != None:
                    crud = crud_model.CrudModel()
                    row = crud.select_record(id=article_id)
                    title = row[0][1] # element 1 is the article title
                    body = str(row[0][2]) # element 2 is the article body html content
                    tags = row[0][3].split(", ") # element 3 is the tags - turn it into a list: from string 'us, new york, big apple' to ['us', 'new york', 'big apple']
                    if tags == []: tags = [""] # this is necessary format for tagsManager({ prefilled: }) - see file 'editor.html'
                
                ''' if new article, open editor with empty body, no title, and empty tag-list '''
                if tags == []: tags = [""] # this is necessary format for tagsManager({ prefilled: }) - see file 'editor.html'
                
                editor_html = self.get_editor_html(base_directory, "/views/editor.html", title, body, tags) # put editor html into variable 'editor'
                
                posted_content = self.get_editor_content(environ)
                if posted_content != {}:
                    ''' use EditorModel to process and save new(create) or existing(update) article '''
                    m_editor = editor_model.EditorModel()
                    ''' 
                    @return ['new', row_id] for newly created and saved article
                            ['existing', row_id] for update of existing article
                    '''
                    type_id = m_editor.process_content(article_id, posted_content)
                    type = type_id[0]
                    id = type_id[1]
                    print('type:', type, " id:", id)
            
            '''
            View-page: /read
            '''       
            if requested_view == '/read':
                crud = crud_model.CrudModel()
                row = crud.select_record(id=article_id)
                bs_container_open = '''<div class='row'><div class='col'>'''
                bs_block_open = '''<div class='row'><div class='col'>'''
                bs_block_close = '''</div></div>'''
                bs_container_close = '''</div></div>'''
                bs_dummy_space = '''<span style='margin-left: 20px;'><!-- dummy space --></span>'''
                bs_hr = "<hr />"
                content = ""
                id = str(row[0][0])
                title = row[0][1]
                body = row[0][2]
                ''' show article for reading '''
                content += bs_container_open
                content += bs_block_open
                content += "<p class='text-right'><a href = '/editor/" + id + "'>" + "edit" + "</a>"
                content += bs_dummy_space + "<a href = '/delete/" + id + "'>" + "delete" + "</a></p>"
                content += bs_block_close
                
                content += bs_block_open
                content += bs_hr
                content += "<h1 class='text-center'>" + title + "</h1><br />"
                content += bs_block_close
                
                content += bs_block_open
                content += body # article body html
                content += bs_hr
                content += bs_block_close
                content += bs_block_open
                content += "<p class='text-right'><a href = '/editor/" + id + "'>" + "edit" + "</a>"
                content += "<span style='margin-left: 20px;'><!-- dummy space --></span><a href = '/delete/" + id + "'>" + "delete" + "</a></p>"
                content += bs_block_close
                content += bs_container_close
            
                read_html = self.get_read_html(base_directory, "/views/read.html", content) # put article html into variable 'read_html'
            
            '''
            View-page: /delete
            '''       
            if requested_view == '/delete':
                m_admin = admin_model.AdminModel()
                m_admin.to_trashcan(article_id)
                
                #crud = crud_model.CrudModel()
                
                ''' first make a copy to trashcan '''
                #row = crud.select_record(id = article_id)
                #debug
                #pp = pprint.PrettyPrinter(indent=4)
                #pp.pprint(row)
                
                #id = row[0][0]
                #title = row[0][1]
                #content = row[0][2]
                #tags = row[0][3]
                #created = row[0][4]
                #updated = row[0][5]
                #deleted = crud.get_date()
                #db_table = 'trashcan'
                # prepared statement
                #sql = 'INSERT INTO ' + db_table + '(id, title, content, tags, created, updated, deleted) VALUES(?,?,?,?,?,?,?)'
                # data to inject
                #data = (id, title, content, tags, created, updated, deleted)
                #row_id = crud.insert_record(db_table = 'trashcan', sql = sql, data = data)
                #print('copied file to trashcan...')
                
                ''' then delete article from comments database '''
                #row = crud.delete_record(id = article_id)
                #status = "308 Permanent Redirect"
                status = "302 Found"
                redirect = True # we activate redirection
                redirect_target = '/comments' # and set the page we want to serve
                
            '''
            View-page: /admin
            '''       
            if requested_view == '/admin':

                posted_content = self.get_admin_post(environ)
                if posted_content != {}:
                    ''' use AdminModel to process POSTed data: e.g. user SET a new theme '''
                    m_admin = admin_model.AdminModel()
                    result = m_admin.process_content(posted_content)
                   
                    if result['theme']:
                        theme = result['theme']
                        
                selected_theme_html = "<option value = " + theme + " selected>" + theme + "</option>"
                content = {'selected_theme': selected_theme_html}
                admin_html = self.get_admin_html(base_directory, "/views/admin.html", content) # put admin html into variable 'admin_html'
                    
            
            ''' 
            Use Jinja2 Template object to inject params into templates
            1. view-page '/comments' template is already injected with all articles available in database,
            param 'comments_html' holds a list of links to all articles. User can select 'edit', 'read', or 'delete'
            2. view-page '/editor' template is already injected with article 'title', 'body'(in editor) and 'tags' if available,
            so when user selects article to update, the existing content is rendered in editor, and title and tags are displayed as well.
            '''
            
            ''' pull-in our main templates '''
            html = self.read_file(base_directory, "/views/header.html")
            html += self.read_file(base_directory, "/views/body.html")
            html += self.read_file(base_directory, "/views/footer.html")
            
            breadcrumb = requested_view[1:] # cut the first char from string ('/') - do not show '/' in breadcrumb
            if requested_view != "/admin":
                bstrap_container = "container"
            else:
                bstrap_container = "container-fluid" # we want to use full-screen for admin area
                
            template = Template(html) # Jinja2 Template object, give it the html content with placeholders that needs to be injected with values
            
            ''' set active button color in navigation menu '''
            active_home = active_comments = active_editor = active_admin = ""
            if requested_view == '/home': active_home = "style='color: white;'"
            if requested_view == '/comments': active_comments = "style='color: white;'"
            if requested_view == '/editor': active_editor = "style='color: white;'"
            if requested_view == '/admin': active_admin = "style='color: white;'"
            
            ''' inject template placeholders with values'''
            html = template.render(tapp_name=app_name, tbootswatch_theme=theme, tview=breadcrumb, tcontainer = bstrap_container,
                                   tactive_home = active_home, tactive_comments = active_comments,
                                   tactive_editor = active_editor, tactive_admin = active_admin,
                                   thome = home_html, teditor=editor_html, tcomments = comments_html,
                                   tread = read_html, tsearch = search_html, tadmin = admin_html)
            
            '''
            Send response: return status, headers and view-page html (response_body)
            '''
            # https://docs.python.org/3/library/stdtypes.html#bytes
            response_body = bytes(html, encoding='utf-8')  # response_body must be a bytes literal
            if status == "":
                status = '200 OK'
            if redirect == False:
                response_headers = [
                            ('Content-Type','text/html'),
                            ('Content-Length', str(len(response_body)))
                            ]
            else: # do redirect
                response_headers = [
                            ('Content-Type','text/html'),
                            ('Content-Length', str(len(response_body))),
                            ('Location', redirect_target)
                            ]
            start_response(status, response_headers)
            return [response_body] # response_body must be a bytes literal
            
            
            '''
            Requested view does not exist: 404
            '''
        else:
            theme = theme[0]  # select a bootswatch theme
            html = self.read_file(base_directory, "/views/header.html")
            html += self.read_file(base_directory, "/views/pagenotfound.html")
            html += self.read_file(base_directory, "/views/footer.html")
            # breadcrumbs show user which view-page she's on            
            breadcrumb = requested_view[1:] # cut the first char from string ('/') - do not show '/' in breadcrumb
            theme = theme[0]  # select a bootswatch theme
            template = Template(html) # Jinja2 Template
            html = template.render(tapp_name=app_name, tbootswatch_theme=theme, tview=breadcrumb)
            response_body = bytes(html, encoding='utf-8')
            status = '404 NOT FOUND'
            response_headers = [
                       ('Content-Type', 'text/html'),
                        ('Content-Length', str(len(response_body)))
                       ]
            start_response(status, response_headers)
            return [response_body]
        
    def read_file(self, path="", filename=""):
        file = path + filename
        try:
            file_contents = open(file).read()  # read the template file contents (html with placeholders)
            return file_contents
        except IOError:
            print ("Error: We encountered a problem reading file ", filename)
            sys.exit
    
    def get_views(self):
        views = ["/", "/home", "/editor", "/comments", "/read", "/delete", "/search", "/admin", "/shutdown"] # list of available views
        return views
    
    def get_home_html(self, path="", filename="/views/home.html", content = ""):
        home_html = self.read_file(path, filename)
        ''' use Jinja2 Template object to inject params into template editor '''
        template = Template(home_html)
        ''' here we can inject existing article content'''
        home_html = template.render(tcontent=content)
        return home_html
    
    def get_editor_html(self, path="", filename="/views/editor.html", title = "", body = "", tags = ""):
        editor_html = self.read_file(path, filename)
        ''' use Jinja2 Template object to inject params into template editor '''
        template = Template(editor_html)
        ''' here we can inject existing article content'''
        editor_html = template.render(ttitle = title, tbody = body, ttags = tags)
        return editor_html
    
    def get_comments_html(self, path="", filename="/views/comments.html", content = ""):
        comments_html = self.read_file(path, filename)
        ''' use Jinja2 Template object to inject params into template editor '''
        template = Template(comments_html)
        ''' here we can inject existing article content'''
        comments_html = template.render(tcontent=content)
        return comments_html
    
    def get_admin_html(self, path="", filename="/views/admin.html", content = ""):
        admin_html = self.read_file(path, filename)
        ''' use Jinja2 Template object to inject params into template editor '''
        template = Template(admin_html)
        ''' inject selected theme'''
        admin_html = template.render(tselected = content['selected_theme'])
        return admin_html
    
    def get_search_html(self, path="", filename="/views/search.html", content = ""):
        search_html = self.read_file(path, filename)
        ''' use Jinja2 Template object to inject params into template editor '''
        template = Template(search_html)
        ''' here we can inject existing article content'''
        search_html = template.render(tcontent=content)
        return search_html
    
    def get_read_html(self, path="", filename="/views/read.html", content = ""):
        read_html = self.read_file(path, filename)
        ''' use Jinja2 Template object to inject params into template editor '''
        template = Template(read_html)
        ''' here we can inject existing article content'''
        read_html = template.render(tcontent=content)
        return read_html
    
    def get_editor_content(self, environ):
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            posted_content = parse_qs(request_body)
            return posted_content
        except (ValueError):
            request_body_size = 0
            return False # nothing was POSTed
        
    def get_search_content(self, environ):
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            posted_content = parse_qs(request_body)
            return posted_content
        except (ValueError):
            print('value error encountered')
            request_body_size = 0
            return False # nothing was POSTed
    
    def get_admin_post(self, environ):
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            posted_content = parse_qs(request_body)
            return posted_content
        except (ValueError):
            print('value error encountered')
            request_body_size = 0
            return False # nothing was POSTed
        
    def bstrap_alert(self, msg = "", dismiss = False):
        dismiss1 = dismiss0 = ""
        if dismiss == True:
            dismiss0 = "alert-dismissible"
            dismiss1 = """<button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
            """
        html = """
        <div class="alert alert-secondary {tdismiss0} fade show" role="alert">
          <h2><p>{tmsg}</p></h2>
          {tdismiss1}
        </div>
        """.format(tmsg = msg, tdismiss0 = dismiss0, tdismiss1 = dismiss1)
        return html
    
    def list_to_comma_sep_string(self, a_list):
        seperator = ", "
        result = seperator.join(a_list) # turn list it into a comma seperated string
        #debug
        #print('result:', result) # show (in CLI) the result (comma seperated string)
        #print('length :', len(result)) # show length of the string
        return result
    
    '''
    We need to convert bytes literals in POST back to normal 'string' literals.
    Surely, we only need dictionary conversion here, as the POST content is
    a dictionary, but we leave the other type conversions for possible
    future use
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
    
    '''
    shut down Cherry Py server
    '''
    def shut_down_server(self):
        cherrypy.engine.exit()

'''
We feed cherrypy_server with a 'callable' class App object
'''
app = App()
if __name__ == '__main__':
    cherrypy.tree.graft(app, '/') # use tree.graft to host a foreign app with CherryPy server
    
    '''
    app config, so cherrypy-server will serve all static files in folder static and any sub-folders
    os.path.abspath(os.path.dirname(__file__))) === d:\pydev\scribbler\src
    ''' 
    static_files = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
            'tools.staticdir.on': True,
            'log.screen': False,
            'tools.staticdir.dir': 'static'
        }}
    '''
    cherrypy.config.update is used for global config settings,
    cherrypy.tree.mount is used for per-app config settings.
    '''
    cherrypy.tree.mount(app, '/static', config=static_files) # use tree.mount to set config settings per application
    cherrypy.engine.start()
    cherrypy.engine.block()