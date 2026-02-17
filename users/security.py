from django.core import signing
from datetime import timedelta

TOKEN_AGE = 60 * 60 * 24 * 7  # 7 días

def create_user_token(user):
    data = {
        "user_id": user.id,
        "username": user.username,
    }
    return signing.dumps(data)

def decode_user_token(token):
    try:
        return signing.loads(token, max_age=TOKEN_AGE)
    except signing.BadSignature:
        return None
    except signing.SignatureExpired:
        return None
