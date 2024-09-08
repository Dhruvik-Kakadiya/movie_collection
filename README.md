
# Movie Collection

This is a backend django project for Movie Collection


## Prerequisites

- [Python](https://www.python.org/downloads/) v3.8.0+
- [pip](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-pip) v21.0.0+


## Setup Django Project

Clone the project

_using ssh_

```bash
git clone git@github.com:Dhruvik-Kakadiya/movie_collection.git
```

_or using https_

```bash
git clone https://github.com/Dhruvik-Kakadiya/movie_collection.git
```

Go to the project directory

```bash
cd movie_collection
```

Create a virtual environment

```bash
python3 -m venv ./venv
```

Activate a virtual environment

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Provide Environment variables in project root directory

```bash
cp .env.sample .env
gedit .env
```


## Run using runserver


Run the migrations first

```bash
python manage.py migrate
```

To run the python server

```bash
python manage.py runserver
```

To create your admin user

```bash
python manage.py createsuperuser
```

## Run Tests

To run tests,

```bash
python manage.py test
```