
import jwt
from datetime import datetime, timedelta
from django.conf import settings

from login.models import users

def create_jwt_pair_for_user(user: users):
    expiration_time = datetime.utcnow() + timedelta(hours=3)
    payload = {
        "token_type": "access",
        "exp": expiration_time,
        "iat": datetime.utcnow(),
        "jti": str(user.id_user),
        "user_id": user.id_user,
        "station_name": user.station.station_name,
        "station_id": user.station.id_station,
        "country": user.station.country,
    }

    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    tokens = {
        "token": access_token,
         }
    return tokens