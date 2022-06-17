from src.firebase.access import get_bucket
from src.database.access import get_db
from fastapi import APIRouter, UploadFile, File, Form
from fastapi import Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database import models, crud
from src import roles, utils, schemas
from src.roles import get_role

router = APIRouter(tags=["streamings"])


@router.get("/streamings/", response_model=List[schemas.StreamingBase])
def get_streamings(
    pdb: Session = Depends(get_db),
):
    """Get all active streamings"""

    return crud.streaming.get_streamings(pdb)


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

    if user.streaming is not None:
        raise HTTPException(status_code=403, detail="You already have a streaming")

    if not role.can_stream():
        raise HTTPException(
            status_code=403, detail="You don't have the permission to stream"
        )

    (
        streaming_artist_token,
        streaming_listener_token,
    ) = utils.streaming.build_streaming_tokens(user.id)

    if img is not None:
        img_url = utils.streaming.upload_img(img, user.id, bucket)
    else:
        img_url = None

    crud.streaming.create_streaming(pdb, name, img_url, user, streaming_listener_token)

    return streaming_artist_token


@router.delete("/streamings/")
def delete_streaming(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Delete a streaming"""
    streaming = user.streaming

    if streaming is None:
        raise HTTPException(status_code=404, detail="You don't have a streaming")

    if streaming.img_url is not None:
        utils.streaming.delete_img(user.id, bucket)

    crud.streaming.delete_streaming(pdb, streaming)
