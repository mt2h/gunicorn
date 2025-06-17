from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import pymysql
import os
import json
import time
import logging
import threading

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s +0000] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

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
        logging.error(f"Database connection error: {e}")
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

    if path == '/':
        if method == 'GET':
            response = Response("Welcome to the home page!", content_type='text/plain')
        else:
            response = Response("Method Not Allowed", status=405)
        return response(environ, start_response)

    elif path == '/quotation':

        if method != 'GET':
            response = Response("Method Not Allowed", status=405)
            return response(environ, start_response)

        conn = get_connection()

        sleep_time = request.args.get('sleep')
        timestamp = request.args.get('timestamp')

        if not conn:
            response = Response("Database connection error", status=500)
            return response(environ, start_response)

        if sleep_time:
            try:
                sleep_seconds = float(sleep_time)
                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)
            except ValueError:
                logging.warning(f"[{timestamp}] - Invalid sleep value provided")

        try:
            with conn.cursor() as cursor:
                cursor.execute("START TRANSACTION")

                cursor.execute("SELECT CONNECTION_ID()")
                connection_id = cursor.fetchone()[0]

                worker_id = os.getpid()
                thread_id = threading.get_ident()

                logging.info(
                    f"DB connection id: {connection_id} | Worker id: {worker_id} | Thread id: {thread_id} | "
                    f"Sleep parameter: {sleep_time} | Timestamp parameter: {timestamp}"
                )

                cursor.execute("SELECT id, text, author, category, created_at FROM quotation")
                rows = cursor.fetchall()

            conn.commit()

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

            response_body = json.dumps(quotations, indent=2)
            response = Response(response_body, content_type='application/json')

        except Exception as e:
            conn.rollback()
            logging.exception("Error during /quotation request")
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