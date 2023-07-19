import json
import requests
import urllib3

from mvlogger import *

#############################################################################

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#############################################################################

proxies = {'https' : 'http://127.0.0.1:8888'}

#############################################################################

def create_user():
    api_url = 'https://app4.moovitapp.com/services-app/services/V4/UserDetails/CreateUser'
    headers = {
        'CLIENT_VERSION': '5.94.2.537',
        'Host': 'app4.moovitapp.com',
        'Content-Type': 'application/octet-stream',
        'Content-Length': '253'
    }
    data = open(r'real_create_user_request_from_israel.bin', 'rb').read()
    response = requests.post(api_url, verify=False, proxies=proxies ,headers=headers, data=data)
    
    user_key = None

    if response.ok:
        user_key = (response.content[10:42]).decode('utf-8')
        logging.info(f'Create User-Key -> {user_key}')
        
    return user_key

def firebase_register(user_key):
    logging.info(f'Registering {user_key} to firebase')
    api_url = 'https://app4.moovitapp.com/services-app/services/Firebase/Register'
    headers = {
        'USER_KEY' : user_key,
        'App-Id' : '1'
    }

    response = requests.post(api_url, verify=False, proxies=proxies, headers=headers)
    if response.ok:
        custom_token = response.content[7:-1]
        return custom_token
    else:
        logging.error('Failed registering to firebase')
        exit(1)

def verify_firebase_token(firebase_token):
    logging.info(f'Verifing firebase token')
    api_url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key=AIzaSyBkZSYR6T3PYyZ6ery0LP_6e7k1Ia3TRjM'
     
    headers = {
        'X-Android-Package' : 'com.tranzmate',
        'X-Android-Cert' : 'C56ABF7C6890113ED6654E381E2A1797DA3E7F6A'
    }
    x = {
        "token": firebase_token.decode('utf-8'),
        "returnSecureToken": True
    }
    data = json.dumps(x)

    headers['Content-Length'] = str(len(data))

    response = requests.post(api_url, verify=False ,proxies=proxies, headers=headers, data=data)

    if response.ok:
        custom_token = json.loads(response.content)
        logging.info('Firebase token has verified')
        return custom_token
    else:
        logging.error('Failed to verify firebase token')
        exit(1)

def user_profile(user_key):
    global proxies
    api_url = 'https://app4.moovitapp.com/services-app/services/V4/UserDetails/UserProfile'
    headers = {
        'USER_KEY': user_key
    }
    data = open(r"user_profile.bin", 'rb').read()
    response = requests.post(api_url, verify=False ,proxies=proxies, headers=headers, data=data)
    
    return response

def generate_verification_token(user_key, access_token, phone_number):
    logging.info(f'Generating OTP verification for {phone_number}')
    api_url = 'https://app4.moovitapp.com/services-app/services/PaymentContext/GenerateVerificationToken'
    headers = {
        'CLIENT_VERSION': '5.94.2.537',
        'USER_KEY': user_key,
        'Access-Token': access_token,
        'Host': 'app4.moovitapp.com',
        'Content-Length': '44'
    }
    data = open(r'generate_verification_token.bin', 'rb').read()
    data = data.replace(data[7:16], bytes(phone_number, 'utf-8'))
    response = requests.post(api_url, verify=False, proxies=proxies ,headers=headers, data=data)

    if response.ok:
        logging.info('Generated.')
        return True

    logging.error('Failed to generate OTP')
    return False

def register_verification(user_key, access_token, code):
    api_url = 'https://app4.moovitapp.com/services-app/services/PaymentContext/RegistrationVerification'
    headers = {
        'CLIENT_VERSION' : '5.94.2.537',
        'USER_KEY' : user_key,
        'Access-Token' : access_token,
        'Host' : 'app4.moovitapp.com',
        'Content-Length' : '32'
    }
    data = open(r'registration_verification.bin', 'rb').read()
    data = data.replace(data[23:27], code)
    
    response = requests.post(api_url, verify=False, proxies=proxies ,headers=headers, data=data)
    
    if response.ok:
        logging.info(f'OTP verified, OTP: {code}')
        return True

    return False

def get_payment_account(user_key, token):
    api_url = 'https://app4.moovitapp.com/services-app/services/PaymentContext/GetPaymentAccount'
    headers = {
        'CLIENT_VERSION' : '5.94.2.537',
        'USER_KEY' : user_key,
        'Access-Token' : token,
        'Host' : 'app4.moovitapp.com',
        'Content-Length' : '1'
    }
    data = b'\x00'
    response = requests.post(api_url, verify=False, proxies=proxies ,headers=headers, data=data)
    
    if response.ok:
        logging.info('Got PaymentAccount')

    return response

def get_train_ticket(user_key, token):
    api_url = 'https://app4.moovitapp.com/services-app/services/PTB/Activations/SetActivationByLocation'
    headers = {
        'CLIENT_VERSION' : '5.94.2.537',
        'USER_KEY' : user_key,
        'Access-Token' : token,
        'Host' : 'app4.moovitapp.com',
        'Content-Length' : '49'
    }
    data = open(r'set_activation_by_location.bin', 'rb').read()
    response = requests.post(api_url, verify=False, proxies=proxies ,headers=headers, data=data)

    if response.ok:
        var_id_index = response.content.find(b'\x0B\x00\x0C\x00\x00\x00')
        ticket_len = response.content[var_id_index + 6]
        ticket = response.content[var_id_index + 7: var_id_index + 7 + ticket_len].decode('utf-8')
        logging.info(f'Train Ticket: {ticket}')
        return ticket
    else:
        logging.error('Train Ticket Failed')