# Web-Service

### 1. install dependencies

```shell
pip install -r requirements.txt
```

### 2. create database

```shell
python
from project_name import app, db
app.app_context().push()
db.create_all()
```

### 3. run server

```shell
python app.py
```