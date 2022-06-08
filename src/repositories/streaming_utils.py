import datetime
from fastapi import UploadFile, HTTPException
from src.constants import SUPPRESS_BLOB_ERRORS
from agora_token_builder import RtcTokenBuilder
from src.constants import AGORA_APP_ID, AGORA_APP_CERT

ROLE_PUBLISHER = 1
ROLE_SUBSCRIBER = 2
TOKEN_VALIDITY_TIME = datetime.timedelta(hours=10)


def build_streaming_tokens(channel_name: str):

    now = datetime.datetime.now()
    timestamp = (now + TOKEN_VALIDITY_TIME).timestamp()

    streaming_artist_token = RtcTokenBuilder.buildTokenWithUid(
        AGORA_APP_ID, AGORA_APP_CERT, channel_name, 0, ROLE_PUBLISHER, timestamp
    )
    streaming_listener_token = RtcTokenBuilder.buildTokenWithUid(
        AGORA_APP_ID, AGORA_APP_CERT, channel_name, 0, ROLE_SUBSCRIBER, timestamp
    )

    return streaming_artist_token, streaming_listener_token


def upload_img(img: UploadFile, img_id: str, bucket):
    try:
        blob = bucket.blob("streaming_imgs/" + str(img_id))
        blob.upload_from_file(img.file)
        blob.make_public()
        return blob.public_url
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507,
                detail=f"Could not upload img for streaming: {entry_not_found}",
            ) from entry_not_found


def delete_img(img_id: str, bucket):
    try:
        blob = bucket.blob("streaming_imgs/" + str(img_id))
        blob.delete()
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507,
                detail=f"Could not delete img for streaming: {entry_not_found}",
            ) from entry_not_found
