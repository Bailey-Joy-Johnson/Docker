FROM python:3.6-slim-buster
RUN apt-get -y update && apt-get install -y sqlite3 libsqlite3-dev
RUN pip install flask
RUN pip install flask-restful
RUN pip install -U Flask-SQLAlchemy
CMD python app.py
