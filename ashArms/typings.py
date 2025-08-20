from typing import TypedDict


class DownloadInfo(TypedDict):
    name: str
    url: str
    md5: str
    file_type: str
