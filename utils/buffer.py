import struct
import binascii
from typing import Literal, Union, List

type BufferList = List[Buffer]
type BufferMode = Literal["static", "dynamic"]
type BufferLike = Union[bytearray, bytes, List[int], Buffer, int, str]
type BufferEncoding = Literal["hex", "utf-8", "ascii"]
type BufferEncErrors = Literal["strict", "ignore", "replace", "xmlcharrefreplace"]


def hex_dump(
    buffer: Union[bytes, bytearray],
    length: Union[int, None] = None,
    title: Union[str, None] = None,
    show_length: bool = False,
) -> str:
    result = "\n"
    if title is not None:
        result += f"[{title}]\n"

    if length is None:
        buffer_length = len(buffer)
    else:
        buffer_length = min(length, len(buffer))

    if show_length:
        result += f"Length: 0x{buffer_length:02x} / 0x{len(buffer):02x}\n"

    for i in range(0, buffer_length, 16):
        chunk = buffer[i : i + 16]
        hex_chunk = " ".join(f"{byte:02x}" for byte in chunk)
        ascii_chunk = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in chunk)
        result += f"{i:08x}  {hex_chunk:<48}  {ascii_chunk}\n"
    return result


class Buffer:
    @staticmethod
    def create(data: BufferLike, encoding: str = "utf-8"):
        if type(data) == bytes or type(data) == list:
            data = bytearray(data)
        elif type(data) == bytearray:
            data = data
        elif type(data) == int:
            raise TypeError(f"Data type {type(data)} is not supported!")
        elif type(data) == str:
            if encoding == "hex":
                data = bytearray.fromhex(data)
            else:
                data = bytearray(data, encoding=encoding)
        else:
            raise TypeError(f"Data type {type(data)} is not supported!")
        return Buffer(data=data)

    @staticmethod
    def alloc(length: int = 0):
        return Buffer(bytearray(length))

    @staticmethod
    def concat(buffer_list: BufferList):
        buffer = Buffer.alloc(0)
        buffer.append(buffer_list)
        return buffer

    def __init__(
        self,
        data: Union[bytearray, None] = None,
        read_mode: BufferMode = "static",
        write_mode: BufferMode = "static",
    ):
        self.buffer = data
        self.read_mode: BufferMode = read_mode
        self.write_mode: BufferMode = write_mode
        self.read_offset = 0
        self.write_offset = 0

    def get_end(self):
        if self.buffer is None:
            raise Exception("buffer is None, please use create function to init")
        return len(self.buffer)

    def set_read_mode(self, read_mode: BufferMode):
        self.read_mode = read_mode
        self.reset_read_offset()

    def set_read_offset(self, offset: int):
        self.read_offset = offset

    def reset_read_offset(self):
        self.read_offset = 0

    def get_read_offset(self) -> int:
        return self.read_offset

    def set_write_mode(self, write_mode: BufferMode):
        self.write_mode = write_mode
        self.reset_write_offset()

    def set_write_offset(self, write_offset: int):
        self.write_offset = write_offset

    def reset_write_offset(self):
        self.write_offset = 0

    def _unpack_from(self, fmt: str, offset: int = 0):
        if self.buffer is None:
            raise Exception("buffer is None, please use create function to init")
        data = struct.unpack_from(fmt, self.buffer, offset)[0]
        if self.read_mode == "dynamic":
            data = struct.unpack_from(fmt, self.buffer, self.read_offset)[0]
            self.read_offset += struct.calcsize(fmt)
        return data

    def _set_pack(self, fmt: str, data: BufferLike, offset: int):
        if type(data) == Buffer:
            data = data.to_bytearray()
        elif type(data) != int:
            data = Buffer.create(data=data).to_bytearray()

        if type(data) == bytearray:
            data = int.from_bytes(data)

        if self.buffer is None:
            raise Exception("buffer is None, please use create function to init")

        if self.write_mode == "dynamic":
            struct.pack_into(fmt, self.buffer, self.write_offset, data)
            self.write_offset += struct.calcsize(fmt)
        else:
            struct.pack_into(fmt, self.buffer, offset, data)

    def write_ubytes(
        self,
        data: BufferLike,
        length: int = 0,
        offset: int = 0,
        endian: Literal["<", ">"] = ">",
        pad: Literal["None", "Zeros"] = "None",
    ):
        if type(data) == Buffer:
            data = data.to_bytearray()
        else:
            data = Buffer.create(data).to_bytearray()

        if pad == "Zeros":
            pad_len = length - len(data)
            data.extend([0 for i in range(pad_len)])

        if endian == "<":
            data.reverse()

        for _index, _value in enumerate(data):
            self._set_pack("B", _value, offset + _index)

    def write_uint8(self, data: BufferLike, offset: int = 0):
        self._set_pack("B", data, offset)

    def write_uint16_le(self, data: BufferLike, offset: int = 0):
        self._set_pack("<H", data, offset)

    def write_uint16_be(self, data: BufferLike, offset: int = 0):
        self._set_pack(">H", data, offset)

    def write_uint32_le(self, data: BufferLike, offset: int = 0):
        self._set_pack("<I", data, offset)

    def write_uint32_be(self, data: BufferLike, offset: int = 0):
        self._set_pack(">I", data, offset)

    def write_uint64_le(self, data: BufferLike, offset: int = 0):
        self._set_pack("<Q", data, offset)

    def write_uint64_be(self, data: BufferLike, offset: int = 0):
        self._set_pack(">Q", data, offset)

    def write_bytes(
        self,
        data: BufferLike,
        length: int = 0,
        offset: int = 0,
        endian: Literal["<", ">"] = ">",
        pad: Literal["None", "Zeros"] = "None",
    ):
        if type(data) == Buffer:
            data = data.to_bytearray()
        else:
            data = Buffer.create(data).to_bytearray()

        if pad == "Zeros":
            pad_len = length - len(data)
            data.extend([0 for i in range(pad_len)])
        if endian == "<":
            data.reverse()

        for _index, _value in enumerate(data):
            self._set_pack("b", _value, offset + _index)

    def write_int8(self, data: BufferLike, offset: int):
        self._set_pack("b", data, offset)

    def write_int16_le(self, data: BufferLike, offset: int = 0):
        self._set_pack("<h", data, offset)

    def write_int16_be(self, data: BufferLike, offset: int = 0):
        self._set_pack(">h", data, offset)

    def write_int32_le(self, data: BufferLike, offset: int = 0):
        self._set_pack("<i", data, offset)

    def write_int32_be(self, data: BufferLike, offset: int = 0):
        self._set_pack(">i", data, offset)

    def write_int64_le(self, data: BufferLike, offset: int = 0):
        self._set_pack("<q", data, offset)

    def write_int64_be(self, data: BufferLike, offset: int = 0):
        self._set_pack(">q", data, offset)

    def read_ubytes(self, length: int, offset: int = 0):
        if self.read_mode == "dynamic":
            data = Buffer.create([self.read_uint8() for i in range(length)])
        else:
            data = Buffer.create([self.read_uint8(offset + i) for i in range(length)])
        return data

    def read_bytes(self, length: int, offset: int = 0):
        if self.read_mode == "dynamic":
            data = Buffer.create([self.read_int8() for i in range(length)])
        else:
            data = Buffer.create([self.read_int8(offset + i) for i in range(length)])
        return data

    def read_uint8(self, offset: int = 0) -> int:
        return self._unpack_from("B", offset)

    def read_uint16_le(self, offset: int = 0) -> int:
        return self._unpack_from("<H", offset)

    def read_uint16_be(self, offset: int = 0) -> int:
        return self._unpack_from(">H", offset)

    def read_uint32_le(self, offset: int = 0) -> int:
        return self._unpack_from("<I", offset)

    def read_uint32_be(self, offset: int = 0) -> int:
        return self._unpack_from(">I", offset)

    def read_uint64_le(self, offset: int = 0) -> int:
        return self._unpack_from("<Q", offset)

    def read_uint64_be(self, offset: int = 0) -> int:
        return self._unpack_from(">Q", offset)

    def read_int8(self, offset: int = 0) -> int:
        return self._unpack_from("b", offset)

    def read_int16_le(self, offset: int = 0) -> int:
        return self._unpack_from("<h", offset)

    def read_int16_be(self, offset: int = 0) -> int:
        return self._unpack_from(">h", offset)

    def read_int32_le(self, offset: int = 0) -> int:
        return self._unpack_from("<i", offset)

    def read_int32_be(self, offset: int = 0) -> int:
        return self._unpack_from(">i", offset)

    def read_int64_le(self, offset: int = 0) -> int:
        return self._unpack_from("<q", offset)

    def read_int64_be(self, offset: int = 0) -> int:
        return self._unpack_from(">q", offset)

    def append(self, buffer_list: BufferList):
        if self.buffer is None:
            raise Exception("buffer is None, please use create function to init")

        for buffer in buffer_list:
            self.buffer.extend(buffer.to_bytearray())

    def hex_dump(
        self,
        length: Union[int, None] = None,
        title: Union[str, None] = None,
        show_length: bool = False,
    ) -> str:
        if self.buffer is None:
            raise Exception("buffer is None, please use create function to init")

        return hex_dump(
            self.buffer, length=length, title=title, show_length=show_length
        )

    def to_bytearray(self) -> bytearray:
        if self.buffer is None:
            raise Exception("buffer is None, please use create function to init")
        return self.buffer

    def to_string(
        self, encoding: BufferEncoding = "utf-8", errors: BufferEncErrors = "strict"
    ) -> str:

        if self.buffer is None:
            raise Exception("buffer is None, please use create function to init")

        if encoding == "hex":
            return binascii.hexlify(self.buffer).decode()
        else:
            return self.buffer.decode(encoding=encoding, errors=errors)
