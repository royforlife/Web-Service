# Web-Service

### 1. install dependencies

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