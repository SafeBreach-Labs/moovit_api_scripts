import argparse
import logging

from mvapi import get_payment_account
from mvgetjwt import MVJWTRequest

class MVGetPaymentAccountRequest:
    def __init__(self, user_key):
        self.user_key = user_key
        self.run()

    def run(self):
        self.token = MVJWTRequest(self.user_key).get()

    def get(self):
        return get_payment_account(self.user_key, self.token).content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-userkey', required=True, type=str, help="User_Key")
    args = parser.parse_args()

    user_key = args.userkey
    
    payment_account = MVGetPaymentAccountRequest(user_key)
    logging.info(payment_account.get())
        

if __name__ == "__main__":
    main()