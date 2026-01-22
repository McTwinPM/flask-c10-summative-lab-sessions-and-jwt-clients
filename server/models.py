from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, String, Boolean
from marshmallow import Schema, fields, validates_schema, ValidationError
from datetime import datetime
from config import db, bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)

    journal_entries = db.relationship('JournalEntry', back_populates='user', lazy=True)

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash may not be read.")
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self._password_hash = password_hash
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
    
    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    id = db.Column(Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.String, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='journal_entries', lazy=True)
    

    def __repr__(self):
        return f"<JournalEntry id={self.id} title={self.title} date={self.date} content={self.content}>"
    
class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str(required=True)
    journal_entries = fields.List(fields.Nested(lambda: JournalEntrySchema(exclude=('user_id',))))

class JournalEntrySchema(Schema):
    id = fields.Int()
    title = fields.Str(required=True)
    date = fields.DateTime(required=True)
    content = fields.Str(required=True)

    user = fields.Nested(UserSchema, only=('journal_entries',))
