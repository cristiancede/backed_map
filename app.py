from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

USER_DB = "postgres"
PASS_DB = "Azufaifa1"
URL_DB = "localhost"
NAME_DB = "info"
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACE_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    description = db.Column(db.String(250))

    def __str__(self):
        return (
            f"id: {self.id}\n"
            f"name: {self.name}\n"
            f"description: {self.description}\n"
        )


try:
    db.create_all()
except Exception as e:
    print(f"Error during database initialization: {e}")


class InfoResource(Resource):
    def get(self, info_id):
        info_data = Info.query.get_or_404(info_id)
        return {'id': info_data.id, 'name': info_data.name, 'description': info_data.description}

    def put(self, info_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name cannot be blank')
        parser.add_argument('description', type=str)

        args = parser.parse_args()
        info_data = Info.query.get_or_404(info_id)

        info_data.name = args['name']
        info_data.description = args['description']

        db.session.commit()

        return {'id': info_data.id, 'name': info_data.name, 'description': info_data.description}

    def delete(self, info_id):
        info_data = Info.query.get_or_404(info_id)
        db.session.delete(info_data)
        db.session.commit()
        return {'message': 'Info deleted successfully'}


class InfoListResource(Resource):
    def get(self):
        info_list = Info.query.all()
        return [{'id': info_data.id, 'name': info_data.name, 'description': info_data.description} for info_data in
                info_list]

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name cannot be blank')
        parser.add_argument('description', type=str)

        args = parser.parse_args()
        new_info = Info(name=args['name'], description=args['description'])
        db.session.add(new_info)
        db.session.commit()

        return {'id': new_info.id, 'name': new_info.name, 'description': new_info.description}, 201


api = Api(app)
api.add_resource(InfoListResource, '/info')
api.add_resource(InfoResource, '/info/<int:info_id>')

if __name__ == '__main__':
    app.run(debug=True)
