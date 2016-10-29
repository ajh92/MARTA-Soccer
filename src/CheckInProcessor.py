import os
import requests
from sqlalchemy import select

MARTA_API_KEY = os.environ['MARTA_API_KEY']
EVENTS = {'TUESDAY SOCCER': {'duration': '1 hour'}}


class CheckInProcessor(object):

    def __init__(self, connection, meta):
        self.connection = connection
        self.meta = meta
        self.stations = {}

        s = select([meta.tables['stations']])
        res = connection.execute(s)
        for row in res:
            self.stations[row['id']] = row['name']

    def get_est_train_time(self, origin_id, dest_id):
        r = (requests.get("http://developer.itsmarta.com/RealtimeTrain/"
                          "RestServiceNextTrain/GetRealtimeArrivals?"
                          "apikey=826ad80e-a7b4-47b5-8eb7-460320da8a19"))
        arrivals = r.json()

        best_time = float("inf")
        current_train = {'TRAIN_ID': None}
        arrival_time = '<unknown>'

        for arrival in arrivals:
            if (arrival['STATION'] == self.stations[origin_id] and
               120 <= int(arrival['WAITING_SECONDS']) <= best_time):
                current_train = arrival

        for arrival in arrivals:
            if(arrival['TRAIN_ID'] == current_train['TRAIN_ID'] and
               arrival['STATION'] == self.stations[dest_id]):
                arrival_time = arrival['WAITING_TIME']

        return ("Estimated arrival at " + self.stations[dest_id] +
                " in " + arrival_time)

    def get_est_event_time(self, dest_id):
        if dest_id in EVENTS:
            return ("Estimated Event Duration: " +
                    EVENTS[dest_id]['duration'])

    def get_time_update(self, checkin):
        if checkin['dest_id'] in self.stations:
            return self.get_est_train_time(checkin['origin_id'],
                                           checkin['dest_id'])
        else:
            return self.get_est_event_time(checkin['dest_id'])

    def process_checkin(self, checkin):
        msg = ("Jose checked in at " + self.stations[checkin['origin_id']] +
               " en route to " + self.stations[checkin['dest_id']] + ". " +
               self.get_time_update(checkin))

        print(msg)
        r = requests.post(os.environ['EASYSMS_URL'] + '/messages',
                          data={'to': '+14044290402', 'body': msg})

        return True
