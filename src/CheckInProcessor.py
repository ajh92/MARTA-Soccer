import os
import requests
import json

MARTA_API_KEY = os.environ['MARTA_API_KEY']
STATIONS = {'CHAMBLEE STATION', 'FIVE POINTS STATION'}
EVENTS = {'TUESDAY SOCCER': {'duration': '1 hour'}}


class CheckInProcessor(object):

    def __init__(self, participants):
        self.participants = participants

    def get_est_train_time(self, origin_id, destination_id):
        r = (requests.get("http://developer.itsmarta.com/RealtimeTrain/"
                          "RestServiceNextTrain/GetRealtimeArrivals?"
                          "apikey=826ad80e-a7b4-47b5-8eb7-460320da8a19"))
        arrivals = r.json()

        best_time = float("inf")
        current_train = {'TRAIN_ID': None}
        arrival_time = 'unknown'

        for arrival in arrivals:
            if (arrival['STATION'] == origin_id and
               120 <= int(arrival['WAITING_SECONDS']) <= best_time):
                current_train = arrival

        for arrival in arrivals:
            if(arrival['TRAIN_ID'] == current_train['TRAIN_ID'] and
               arrival['STATION'] == destination_id):
                arrival_time = arrival['WAITING_TIME']

        return ("Estimated arrival at " + destination_id.title() + " in " +
                arrival_time)

    def get_est_event_time(self, destination_id):
        return ("Estimated Event Duration: " +
                EVENTS[destination_id]['duration'])

    def get_time_update(self, checkin):
        if checkin['destination_id'] in STATIONS:
            return self.get_est_train_time(checkin['origin_id'],
                                           checkin['destination_id'])
        else:
            return self.get_est_event_time(checkin['destination_id'])

    def process_checkin(self, checkin):
        print("Jose checked in at " + checkin['origin_id'].title() +
              " en route to " + checkin['destination_id'].title())
        print(self.get_time_update(checkin))

        return True
