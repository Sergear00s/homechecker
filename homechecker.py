import requests
import ftlib
import config
import time

api = ftlib.Ftlib(config.INTRA_APP_PUBLIC, config.INTRA_APP_SECRET)
hed = {
                "Authorization": f"Bearer {config.HOMEMAKER_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json"
        }

def list_homes() -> list:
    homes = requests.get(f"{config.HOMEMAKER_ENDPOINT}/homes", headers=hed)
    if (homes.status_code == 200):
        return homes.json()
    else:
        raise ConnectionError("status code is 200")

def get_active_sessions() -> list:
    lst = list_homes()
    out  = []
    for i in lst:
        if i["busy"] == True:
            out.append(i)
    return out

def close(iqn : str, login : str):
    data = { "force": True,
    "iqn": iqn,
    "login": login}
    resp = requests.put(f"{config.HOMEMAKER_ENDPOINT}/homes/umount", headers=hed, json=data)
    if (resp.status_code == 409):
        raise RuntimeError(f"No home with this name exposed! {iqn}, {login}")
    if (resp.status_code == 400):
        raise RuntimeError("error")
    if (resp.status_code == 404):
        raise RuntimeWarning(f"couldnt close for iqn : {iqn}, login : {login}")
    print(iqn, login, " is closed")

def check_fails():
    actives = get_active_sessions()
    for i in actives:
        user = i["identifier"]
        user_intra = api.Users.get_user_by_login(user)
        if (user_intra.location is None):
            #close home
            close(i["exposed_to"], user)
            ##
            print("closed , ", user)
            pass
        print("not none, ", user)
        time.sleep(0.5)

def main():
    while True:
        check_fails()
        time.sleep(config.PERCHECK_TIME_IN_SEC)
