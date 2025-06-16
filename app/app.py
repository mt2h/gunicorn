from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import pymysql
#import threading
import os
import json

def get_connection():
    try:
        return pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', ''),
            password=os.getenv('DB_PASSWORD', ''),
            db=os.getenv('DB_NAME', ''),
            port=int(os.getenv('DB_PORT', '3306')),
            autocommit=False
        )
    except pymysql.MySQLError as e:
        print(f"Database connection error: {e}")
        return None

# Define a simple WSGI application
def app(environ, start_response):
    request = Request(environ)
    method = request.method
    path = request.path

    #pid = os.getpid()
    #thread_id = threading.get_ident()
    #thread_name = threading.current_thread().name
    #print(f"[PID {pid}] [ThreadID {thread_id}] [ThreadName {thread_name}] {method} {path}")

    if path == '/quotation':
        if path == '/':
            if method == 'GET':
                response = Response("Welcome to the home page!", content_type='text/plain')
            else:
                response = Response("Method Not Allowed", status=405)
            return response(environ, start_response)

        elif method != 'GET':
            response = Response("Method Not Allowed", status=405)
            return response(environ, start_response)

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("START TRANSACTION")

                cursor.execute("SELECT id, text, author, category, created_at FROM quotation")
                rows = cursor.fetchall()

            quotations = [
                {
                    "id": row[0],
                    "text": row[1],
                    "author": row[2],
                    "category": row[3],
                    "created_at": str(row[4])
                }
                for row in rows
            ]

            conn.commit()

            response_body = json.dumps(quotations, indent=2)
            response = Response(response_body, content_type='application/json')

        except Exception as e:
            conn.rollback()
            response = Response(f"Error: {str(e)}", status=500)
        finally:
            conn.close()

    else:
        response = Response(f"Path {path} not found", status=404)
        return response(environ, start_response)

    return response(environ, start_response)


def serve(port=5000, profile=False, no_reload=False, no_threading=False, site=None, sites_path='.'):
    print(f"Starting server on port {port}...")
    run_simple(
        hostname='0.0.0.0',
        port=port,
        application=app,
        use_reloader=no_reload,
        use_debugger=profile,
        threaded=not no_threading
    )

if __name__ == '__main__':
    serve(port=5000)