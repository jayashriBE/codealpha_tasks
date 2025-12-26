# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///event_system.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================== MODELS ==================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    location = db.Column(db.String(100))
    organizer = db.Column(db.String(100))


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

# ================== ROUTES ==================

@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.json
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "name": user.name})


@app.route("/api/events", methods=["POST"])
def create_event():
    data = request.json
    event = Event(**data)
    db.session.add(event)
    db.session.commit()
    return jsonify({"id": event.id, "title": event.title})


@app.route("/api/events", methods=["GET"])
def get_events():
    events = Event.query.all()
    return jsonify([
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "date": e.date,
            "location": e.location
        } for e in events
    ])


@app.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    e = Event.query.get(event_id)
    return jsonify({
        "id": e.id,
        "title": e.title,
        "description": e.description,
        "date": e.date,
        "location": e.location
    })


@app.route("/api/registrations", methods=["POST"])
def register_event():
    data = request.json
    reg = Registration(**data)
    db.session.add(reg)
    db.session.commit()
    return jsonify({"id": reg.id})


@app.route("/api/registrations/user/<int:user_id>", methods=["GET"])
def user_registrations(user_id):
    regs = Registration.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            "registration_id": r.id,
            "event_id": r.event_id,
            "registered_at": r.registered_at
        } for r in regs
    ])


@app.route("/api/registrations/<int:reg_id>", methods=["DELETE"])
def cancel_registration(reg_id):
    reg = Registration.query.get(reg_id)
    db.session.delete(reg)
    db.session.commit()
    return jsonify({"message": "Registration cancelled"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)