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
			charset='utf8mb4',
			use_unicode=True
            #autocommit=False
        )
    except pymysql.MySQLError as e:
        logging.error(f"Database connection error: {e}")
        return None

# Define a simple WSGI application
def app(environ, start_response):
    request = Request(environ)
    method = request.method
    path = request.path

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

        if not conn:
            response = Response("Database connection error", status=500)
            return response(environ, start_response)

        sleep_time = request.args.get('sleep')
        timestamp = request.args.get('timestamp')

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT CONNECTION_ID()")
                connection_id = cursor.fetchone()[0]

                cursor.execute("START TRANSACTION")

                if sleep_time:
                    try:
                        sleep_seconds = float(sleep_time)
                        if sleep_seconds > 0:
                            time.sleep(sleep_seconds)
                    except ValueError:
                        logging.warning(f"[{timestamp}] - Invalid sleep value provided")

                worker_id = os.getpid()
                thread_id = threading.get_ident()

                logging.info(
                    f"DB connection id: {connection_id} | Worker id: {worker_id} | Thread id: {thread_id} | "
                    f"Sleep parameter: {sleep_time} | Timestamp parameter: {timestamp}"
                )

                #cursor.execute("SELECT id, text, author, category, created_at FROM quotation")

                # WARNING: This is an abomination of a query designed to be extremely slow and resource-intensive.
                # Run at your own risk. It will severely impact database performance and can cause timeouts.
                cursor.execute("""
                    SELECT
                        q1.id, q1.text, q1.author, q1.category, q1.created_at
                    FROM quotation q1
                    JOIN quotation q2 ON q1.id <> q2.id
                    JOIN quotation q3 ON q2.id <> q3.id
                    JOIN quotation q4 ON q3.id <> q4.id
                    WHERE
                        (q1.text LIKE '%a%' OR q1.text LIKE '%e%')
                        AND (LOWER(q2.author) LIKE CONCAT('%', LOWER(q3.author), '%') OR LENGTH(q4.text) > 10)
                        AND EXISTS (
                            SELECT 1 FROM quotation q5
                            WHERE q5.category = q1.category
                            AND NOT EXISTS (
                                SELECT 1 FROM quotation q6
                                WHERE q6.author = q5.author
                                AND q6.text LIKE '%z%'
                            )
                        )
                    ORDER BY RAND(), LENGTH(q1.text) + LENGTH(q2.author) DESC
                """)

                rows = cursor.fetchall()

            quotations = []
            for row in rows:
                quotations.append({
                    "id": row[0],
                    "text": row[1],
                    "author": row[2],
                    "category": row[3],
                    "created_at": str(row[4])
                })

            conn.commit()

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