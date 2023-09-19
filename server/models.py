from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    signups = db.relationship("Signup", back_populates="activity")
    camper = association_proxy('signups','camper')
    serialize_rules = ('-signups.activity',)

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)

    signups = db.relationship("Signup", back_populates="camper")
    activity = association_proxy('signups','activity')
    serialize_rules = ('-signups.camper',)
    # Add validation
    @validates('age')
    # age must be between 8 and 18
    def validate_age(self, key, value):
        if value >= 8 and value <= 18:
            return value
        return ValueError("age must be between 8 and 18")
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}, {self.age}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    camper = db.relationship("Camper", back_populates="signups")
    activity = db.relationship("Activity", back_populates="signups")
    serialize_rules = ('-camper.signups', '-activity.signups')
    # Add validation
    @validates('time')
    def validate_time(self, key, value):
        # must have a time between 0 and 23 (referring to the hour of day for the activity)
        if value >= 0 and value <= 23:
            return value
        return ValueError('time must be between 0 and 23')

    def __repr__(self):
        return f'<Signup {self.id}: {self.camper}, {self.activity}, {self.time}>'
