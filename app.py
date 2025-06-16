from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
#import threading
#import os

# Define a simple WSGI application
def app(environ, start_response):
    request = Request(environ)
    method = request.method
    path = request.path

    #pid = os.getpid()
    #thread_id = threading.get_ident()
    #thread_name = threading.current_thread().name
    #print(f"[PID {pid}] [ThreadID {thread_id}] [ThreadName {thread_name}] {method} {path}")

    text = f"Hello! You made a {method} request to {path}"
    response = Response(text, content_type='text/plain')

    return response(environ, start_response)

# Run the server on localhost:5000
if __name__ == '__main__':
    run_simple('localhost', 5000, app)