from fastapi import Form, Depends, HTTPException, Header

from src import roles
from src.database import models
from typing import Optional
from src.postgres import schemas
from src.postgres.database import get_db


def retrieve_resource_update(
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    blocked: Optional[bool] = Form(None),
):
    return schemas.ResourceUpdate(name=name, description=description, blocked=blocked)


def retrieve_resource(
    name: str = Form(...),
    description: str = Form(...),
    uid: str = Header(...),
    pdb=Depends(get_db),
):
    if pdb.get(models.UserModel, uid) is None:
        raise HTTPException(status_code=404, detail=f"User with id {uid} not found")

    return schemas.ResourceBase(
        name=name, description=description, blocked=False, creator_id=uid
    )


def retrieve_resource_creator_update(
    resource_update: schemas.ResourceUpdate = Depends(retrieve_resource_update),
    genre: Optional[str] = Form(None),
):
    return schemas.ResourceCreatorUpdate(genre=genre, **resource_update.dict())


def retrieve_resource_creator(
    resource: schemas.ResourceBase = Depends(retrieve_resource),
    genre: str = Form(...),
    role: roles.Role = Depends(roles.get_role),
):
    if not role.can_post_content():
        raise HTTPException(
            status_code=403, detail="You are not allowed to post content"
        )

    return schemas.ResourceCreatorBase(genre=genre, **resource.dict())
