from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from socket_instance import socketio
from db import db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio.init_app(app, cors_allowed_origins="*")
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:ZaSvzITGYvRgQajMXiRSAgTVmEgyZhzq@junction.proxy.rlwy.net:45906/railway'
db.init_app(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this in production
jwt = JWTManager(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "name": self.name
        }

class CreateUser(Resource):
    def post(self):
        data = request.get_json()
        new_user = Users(**data)
        db.session.add(new_user)
        db.session.commit()
        # Return response as a proper JSON response
        return {"message": "user created", "user": new_user.serialize()}, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        user = Users.query.filter_by(username=username).first()
        return {"message": "connected"}, 200

class Home(Resource):
    def get(self):
        # Return JSON-compatible dictionary
        return {"message": "connected"}, 200
    

@socketio.on('message')
def handle_message(data):
    print('received message: ' , data)
    socketio.emit('server_message', data)



with app.app_context():
    db.create_all()

api.add_resource(CreateUser, '/create_user')
api.add_resource(Login, '/login')
api.add_resource(Home, '/')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)