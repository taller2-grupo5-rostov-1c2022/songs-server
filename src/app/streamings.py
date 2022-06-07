import datetime
from src.postgres import schemas
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres import models
from src import roles
from src.repositories import user_utils
from src.roles import get_role
from agora_token_builder import RtcTokenBuilder
from src.constants import AGORA_APP_ID, AGORA_APP_CERT

ROLE_PUBLISHER = 1
ROLE_SUBSCRIBER = 2
TOKEN_VALIDITY_TIME = datetime.timedelta(hours=10)

router = APIRouter(tags=["streamings"])


@router.get("/streamings/", response_model=List[schemas.StreamingBase])
def get_streamings(
    pdb: Session = Depends(get_db),
):
    """Get all active streamings"""

    users_with_streamings = (
        pdb.query(models.UserModel)
        .filter(models.UserModel.streaming_listener_token.isnot(None))
        .all()
    )
    return users_with_streamings


@router.post("/streamings/")
def post_streaming(
    user: models.UserModel = Depends(user_utils.retrieve_user),
    pdb: Session = Depends(get_db),
    role: roles.Role = Depends(get_role),
):
    """Create a new streaming and returns the publisher token"""

    if user.streaming_listener_token is not None:
        raise HTTPException(status_code=403, detail="You already have a streaming")

    if not role.can_stream():
        raise HTTPException(
            status_code=403, detail="You don't have the permission to stream"
        )

    now = datetime.datetime.now()
    timestamp = (now + TOKEN_VALIDITY_TIME).timestamp()

    streaming_artist_token = RtcTokenBuilder.buildTokenWithUid(
        AGORA_APP_ID, AGORA_APP_CERT, user.id, user.id, ROLE_PUBLISHER, timestamp
    )
    user.streaming_listener_token = RtcTokenBuilder.buildTokenWithUid(
        AGORA_APP_ID, AGORA_APP_CERT, user.id, user.id, ROLE_SUBSCRIBER, timestamp
    )

    pdb.commit()

    return streaming_artist_token


@router.delete("/streamings/")
def delete_streaming(
    user: models.UserModel = Depends(user_utils.retrieve_user),
    pdb: Session = Depends(get_db),
):
    """Delete a streaming"""
    user.streaming_listener_token = None
    pdb.commit()
