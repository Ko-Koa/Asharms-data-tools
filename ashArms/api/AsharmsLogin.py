import requests

from ashArms.utils.encryption import encrypt_request_data, getSubkey

headers = {
    "Host": "cn-prod-bili-gl.asharms.com:7055",
    "User-Agent": "UnityPlayer/2021.3.45f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Unity-Version": "2021.3.45f1",
}


def getRouteVersion(game_version: str):
    data = {
        "version": game_version,
        "channelid": "999",
        "session": "UNLOGIN",
        "subkey": getSubkey(),
        "uid": "-1",
    }
    encrypt_data = {"data": encrypt_request_data(data)}
    url = "http://cn-prod-bili-gl.asharms.com:7055/AsharmsLogin/getRouteVersion"
    resposne = requests.post(url=url, headers=headers, data=encrypt_data, timeout=10)
    return resposne.json()


def getServerStatus(game_version: str):
    data = {
        "channelid": "BILI",
        "version": game_version,
        "session": "UNLOGIN",
        "subkey": getSubkey(),
        "uid": "-1",
    }
    encrypt_data = {"data": encrypt_request_data(data)}
    url = "http://cn-prod-bili-gl.asharms.com:7055/AsharmsLogin/getServerStatus"
    resposne = requests.post(url=url, headers=headers, data=encrypt_data, timeout=10)
    return resposne.json()


if __name__ == "__main__":
    game_version = "1.0.21"
    route_version_response = getRouteVersion(game_version=game_version)
    print(route_version_response)
