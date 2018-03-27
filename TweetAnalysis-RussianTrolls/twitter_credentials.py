import random

class twitter_credentials:

    def __init__(self):

        option1 = {
            "consumer_key":"XXXX",
            "consumer_secret":"XXXX",
            "access_token":"XXXX",
            "access_token_secret":"XXXX"
        }
        option2 = {
            "consumer_key":'XXXX',
            "consumer_secret":'XXXX',
            "access_token":'XXXX',
            "access_token_secret":'XXXX'
        }
        option3 = {
            "consumer_key":'XXXX',
            "consumer_secret":'XXXX',
            "access_token":'XXXX',
            "access_token_secret":'XXXX'
        }

        key = random.choice([option1, option2, option3])

        self.consumer_key = key['consumer_key']
        self.consumer_secret = key['consumer_secret']
        self.access_token = key['access_token']
        self.access_token_secret = key['access_token_secret']





