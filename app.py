from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

PARTICIPANTS = {}


def abort_if_participant_doesnt_exist(participant_id):
    if participant_id not in PARTICIPANTS:
        abort(404,
              message="Participant {} doesn't exist".format(participant_id))

parser = reqparse.RequestParser()
parser.add_argument('task')


class Participant(Resource):
    """
    Shows a single participant and allows deletion of participant
    """
    def get(self, participant_id):
        abort_if_participant_doesnt_exist(participant_id)
        return PARTICIPANTS[participant_id]

    def delete(self, participant_id):
        abort_if_participant_doesnt_exist(participant_id)
        del PARTICIPANTS[participant_id]

    def put(self, participant_id):
        args = parser.parse_args()
        participant = {'id': args['participant_id'],
                       'last_name': args['last_name'],
                       'given_names': args['given_names']}
        PARTICIPANTS[participant_id] = participant


class ParticipantList(Resource):
    def get(self):
        return PARTICIPANTS

    # def post(self):
    #     args = parser.parse_args()
    #     todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
    #     todo_id = 'todo%i' % todo_id
    #     TODOS[todo_id] = {'task': args['task']}
    #     return TODOS[todo_id], 201


api.add_resource(ParticipantList, '/api/v1/participants')
api.add_resource(Participant, '/api/v1/participants/<participants_id>')


if __name__ == '__main__':
    app.run(debug=True)
