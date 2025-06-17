FROM python:3.9.22-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["gunicorn", "app:app", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--timeout", "30", \
     "--log-file", "-", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "debug"]