import json
import gzip
import base64
import random

import pydash as _
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad, pad

KEY = "HgKeAEzJ"
IV = "Areyoumy"


def getSubkey():
    return str(random.randint(10000, 99999))


def unzip_file(compressed_data: str):
    b64_decode_data = base64.b64decode(compressed_data)
    decompressed_data = gzip.decompress(b64_decode_data).decode("utf-8-sig")
    data = decompressed_data.replace("\xff\xff", "\x20").strip()
    return json.loads(data, strict=False)


def encrypt_request_data(plaintext: dict[str, str]):
    des = DES.new(key=KEY.encode("utf-8"), mode=DES.MODE_CBC, iv=IV.encode("utf-8"))
    plaintext_str = "&".join(f"{k}={v}" for k, v in plaintext.items())
    plaintext_pad = pad(plaintext_str.encode("utf-8"), 8, "pkcs7")
    return des.encrypt(plaintext_pad).hex().upper()


def decrypt_request_data(cipher: str) -> dict[str, str]:
    des = DES.new(key=KEY.encode("utf-8"), mode=DES.MODE_CBC, iv=IV.encode("utf-8"))
    decrypt_data_bytes = des.decrypt(bytes.fromhex(cipher))
    decrypt_str = unpad(
        decrypt_data_bytes, 8, "pkcs7"
    ).decode()  # block size is 8
    decrypt_params = decrypt_str.split("&")
    return {
        decode_param.split("=")[0]: decode_param.split("=")[1]
        for decode_param in decrypt_params
    }


if __name__ == "__main__":
    from loguru import logger

    test_Data = "72C88422A0922E713AE0D41D879BBE888D3A03EA4D76E0E670642F22AA21267CA2C4368CB5DE53848BEAB69982BD13AEC6EE66B2077114DDBD27E928BCF8002C70E7F644C82EEC96"
    decrypt_data = decrypt_request_data(test_Data)
    logger.debug(f"Decrypt:\n{json.dumps(decrypt_data,indent=4,ensure_ascii=False)}")
    encrypt_data = encrypt_request_data(decrypt_data)
    logger.debug(f"Encrypt:\n{encrypt_data}")
