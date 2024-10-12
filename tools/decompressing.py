import base64
import gzip
from Crypto.Cipher import AES

def compress(x: bytes) -> bytes:
    return b'H4sIAAAAAAAAC' + base64.b64encode(gzip.compress(x)).replace(b'+', b'-').replace(b'/', b'_')[13:]

def decompress(x: bytes) -> bytes:
    return gzip.decompress(base64.b64decode(b'H4sIAKeEmGIC/' + x[13:].replace(b'-', b'+').replace(b'_', b'/')))

def _xor_bytes(data: bytes, value: int) -> bytes:
    return bytes(map(lambda x: x ^ value, data))

def _remove_pad(save: bytes) -> bytes:
    pad = save[-1]
    if pad <= 16:
        return save[:-pad]
    return save

def decrypt_save_xml(data: bytes) -> bytes:
    # thanks https://github.com/Wyliemaster/GD-Save-Decryptor/blob/main/saves.py
    if data[0] == 67:
        return decompress(_xor_bytes(data, 11))
    cipher = AES.new(b'ipu9TUv54yv]isFMh5@;t.5w34E2Ry@{', AES.MODE_ECB)
    return _remove_pad(cipher.decrypt(data))

def encrypt_save_xml(data: bytes, ios_mode: bool = False) -> bytes:
    if not ios_mode:
        return _xor_bytes(compress(data), 11)
    cipher = AES.new(b'ipu9TUv54yv]isFMh5@;t.5w34E2Ry@{', AES.MODE_ECB)
    pad = ((-len(data) - 1) % 16) + 1
    return cipher.encrypt(data + bytes((pad,)) * pad)
