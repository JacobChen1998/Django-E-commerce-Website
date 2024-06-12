rm db.sqlite3
rm -rf shop/migrations
mkdir shop/migrations
touch shop/migrations/__init__.py
python manage.py makemigrations shop
python manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'jinyor8736@gmail.com', '1qaz!QAZ')" | python manage.py shell
