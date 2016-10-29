from flask import Flask
from flask_restful import Api
from src.CheckIns import CheckIn, CheckInList
from src.Participants import Participant, ParticipantList

app = Flask(__name__)
api = Api(app)

api.add_resource(CheckInList, '/api/v1/checkins')
api.add_resource(CheckIn, '/api/v1/checkins/<checkin_id>')
api.add_resource(ParticipantList, '/api/v1/participants')
api.add_resource(Participant, '/api/v1/participants/<participant_id>')


if __name__ == '__main__':
    app.run(debug=True)
