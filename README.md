# gunicorn

# Run only werkzeug

```bash
python app.py
```

### Run load test

```bash
./loadtest.sh send_basic_requests 10 1
```

## Run only gunicorn

```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --threads 2 --timeout 120
```