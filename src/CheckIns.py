import os
import datetime
from flask_restful import abort, Resource, reqparse
from .CheckInProcessor import CheckInProcessor
from sqlalchemy import MetaData, create_engine, select
from sqlalchemy.exc import IntegrityError

engine = create_engine(os.environ['DATABASE_URL'])
meta = MetaData()
meta.reflect(bind=engine)

connection = engine.connect()


def abort_if_not_exists(checkin_id):
    if not checkin_id.isdigit():
        abort(400,
              message="Invalid checkin_id {} specified".format(checkin_id))
    s = select([meta.tables['checkins']]).where(
                meta.tables['checkins'].c.id == checkin_id)
    res = connection.execute(s)
    if res.rowcount == 0:
        abort(404,
              message="CheckIn {} doesn't exist".format(checkin_id))


class CheckIn(Resource):
    """
n    Represents checkins of checkins to the tracking system
    """
    base_uri = '/api/v1/checkins/'

    def get(self, checkin_id):
        """"
        Returns information about requested checkin
        """
        abort_if_not_exists(checkin_id)
        # Probably shouldn't run this twice, but in a hurry
        s = select([meta.tables['checkins']]).where(
            meta.tables['checkins'].c.id == checkin_id)
        res = connection.execute(s)
        checkins = [(dict(row.items())) for row in res]
        ts = checkins[0].pop('timestamp')
        if ts is not None:
                checkins[0]['timestamp'] = str(ts)
        return checkins[0]

    def delete(self, checkin_id):
        """
        Delete information about checkin
        """
        abort_if_not_exists(checkin_id)
        del CHECKINS[checkin_id]
        ret = {'message': "Checkin Deleted", 'checkin_id': checkin_id}
        return ret


class CheckInList(Resource):

    base_uri = '/api/v1/checkins/'

    def verify_args(self, args):
            return True

    def get(self):
        s = select([meta.tables['checkins']])
        res = connection.execute(s)
        checkins = [(dict(row.items())) for row in res]

        for checkin in checkins:
            ts = checkin.pop('timestamp')
            if ts is not None:
                checkin['timestamp'] = str(ts)

        return checkins

    def post(self):
        processor = CheckInProcessor(connection, meta)
        parser = reqparse.RequestParser()
        parser.add_argument('participant_id', required=True)
        parser.add_argument('chaperone_id', required=True)
        parser.add_argument('origin_id', required=True)
        parser.add_argument('destination_id', required=True)
        args = parser.parse_args()
        if self.verify_args(args):
            try:
                res = connection.execute(meta.tables['checkins'].insert(),
                                         {'kid_id': args['participant_id'],
                                          'timestamp': datetime.datetime.now(),
                                          'chaperone_id': args['chaperone_id'],
                                          'origin_id': args['origin_id'],
                                          'dest_id': args['destination_id']})
            except IntegrityError as e:
                abort(400, message=str(e))

            s = select([meta.tables['checkins']]).where(
                meta.tables['checkins'].c.id == res.inserted_primary_key[0])
            res = connection.execute(s)
            checkins = [(dict(row.items())) for row in res]
            ts = checkins[0].pop('timestamp')
            if ts is not None:
                checkins[0]['timestamp'] = str(ts)
            processor.process_checkin(checkins[0])
            ret = {'uri': CheckInList.base_uri + str(checkins[0]['id']),
                   'checkin': checkins[0]}
            return ret
