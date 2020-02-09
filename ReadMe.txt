copy lifeline/.env.example to lifeline/.env and update settings
run:
  docker-compose build
  docker-compose up
  docker-compose exec web python manage.py migrate

After you did all described steps you can use folow: http://localhost:8000 to login into admin area.
NOTE: refer to apps/accounts/migrations/0002_createsuperuser.py for initial SuperUser login/password.