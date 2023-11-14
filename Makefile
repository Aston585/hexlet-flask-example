install:
	poetry install --sync --without dev 
dev-start:
	poetry run flask --app self-working --debug run --port 8000
prod-start:
	poetry run gunicorn --workers=4 self-working:app

