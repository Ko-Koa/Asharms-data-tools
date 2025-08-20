import json
import os
import requests
import pydash as _
from loguru import logger

from ashArms.api.AsharmsLogin import getRouteVersion
from ashArms.typings import DownloadInfo
from ashArms.utils.encryption import unzip_file
from settings.projectEnv import ProjectEnv
from utils.cache_utils import read_cache, write_cache


def get_download_list(
    resource_url: str, resource_md5: str
) -> dict[str, list[DownloadInfo]]:
    download_list_url = f"{resource_url}android/DownLoadList.txt.{resource_md5}"
    response = requests.get(download_list_url)
    download_list = _.filter_(response.text.split("#"), lambda r: r != "")
    download_info_list: list[DownloadInfo] = _.map_(
        download_list,
        lambda r: (
            {
                "name": r.split(",")[0],
                "url": f"https://cn-web.asharms.com/bili/prod/android/{r.split(',')[1]}.{r.split(',')[2]}",
                "md5": r.split(",")[2],
                "file_type": r.split(",")[3],
            }
        ),
    )
    return _.group_by(download_info_list, "name")


def read_download_list(game_version: str) -> dict[str, list[DownloadInfo]]:
    route_version = getRouteVersion(game_version=game_version)
    resource_url = route_version.get("resourceurl")
    resource_md5 = route_version.get("MD5")
    # 判断是否需要更新下载列表文件
    cache_download_list_md5 = read_cache("download_list_md5").get("md5")
    if resource_md5 != cache_download_list_md5:
        logger.debug("update download file list")
        write_cache("download_list_md5", {"md5": resource_md5})
        # udpate data
        download_list_data = get_download_list(resource_url, resource_md5)
        write_cache("download_list", download_list_data)

    return read_cache("download_list")


def _save_file(download_info: DownloadInfo, out_path: str):
    file_response = requests.get(url=download_info["url"])
    unzip_data = unzip_file(file_response.text)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(unzip_data, fp=f, ensure_ascii=False, indent=4)

    # write cache
    ori_cache = read_cache("has_download")
    ori_cache[download_info["name"]] = {"md5": download_info["md5"]}
    write_cache("has_download", ori_cache)

    logger.success(f"Saved file {download_info['name']}")


def download_file(file_name: str, game_version: str):
    # get file newest md5
    download_list = read_download_list(game_version=game_version)
    file_info_result = download_list.get(file_name)
    if file_info_result is None:
        logger.error(f"Can not find file: {file_name}")
        return
    file_info = file_info_result[0]
    file_md5 = file_info["md5"]
    has_download_list = read_cache("has_download")

    # check outdir exists
    if not os.path.exists(ProjectEnv.outPath):
        os.makedirs(ProjectEnv.outPath)

    file_out_path = os.path.join(ProjectEnv.outPath, f"{file_name}.json")
    if not os.path.exists(file_out_path):
        _save_file(file_info, file_out_path)
        return

    if has_download_list.get(file_name, {}).get("md5") != file_md5:
        _save_file(file_info, file_out_path)
        return
    logger.debug(f"File {file_info['name']} don`t need download")
