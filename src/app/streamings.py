from src.firebase.access import get_bucket
from src.postgres import schemas
from fastapi import APIRouter, UploadFile, File, Form
from fastapi import Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres import models
from src import roles
from src.repositories import user_utils, streaming_utils
from src.roles import get_role

router = APIRouter(tags=["streamings"])


@router.get("/streamings/", response_model=List[schemas.StreamingBase])
def get_streamings(
    pdb: Session = Depends(get_db),
):
    """Get all active streamings"""

    streamings = pdb.query(models.StreamingModel).all()

    return streamings


@router.post("/streamings/")
def post_streaming(
    name: str = Form(...),
    img: Optional[UploadFile] = File(None),
    user: models.UserModel = Depends(user_utils.retrieve_user),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
    role: roles.Role = Depends(get_role),
):
    """Create a new streaming and returns the publisher token"""

    if user.streaming is not None:
        raise HTTPException(status_code=403, detail="You already have a streaming")

    if not role.can_stream():
        raise HTTPException(
            status_code=403, detail="You don't have the permission to stream"
        )

    (
        streaming_artist_token,
        streaming_listener_token,
    ) = streaming_utils.build_streaming_tokens(user.id)

    if img is not None:
        img_url = streaming_utils.upload_img(img, user.id, bucket)
    else:
        img_url = None

    streaming = models.StreamingModel(
        name=name, listener_token=streaming_listener_token, img_url=img_url, artist=user
    )
    pdb.add(streaming)
    pdb.commit()

    return streaming_artist_token


@router.delete("/streamings/")
def delete_streaming(
    user: models.UserModel = Depends(user_utils.retrieve_user),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Delete a streaming"""
    streaming = user.streaming

    if streaming is None:
        raise HTTPException(status_code=404, detail="You don't have a streaming")

    if streaming.img_url is not None:
        streaming_utils.delete_img(user.id, bucket)

    pdb.delete(user.streaming)
    pdb.commit()
