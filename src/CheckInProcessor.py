import os
import requests
from sqlalchemy import select

MARTA_API_KEY = os.environ['MARTA_API_KEY']


class CheckInProcessor(object):

    def __init__(self, connection, meta):
        self.connection = connection
        self.meta = meta
        self.stations = {}

        s = select([meta.tables['stations']])
        res = connection.execute(s)
        for row in res:
            self.stations[row['id']] = {'name': row['name'],
                                        'marta_api_id': row['marta_api_id']}

    def get_est_train_time(self, origin_id, dest_id):
        r = (requests.get("http://developer.itsmarta.com/RealtimeTrain/"
                          "RestServiceNextTrain/GetRealtimeArrivals?"
                          "apikey=" + MARTA_API_KEY))
        arrivals = r.json()

        best_time = float("inf")
        current_train = {'TRAIN_ID': None}
        arrival_time = '<unknown>'

        if(self.stations[dest_id]['marta_api_id'] is None):
            return ""

        for arrival in arrivals:
            if (arrival['STATION'] == self.stations[origin_id]['marta_api_id'] and
                120 <= int(arrival['WAITING_SECONDS']) <= best_time):
                current_train = arrival

        for arrival in arrivals:
            if(arrival['TRAIN_ID'] == current_train['TRAIN_ID'] and
               arrival['STATION'] == self.stations[dest_id]['marta_api_id']):
                arrival_time = arrival['WAITING_TIME']

        return ("Estimated arrival at " + self.stations[dest_id]['name'] +
                " in " + arrival_time)

    def get_est_event_time(self, dest_id):
        pass

    def get_time_update(self, checkin):
        if checkin['dest_id'] in self.stations:
            return self.get_est_train_time(checkin['origin_id'],
                                           checkin['dest_id'])
        else:
            return self.get_est_event_time(checkin['dest_id'])

    def process_checkin(self, checkin):
        s = select([self.meta.tables['individuals']]).where(
            self.meta.tables['individuals'].c.id == checkin['kid_id'])
        individual = self.connection.execute(s).fetchone()

        msg = (individual['firstname'] + " checked in at " +
               self.stations[checkin['origin_id']]['name'] +
               " en route to " + self.stations[checkin['dest_id']]['name'] +
               ". " + self.get_time_update(checkin))

        s = select([self.meta.tables['phonenums'].join(
            self.meta.tables['kids_parents'],
            self.meta.tables['phonenums'].c.individ_id ==
            self.meta.tables['kids_parents'].c.parent_id)]).where(
                self.meta.tables['kids_parents'].c.kid_id == checkin['kid_id'])
        info = self.connection.execute(s).fetchone()
        print(msg)
        if info is not None:
            print(info['phone'])
#        r = requests.post(os.environ['EASYSMS_URL'] + '/messages',
#                        data={'to': '+14044290402', 'body': msg})

        return True
