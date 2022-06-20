import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP
from typing.io import IO

from src import roles
from src.constants import SUPPRESS_BLOB_ERRORS
from src.database.models.crud_template import CRUDMixin
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.orm.query import Query


class ResourceModel(CRUDMixin):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    blocked = Column(Boolean, nullable=False, index=True)

    @classmethod
    def create(cls, pdb: Session, **kwargs):
        name = kwargs.pop("name")
        description = kwargs.pop("description")
        blocked = kwargs.pop("blocked")
        creator_id = kwargs.pop("creator_id")
        return super().create(
            pdb,
            name=name,
            description=description,
            blocked=blocked,
            creator_id=creator_id,
            **kwargs,
        )

    @classmethod
    def get(cls, pdb: Session, *args, **kwargs):
        role: roles.Role = kwargs.pop("role")
        resource = super().get(pdb, *args, **kwargs)
        if resource.blocked and not role.can_see_blocked():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
            )
        return resource

    @classmethod
    def get_many(cls, pdb: Session, *args, **kwargs):
        role: roles.Role = kwargs.pop("role")
        resources = super().get_many(pdb, *args, **kwargs)
        if not role.can_see_blocked():
            for resource in resources:
                if resource.blocked:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Resource not found",
                    )
        return resources

    @classmethod
    def search(cls, pdb: Session, **kwargs):
        query: Query = kwargs.pop("query", None)
        if not query:
            query = pdb.query(cls)

        name = kwargs.pop("name", None)
        role: roles.Role = kwargs.pop("role")
        creator_id = kwargs.pop("creator_id", None)

        if not role.can_see_blocked():
            query = query.filter(cls.blocked == False)
        if name is not None:
            query = query.filter(cls.name.ilike(f"%{name}%"))
        if creator_id is not None:
            query = query.filter(cls.creator_id == creator_id)
        query = query.order_by(cls.id)

        return super().search(pdb, query=query, **kwargs)

    def update(self, pdb: Session, **kwargs):
        blocked = kwargs.get("blocked", None)
        role: roles.Role = kwargs.pop("role")
        if blocked is not None and not role.can_block():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to block this resource",
            )
        return super().update(pdb, **kwargs)


class ResourceCreatorModel(ResourceModel):
    __abstract__ = True
    genre = Column(String, nullable=False, index=True)

    @classmethod
    def search(cls, pdb: Session, **kwargs):
        query: Query = kwargs.pop("query", None)
        if not query:
            query = pdb.query(cls)

        genre = kwargs.pop("genre", None)
        if genre is not None:
            query = query.filter(cls.genre.ilike(f"%{genre}%"))

        return super().search(pdb, query=query, **kwargs)


class ResourceWithFile(ResourceCreatorModel):
    __abstract__ = True

    file_last_update = Column(TIMESTAMP, nullable=False)

    def upload_file(self, pdb: Session, file: IO, bucket):
        try:
            blob = bucket.blob(f"{self.__tablename__}/{self.id}")
            blob.upload_from_file(file)
            blob.make_public()

        except Exception as e:
            if not SUPPRESS_BLOB_ERRORS:
                self.expire(pdb)
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=f"Could not upload file for for resource {self.__class__.name} with id {self.id}: {e}",
                )

    def delete_file(self, bucket):
        try:
            blob = bucket.blob(f"{self.__tablename__}/{self.id}")
            blob.delete()
        except Exception as e:
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=f"Could not delete file for for resource {self.__class__.name} with id {self.id}: {e}",
                )

    @classmethod
    def create(cls, pdb: Session, **kwargs):
        file_last_update = datetime.datetime.now()
        bucket = kwargs.pop("bucket")
        file = kwargs.pop("file")
        commit = kwargs.pop("commit", True)

        resource = super().create(
            pdb, file_last_update=file_last_update, commit=False, **kwargs
        )
        resource.upload_file(pdb, file, bucket)
        resource.save(pdb, commit=commit)
        return resource

    def update(self, pdb: Session, **kwargs):
        file: Optional[IO] = kwargs.pop("file", None)
        if file is not None:
            bucket = kwargs.pop("bucket")
            self.file_last_update = datetime.datetime.now()
            self.upload_file(pdb, file, bucket)
        return super().update(pdb, **kwargs)

    def delete(self, pdb: Session, **kwargs):
        bucket = kwargs.get("bucket")
        self.delete_file(bucket)

        return super().delete(pdb, **kwargs)
