from loguru import logger

from settings.gameEnv import GameEnv
from ashArms.downloader import download_file
from ashArms.api.AsharmsLogin import getServerStatus
from settings.downloadSetting import DOWNLOAD_FILE_NAME_LIST


def main():
    status = getServerStatus(GameEnv.version)
    state = status.get("state")
    if state != "2":
        logger.warning(f"Game server error, Response: {status}")
        return

    faild_name_list = []
    for file_name in DOWNLOAD_FILE_NAME_LIST:
        try:
            download_file(file_name, GameEnv.version)
        except:
            faild_name_list.append(file_name)

    if len(faild_name_list) != 0:
        logger.error(f"Error: {faild_name_list}")


if __name__ == "__main__":
    main()
