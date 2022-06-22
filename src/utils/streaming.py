import datetime
from agora_token_builder import RtcTokenBuilder
from src.constants import AGORA_APP_ID, AGORA_APP_CERT

ROLE_PUBLISHER = 1
ROLE_SUBSCRIBER = 2
TOKEN_VALIDITY_TIME = datetime.timedelta(hours=10)


def build_streaming_tokens(channel_name: str) -> [str, str]:

    now = datetime.datetime.now()
    timestamp = (now + TOKEN_VALIDITY_TIME).timestamp()

    streaming_artist_token = RtcTokenBuilder.buildTokenWithUid(
        AGORA_APP_ID, AGORA_APP_CERT, channel_name, 0, ROLE_PUBLISHER, timestamp
    )
    streaming_listener_token = RtcTokenBuilder.buildTokenWithUid(
        AGORA_APP_ID, AGORA_APP_CERT, channel_name, 0, ROLE_SUBSCRIBER, timestamp
    )

    return streaming_artist_token, streaming_listener_token
