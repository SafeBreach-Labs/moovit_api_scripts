import argparse
import phonenumbers

from mvlogger import *
from mvapi import user_profile

class MVUserProfileRequest:
    def __init__(self, user_key):
        self.user_key = user_key
        self.profile_exist = False

        self.run()

    def run(self):
        response = user_profile(self.user_key)
        
        if not response.ok:
            logging.error('UserProfile request failed')
            exit(1)
            
        self.content = response.content
        self.__parse_content()

    def has_profile(self):
        return self.profile_exist

    def get(self):
        return self.phone

    def __parse_content(self):
        plus_idx = self.content.find(b'+')
        
        if plus_idx != -1:
            phone_len = self.content[plus_idx - 1]
            str_phone_number = str(self.content[plus_idx:][:phone_len]) 
            phone_number = phonenumbers.parse(str_phone_number)

            if phonenumbers.is_valid_number(phone_number):
                self.phone = phone_number
                self.profile_exist = True
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-userkey', required=True, type=str, help="User_Key")
    args = parser.parse_args()

    user_key = args.userkey

    user = MVUserProfileRequest(user_key)

    if user.has_profile(): 
        profile = user.get()
        logging.info(profile)

if __name__ == "__main__":
    main()

