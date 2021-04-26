#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""app.py
Simple Web interface and API to spaCy entity recognition.
Usage via the API (on the local host):
$> curl http://127.0.0.1:5000/api
$> curl -H "Content-Type: text/plain" -X POST -d@input.txt http://127.0.0.1:5000/api
For the web pages point your browser at http://127.0.0.1:5000
"""


from flask import Flask, request, render_template
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

import ner
from bs4 import BeautifulSoup

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'fc3bb2a43ff1103895a4ee315ee27740'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_users.entity'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.create_all()


# For the website we use the regular Flask functionality and serve up HTML pages.

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('form.html', input=open('input.txt', encoding="utf8").read())
    else:
        text = request.form['text']
        markup = ner.entity_markup(text)
        soup = BeautifulSoup(markup, features="html.parser")
        entity_names = [ent.text for ent in soup.find_all('entity')]
        for i in entity_names:
            exists = db.session.query(Entity).filter_by(entity=i).first() is not None
            if exists:
                update(i)
            else:
                add_entity(i)
        markup_paragraphed = ''
        for line in markup.split('\n'):
            if line.strip() == '':
                markup_paragraphed += '<p/>\n'
            else:
                markup_paragraphed += line
        return render_template('result.html', markup=markup_paragraphed)
    
def add_entity(entity):
   entity = Entity(entity=entity, counter=1)
   db.session.add(entity)
   db.session.commit()
   return f'{entity}\n'

def update(entity):
    updated = Entity.query.filter_by(entity=entity)
    #Entity.update().where(Entity.c.entity == entity).values(counter=counter+1)
    updated.counter = Entity.counter + 1
    #updated.update(dict(counter=c))
    db.session.commit()

# But for the API we use the RESTful extension and return JSON.

class EntityParserAPI(Resource):

    def get(self):
        content = "Content-Type: text/plain"
        url = 'http://127.0.0.1:5000/api'
        return \
            {"description": "Interface to the spaCy entity extractor",
             "usage": 'curl -v -H "%s" -X POST -d@input.txt %s' % (content, url)}

    def post(self):
        text = str(request.get_data(as_text=True))
        markup = ner.entity_markup(text)
        soup = BeautifulSoup(markup, features="html.parser")
        entity_names = [ent.text for ent in soup.find_all('entity')]
        for i in entity_names:
            exists = db.session.query(Entity).filter_by(entity=i).first() is not None
            if exists:
                update(i)
            else:
                add_entity(i)
        return {"input": text,
                "output": entity_names}, 201
    
class Entity(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   entity = db.Column(db.String(80), unique=True, nullable=False)
   counter = db.Column(db.Integer, unique=False, nullable=False, default=1)

   def __repr__(self):
       return '<Entity %r %r>' % (self.entity, self.counter)


class DatabaseAPI(Resource):

    def get(self):
        content = "Content-Type: text/plain"
        url = 'http://127.0.0.1:5000/database'
        return \
            {"description": "Interface to the database",
             "usage": 'curl -v -H "%s" -X POST -d@input.txt %s' % (content, url)}

    def post(self):
        return f'{Entity.query.all()}\n'
        #return render_template('database.html', data=)

api.add_resource(EntityParserAPI, "/api")
api.add_resource(DatabaseAPI, "/database")

if __name__ == '__main__':

    app.run(debug=True)