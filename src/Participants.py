from flask_restful import abort, Resource, reqparse

participants = {}


class Participant(Resource):
    """
    Shows a single participant and allows deletion of participant
    """
    def abort_if_participant_doesnt_exist(self, participant_id):
        if participant_id not in participants:
            abort(404,
                  message= "Participant {} doesn't exist".format(participant_id))

    def get(self, participant_id):
        participant_id = participant_id
        self.abort_if_participant_doesnt_exist(participant_id)
        return participants[participant_id]

    def delete(self, participant_id):
        self.abort_if_participant_doesnt_exist(participant_id)
        del participants[participant_id]

    def put(self, participant_id):
        parser = reqparse.RequestParser()
        parser.add_argument('last_name', required=True)
        parser.add_argument('given_names', required=True)
        parser.add_argument('guardian_id', required=True)
        args = parser.parse_args()

        if self.verify_args(args):
            participant = {'id': participant_id,
                           'last_name': args['last_name'],
                           'given_names': args['given_names']}
            self.participants[participant_id] = participant
            ret = {'uri': ParticipantList.base_uri + str(participant_id),
                   'participant': participant}
            return ret


class ParticipantList(Resource):

    base_uri = '/api/v1/participants'

    def verify_args(self, args):
        return True

    def get(self):
        return participants
