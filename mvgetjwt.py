import argparse

from mvlogger import *
from mvapi import firebase_register, verify_firebase_token

class MVJWTRequest:
    def __init__(self, user_key, verbose=True):
        self.verbose = verbose
        self.user_key = user_key

        self.run()
    
    def run(self):
        logging.info(f'Requesting JWT for {self.user_key}')
        firebase_token = firebase_register(self.user_key)
        custom_token = verify_firebase_token(firebase_token)
        self.jwt = custom_token['idToken']

    def get(self):
        return self.jwt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-userkey', required=True, type=str, help="User_Key")
    args = parser.parse_args()

    user_key = args.userkey
    
    token_obj = MVJWTRequest(user_key)
    token = token_obj.get()

    logging.info(f'Token: {token}')


if __name__ == "__main__":
    main()