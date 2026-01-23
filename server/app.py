from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from config import app, db, api, jwt
from models import User, UserSchema, JournalEntry, JournalEntrySchema
from datetime import datetime
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError


@app.before_request
def check_if_logged_in():
    open_access_list = [
        'signup',
        'login',
        'static'
    ]

    if request.endpoint and request.endpoint not in open_access_list:
        try:
            verify_jwt_in_request()
        except:
            return {'errors': ['401 Unauthorized']}, 401
    

class Signup(Resource):
    def post(self):
        data = request.get_json()

        if not data:
            return {'errors': ['Request must contain JSON data.']}, 400
        
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'errors': ['Username and password are required.']}, 400

        new_user = User(username=username)
        new_user.password_hash = password

        try:
            db.session.add(new_user)
            db.session.commit()
            token = create_access_token(identity=new_user.id)
            return make_response(jsonify(token=token, user=UserSchema().dump(new_user)), 201)
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['Username already exists.']}, 422

    
class WhoAmI(Resource):
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.filter(User.id == user_id).first()

        if not user:
            return {'errors': ['User not found.']}, 404
        
        return make_response(jsonify(user=UserSchema().dump(user)), 200)
    
class Login(Resource):
    def post(self):

        data = request.get_json()

        if not data:
            return {'errors': ['Request must contain JSON data.']}, 400
        
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'errors': ['Username and password are required.']}, 400

        user = User.query.filter(User.username == username).first()
        if user and user.authenticate(password):
            token = create_access_token(identity=user.id)
            return make_response(jsonify(token=token, user=UserSchema().dump(user)), 200)
        else:
            return {'errors': ['Invalid username or password']}, 401

class JournalEntryIndex(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        user_id = get_jwt_identity()

        pagination = JournalEntry.query.filter_by(user_id=user_id).paginate(page, per_page, error_out=False)
        journal_entries = pagination.items

        return {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages,
            'journal_entries': [JournalEntrySchema().dump(je) for je in journal_entries]
        }, 200
    
    def post(self):
        request_json = request.get_json()
        if not request_json:
            return {'errors': ['Request must contain JSON data.']}, 400
        
        title = request_json.get('title')
        content = request_json.get('content')
        
        if not title or not content:
            return {'errors': ['Title and content are required.']}, 400
        
        journal_entry = JournalEntry(
            title=title,
            date=request_json.get('date'),
            content=content,
            user_id=get_jwt_identity()
        )
        try:
            db.session.add(journal_entry)
            db.session.commit()
            return JournalEntrySchema().dump(journal_entry), 201
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['Failed to create journal entry.']}, 422

class JournalEntryDetail(Resource):
    def patch(self, journal_entry_id):
        request_json = request.get_json()
        user_id = get_jwt_identity()
        journal_entry = JournalEntry.query.filter_by(id=journal_entry_id, user_id=user_id).first()
        
        if not journal_entry:
            return {'errors': ['Journal entry not found.']}, 404
        if not request_json:
            return {'errors': ['Request must contain JSON data.']}, 400
        
        journal_entry.title = request_json.get('title', journal_entry.title)
        journal_entry.date = request_json.get('date', journal_entry.date)
        journal_entry.content = request_json.get('content', journal_entry.content)

        try:
            db.session.commit()
            return JournalEntrySchema().dump(journal_entry), 200
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['Failed to update journal entry.']}, 422
    
    def delete(self, journal_entry_id):
        user_id = get_jwt_identity()
        journal_entry = JournalEntry.query.filter_by(id=journal_entry_id, user_id=user_id).first()
        if not journal_entry:
            return {'errors': ['Journal entry not found.']}, 404

        try:
            db.session.delete(journal_entry)
            db.session.commit()
            return '', 204
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['Failed to delete journal entry.']}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(WhoAmI, '/me', endpoint='me')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(JournalEntryIndex, '/journal_entries', endpoint='journal_entries')
api.add_resource(JournalEntryDetail, '/journal_entries/<int:journal_entry_id>', endpoint='journal_entry_detail')
if __name__ == '__main__':
    app.run(port=5555, debug=True)