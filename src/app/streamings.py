from src.exceptions import MessageException
from src.firebase.access import get_bucket
from src.database.access import get_db
from fastapi import APIRouter, UploadFile, File, Form
from fastapi import Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from src.database import models
from src import roles, utils, schemas
from src.roles import get_role

from src.schemas.pagination import CustomPage

router = APIRouter(tags=["streamings"])


@router.get("/streamings/", response_model=CustomPage[schemas.StreamingBase])
def get_streamings(
    pdb: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all active streamings"""

    return models.StreamingModel.search(
        pdb, limit=limit, offset=offset, do_pagination=False
    )


@router.post("/streamings/")
def post_streaming(
    name: str = Form(...),
    img: Optional[UploadFile] = File(None),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
    role: roles.Role = Depends(get_role),
):
    """Create a new streaming and returns the publisher token"""

    if not role.can_stream():
        raise MessageException(
            status_code=403, detail="You don't have the permission to stream"
        )

    if user.streaming:
        raise MessageException(status_code=403, detail="You already have a streaming")

    (artist_token, listener_token) = utils.streaming.build_streaming_tokens(user.id)

    if img is not None:
        models.StreamingModel.create(
            pdb,
            name=name,
            img=img.file,
            artist=user,
            bucket=bucket,
            listener_token=listener_token,
        )
    else:
        models.StreamingModel.create(
            pdb, name=name, artist=user, listener_token=listener_token
        )
    return artist_token


@router.delete("/streamings/")
def delete_streaming(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Delete a streaming"""
    streaming = user.streaming

    if streaming is None:
        raise MessageException(status_code=404, detail="You don't have a streaming")

    streaming.delete(pdb, bucket=bucket)
