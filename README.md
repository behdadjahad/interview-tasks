# WAREHOUSE MANAGEMENT

for running this project first we need to install the requirements.

``` terminal
pip install -r requirements.txt
```

after installing requirements we neet to make databases.

``` terminal
python manage.py makemigrations
python manage.py migrate
```

now it's ready to run.

``` terminal
python manage.py runserver
```

we can also run the tests with command below.

``` terminal
python manage.py test
```

after running the project we can see all the endpoints in the swagger documentation at the link below:

<http://127.0.0.1:8000/>
