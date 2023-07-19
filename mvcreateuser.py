from mvlogger import *
from mvapi import create_user

class MVCreateUserRequest:
    def __init__(self):
        self.user_key = create_user()

    def get(self):
        return self.user_key

def main():
    device = MVCreateUserRequest()
    logging.info(device.get())


if __name__ == "__main__":
    main()