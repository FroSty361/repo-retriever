import base64
import zlib

def encode_string(s: str) -> str:
    string_bytes = s.encode('utf-8')

    string_encoded_bytes = base64.b64encode(string_bytes)

    return string_encoded_bytes.decode('utf-8')

def decode_string(s: str) -> str:
    string_bytes = s.encode('utf-8')

    decoded_bytes = base64.b64decode(string_bytes)

    return decoded_bytes.decode('utf-8')

def encode_url_string(s: str) -> str:
    string_bytes = s.encode('utf-8')

    string_encoded_bytes = base64.urlsafe_b64encode(string_bytes)

    return string_encoded_bytes.decode('utf-8')

def decode_url_string(s: str) -> str:
    string_bytes = s.encode('utf-8')

    string_encoded_bytes = base64.urlsafe_b64decode(string_bytes)

    return string_encoded_bytes.decode('utf-8')

def encode_and_compress_url_string(s: str) -> str:
    string_compressed_bytes = zlib.compress(s.encode('utf-8'), 9)

    string_encoded_bytes = base64.urlsafe_b64encode(string_compressed_bytes)

    return string_encoded_bytes.decode('utf-8').rstrip("=")


def decode_and_decompress_url_string(encoded_s: str) -> str:
    padding = len(encoded_s) % 4

    if padding:
        encoded_s += "=" * (4 - padding)

    string_compressed_bytes = base64.urlsafe_b64decode(encoded_s.encode('utf-8'))

    string_bytes = zlib.decompress(string_compressed_bytes)

    return string_bytes.decode('utf-8')