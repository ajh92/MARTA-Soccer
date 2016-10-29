import os

MARTA_API_KEY = os.environ['MARTA_API_KEY']


class CheckInProcessor(object):

    def __init__(self, participants):
        self.participants = participants

    def process_checkin(self, checkin):
        return True
