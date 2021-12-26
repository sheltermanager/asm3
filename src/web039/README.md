This is web.py 0.39-20181101

Changes

httpserver.py

Add self.directory = os.getcwd() to the bottom of the StaticApp.\_\_init\_\_ method. 

class StaticApp(SimpleHTTPRequestHandler):
    """WSGI application for serving static files."""
    def __init__(self, environ, start_response):
        self.headers = []
        self.environ = environ
        self.start_response = start_response
        self.directory = os.getcwd()


