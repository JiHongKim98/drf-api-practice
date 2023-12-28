from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


def encode_uid(uid) -> str:
    """
    사용자의 고유 식별자(uid)를 받아 URL-safe한 형태로 인코딩
    """

    return urlsafe_base64_encode(force_bytes(uid))

def decode_uid(uidb64) -> int|None:
    """
    URL-safe한 문자열로 인코딩된 사용자의 식별자(uid)를 디코딩
    """

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return int(uid)
    
    except (ValueError, TypeError):
        return None

