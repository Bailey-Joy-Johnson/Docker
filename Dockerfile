FROM python:3.6-slim-buster
RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false -y update && apt-get install -y sqlite3 libsqlite3-dev
RUN pip install flask
RUN pip install flask-restful
RUN pip install -U Flask-SQLAlchemy
RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN python -m spacy download en_core_web_sm
RUN pip install ner
RUN pip install beautifulsoup4
#WORKDIR /app
COPY test/ ./test/
CMD python test/app.py
