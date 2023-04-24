# create a docker file for auth service
FROM python:3-alpine
LABEL authors="xyh"


RUN pip install flask flask_sqlalchemy sqlalchemy_utils gunicorn psycopg2-binary

COPY . /usr/src/app/
WORKDIR /usr/src/app/

EXPOSE 3000
#ENTRYPOINT ["/usr/local/bin/gunicorn"]

# url shortener app server
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]
