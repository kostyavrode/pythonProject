import sys
import requests
import re
import string
import winreg as wrg
import os
def main():
    if len(sys.argv) >= 3:
        file_id = sys.argv[1]
        destination = sys.argv[2]
    else:
        file_id = "settings"
        destination = "settings.reg"


    print(f"dowload {file_id} to {destination}")
    download_file_from_google_drive(file_id, destination)
    registry_values = parse_registry_values(destination)
    subkey = find_values(destination)[0]
    for value in registry_values:
        for key, value in value.items():
            print(f"{key}: {value}")
            soft=wrg.OpenKeyEx(wrg.HKEY_CURRENT_USER,subkey,0,wrg.KEY_ALL_ACCESS)
            wrg.SetValueEx(soft,key,None,wrg.REG_DWORD,0)

    launch_steam()

def download_file_from_google_drive(file_id, destination):
    URL = "https://drive.usercontent.google.com/download?id=1IGENwFzLm8bBEboISadYSNEdxbnjz1fH&export=download&confirm=1"
    session = requests.Session()
    response = session.get(URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)
    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(URL, params=params, stream=True)
    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None

def find_values(file_path):
    with open(file_path, "r") as file:
        reg_text = file.read()
        cleaned_text = remove_non_readable_characters(reg_text)
    lines = cleaned_text.split("n")
    results = []

    for line in lines:
        if "HKEY_CURRENT_USER" in line:
            start_index = line.index("HKEY_CURRENT_USER") + len("HKEY_CURRENT_USER") + 1
            end_index = line.index("]", start_index)
            result = line[start_index:end_index]
            results.append(result)

    return results
def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

def remove_non_readable_characters(text):
    readable_chars = string.printable
    cleaned_text = ""

    for char in text:
        if char in readable_chars:
            cleaned_text += char
    return cleaned_text

def parse_registry_values(file_path):
    with open(file_path, "r") as file:
        reg_text = file.read()
        registry_values = []

        cleaned_text = remove_non_readable_characters(reg_text)
        matches = re.findall(r'"([^"]+)"=dword:([^"]+)', cleaned_text)
        for match in matches:
            key = match[0]
            value = match[1]
            registry_values.append({key: value})

    return registry_values
def find_steam_exe():
    steam_exe = None
    steam_paths = [
        "C:\Program Files (x86)\Steam\Steam.exe",
        "C:\Program Files\Steam\Steam.exe"
    ]

    for path in steam_paths:
        if os.path.exists(path):
            steam_exe = path
            break

    return steam_exe

def launch_steam():
    steam_exe = find_steam_exe()

    if steam_exe:
        os.startfile(steam_exe)
    else:
        print("Steam не найден на вашем компьютере.")


if __name__ == "__main__":
    main()