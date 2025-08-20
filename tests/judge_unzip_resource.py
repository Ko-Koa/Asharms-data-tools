import base64

import requests
import pydash as _
from loguru import logger

from ashArms.downloader import read_download_list
from ashArms.typings import DownloadInfo
from utils.buffer import Buffer


def judge_unzip(file_info: DownloadInfo):
    logger.debug(f"Judge file : {file_info['name']}")
    # filter .cpk .acb
    filter_str = [".cpk", ".acb", ".awb", "l2d_"]
    for i in filter_str:
        if i in file_info["name"]:
            return False
    download_url = file_info["url"]
    file_response = requests.get(download_url)
    try:
        base64_decode = base64.b64decode(file_response.content)
        buffer = Buffer.create(base64_decode)
        magic = buffer.read_int32_be()
        if hex(magic) == "0x1f8b0800":
            return True
        return False
    except:
        return False


if __name__ == "__main__":
    game_version = "1.0.21"
    download_list = read_download_list(game_version=game_version)
    file_info_list = _.map_(download_list, lambda r: r[0])[1:]  # don't download Verison
    file_name_list = []
    for file_info in file_info_list:
        if judge_unzip(file_info):
            file_name_list.append(file_info["name"])
    logger.debug(file_name_list)
