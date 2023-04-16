# Web-Service

### 1. install dependencies

install and run postgres

```shell
pip install -r requirements.txt
```

### 2. create database

```shell
python
```

```python
from app import app, db

app.app_context().push()
db.create_all()
```

### 3. run server

```shell
python app.py
```
The server will be running on `http://localhost:3000`

### 4. run tests

```shell
python test_app.py
```

### todo
Good idea for bonus points: implement your answers to the questions in the report :)

Give answer to the following questions (max ½ page per question):
i. Your services will, by default, run on two different ports. Yet,
most microservice architectures are reachable by a single
port. How can you create one entry point for all your
microservices? Describe your approach.
ii. During peak traffic times, any one of your services can easily
be overloaded with traffic. How would you scale up services
independently of each other? Describe your approach.
iii. A microservice architecture means that many web services
can be distributed over several backend servers. How would
you manage a system like this? Think of metrics you might
need (e.g., health, location, …) and how you can collect them.
iv. If you have any technology in mind when answering any of
the question i - iii, please include a (high-level) description
of how your technology answers that question; just
answering “I would use technology X” is not sufficient