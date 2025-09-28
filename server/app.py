#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize DB and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Flask-Restful
api = Api(app)


# --------------------------
# Session Management
# --------------------------
class ClearSession(Resource):
    def delete(self):
        session.pop('page_views', None)
        session.pop('user_id', None)
        return {}, 204


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')

        if not username:
            return {'message': 'Username required'}, 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return {'message': 'User not found'}, 404

        session['user_id'] = user.id
        return jsonify(user.to_dict())


class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {}, 401

        user = User.query.get(user_id)
        if not user:
            return {}, 401

        return jsonify(user.to_dict())


# --------------------------
# Articles Resources
# --------------------------
class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200


class ShowArticle(Resource):
    def get(self, id):
        page_views = session.get('page_views', 0) + 1
        session['page_views'] = page_views

        if page_views > 3:
            return {'message': 'Maximum pageview limit reached'}, 401

        article = Article.query.get(id)
        if not article:
            return {'message': 'Article not found'}, 404

        return make_response(jsonify(article.to_dict()), 200)


# --------------------------
# Add Resources to API
# --------------------------
api.add_resource(ClearSession, '/clear')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


# --------------------------
# Run the App
# --------------------------
if __name__ == '__main__':
    app.run(port=5555, debug=True)
