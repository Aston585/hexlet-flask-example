dev-start:
	poetry run flask --app self-working --debug run --port 8000
prod-start:
	poetry run gunicorn --workers=4 --bind=127.0.0.1:8000 self-working:app

