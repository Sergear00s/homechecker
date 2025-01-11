import logging.handlers
import requests
import config
import time
import logging
import paramiko
import re

file_handler = logging.handlers.RotatingFileHandler("logs/homechecker.log", maxBytes=config.LOG_FILE_SIZE, backupCount=5)
file_handler.setFormatter(logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s - %(message)s]'))
logger = logging.getLogger("homechecker")
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
pkey = paramiko.RSAKey.from_private_key_file(config.PRIVATE_KEY_PATH)

COMMAND= "who | awk '{print $1}' | sort | uniq | grep -v 'bocal'"
hed = {
                "Authorization": f"Bearer {config.HOMEMAKER_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json"
        }

def execute_cmd(target, username, key, command):
    out = None
    err = None
    try:
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=target,
                username=username,
                pkey=key
            )
            stdin, stdout, stderr = ssh.exec_command(command)
            out = stdout.read().decode()
            err = stderr.read().decode()
    except paramiko.ssh_exception.NoValidConnectionsError:
        logger.error(f"SSH connection unreachable for target: {target}")
    except paramiko.AuthenticationException:
        logger.error(f"Authentication error for target: {target}")
        exit(1)
    except Exception as e:
        if e.errno == 110:
            logger.error(f"Connection Timeout:{target}, {str(e)}")
            return None, None
        logger.error(f"Error!, {e}")
        exit(1)
    return (out, err)


# def convert_to_ip(value: str) -> str:
#     pattern = r'^k(\d+)m(\d+)s(\d+)$'
#     match = re.match(pattern, value)
#     if not match:
#         raise ValueError("format error")
#     part1 = int(match.group(1))  
#     part2 = int(match.group(2))
#     part3 = int(match.group(3)) 
#     return f"10.1{part1}.{part2}.{part3}"
    

# def tgt_to_addr(tgt) -> str:
#     f = tgt[10::]
#     b = f[:8]
#     return convert_to_ip(b)



def list_homes() -> list:
    homes = requests.get(f"{config.HOMEMAKER_ENDPOINT}/homes", headers=hed)
    if (homes.status_code == 200):
        return homes.json()
    else:
        logger.error(f"Error homemaker api! - resp.status_code = {homes.status_code}")
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
        logger.error("Runtime error! resp.status_code = 409")
        raise RuntimeError(f"No home with this name exposed! {iqn}, {login}")
    if (resp.status_code == 400):
        logger.error("Runtime error! resp.status_code = 400")
        raise RuntimeError("error")
    if (resp.status_code == 404):
        logger.error("Runtime error! resp.status_code = 404")
        raise RuntimeWarning(f"couldnt close for iqn : {iqn}, login : {login}")
    logger.info(f"Iqn - > {iqn} , {login} is closed")

def check_fails():
    actives = get_active_sessions()
    for i in actives:
        user = i["identifier"]
        tgt = i["exposed_to"]
        # ips = tgt_to_addr(tgt)
        ips = tgt[10::]
        out, err = execute_cmd(ips, "bocal", pkey, COMMAND)
        if (out is None):
            close(tgt, user)
        else:
            out = out.strip()
            if out != user:
                close(tgt, user)
            else:
                logger.info(f"User {user} is still active!")

def main():
    if pkey == None:
        raise Exception("Private key is invalid!")
    while True:
        logger.debug("Checking...")
        check_fails()
        logger.debug("Checked")
        time.sleep(config.PERCHECK_TIME_IN_SEC)
main()