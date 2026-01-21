from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from config import app, db, api, jwt
from models import User, UserSchema, JournalEntry, JournalEntrySchema
from datetime import timedelta
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError


@app.before_request
def check_if_logged_in():
    open_access_list = [
        'signup',
        'login'
    ]

    if (request.endpoint) not in open_access_list and (not verify_jwt_in_request()):
        return {'errors': ['401 Unauthorized']}, 401
    

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'errors': ['Username and password are required.']}, 400

        new_user = User(username=username)
        new_user.password_hash = password

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['Username already exists.']}, 400

        user_schema = UserSchema()
        return user_schema.dump(new_user), 201