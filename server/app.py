#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.get('/campers')
def get_campers():
    campers = Camper.query.all()
    response = [camper.to_dict(rules=('-signups',)) for camper in campers]
    return jsonify(response), 200

@app.get('/campers/<int:id>')
def get_camper_by_id(id):
    try:
        camper = Camper.query.filter(Camper.id == id).first()
        return jsonify(camper.to_dict()), 200
    except:
        return jsonify({"error": "Camper not found"}), 400

@app.patch('/campers/<int:id>')
def update_camper(id):
    try: 
        data = request.json
        Camper.query.filter(Camper.id == id).update(data)
        camper = Camper.query.filter(Camper.id == id).first()
        db.session.commit()
        return jsonify(camper.to_dict()), 201
    except:
        return jsonify({"error": "Camper not found"}), 404

@app.post('/campers')
def create_camper():
    try:
        data = request.json
        camper = Camper(name=data['name'], age=data['age'])
        db.session.add(camper)
        db.session.commit()
        return jsonify(camper.to_dict()), 201
    except:
        return jsonify({"error": ["validation errors"]}), 404

@app.get('/activities')
def get_activities():
    activities = Activity.query.all()
    response = [activity.to_dict() for activity in activities]
    return jsonify(response), 200

@app.delete('/activities/<int:id>')
def delete_activity(id):
    try: 
        activity = Activity.query.filter(Activity.id == id).first()
        for signups in activity.signups:
            db.session.delete(signups)
        db.session.delete(activity)
        db.session.commit()
        return {}, 204
    except:
        return jsonify({"error": "Activity not found"}), 400

@app.post('/signups')
def create_signup():
    try:
        data = request.json
        camper = Camper.query.filter(Camper.id == data['camper_id']).first()
        activity = Activity.query.filter(Activity.id == data['activity_id']).first()
        signup = Signup(time=data['time'], camper=camper, activity=activity)
        db.session.add(signup)
        db.session.commit()
        print(signup)
        return jsonify(signup.to_dict()), 200
    except:
        return jsonify({"errors": ["validation errors"]})

if __name__ == '__main__':
    app.run(port=5555, debug=True)
