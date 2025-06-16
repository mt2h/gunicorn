from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

# Define a simple WSGI application
def application(environ, start_response):
    request = Request(environ)
    text = f"Hello! You made a {request.method} request to {request.path}"
    response = Response(text, content_type='text/plain')
    return response(environ, start_response)

# Run the server on localhost:5000
if __name__ == '__main__':
    run_simple('localhost', 5000, application)