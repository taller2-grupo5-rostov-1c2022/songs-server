from src.exceptions import MessageException

from sqlalchemy.orm import Session
from src.database.access import Base
from fastapi import status
from sqlalchemy.orm.query import Query

from src.schemas.pagination import CustomPage


class CRUDMixin(Base):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    __abstract__ = True

    @classmethod
    def create(cls, pdb: Session, **kwargs):
        """Create a new record and save it the database."""
        commit = kwargs.get("commit", True)
        instance = cls(**kwargs)
        return instance.save(pdb, commit=commit)

    @classmethod
    def get(cls, pdb: Session, _id, raise_if_not_found=True, **kwargs):
        """Get a record by its id."""
        item = pdb.query(cls).get(_id)
        if item is None and raise_if_not_found:
            raise MessageException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item of {cls.__name__} with id {_id} not found",
            )
        return item

    @classmethod
    def get_many(cls, pdb: Session, *args, **kwargs):
        ids = kwargs.pop("ids")
        items = pdb.query(cls).filter(cls.id.in_(ids)).all()
        if len(items) != len(ids):
            raise MessageException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Some items of {cls.__name__} not found",
            )
        return items

    @classmethod
    def search(cls, pdb: Session, **kwargs):
        """Search for records."""
        query: Query = kwargs.pop("query", None)

        do_pagination = kwargs.pop("do_pagination", True)
        if query is None:
            query = pdb.query(cls)
        if not do_pagination:
            total = query.count()
            items = query.all()
            offset = 0
            limit = total
            return CustomPage(items, offset, limit, total)

        total = query.count()
        limit = kwargs.pop("limit")
        offset = kwargs.pop("offset")
        if offset is None:
            items = query.order_by(cls.id).limit(limit).all()
        else:
            items = query.order_by(cls.id).filter(cls.id > offset).limit(limit).all()
        offset = items[-1].id if items else None

        page = CustomPage(items=items, total=total, limit=limit, offset=offset)
        return page

    def update(self, pdb: Session, **kwargs):
        """Update specific fields of a record."""
        commit = kwargs.pop("commit", True)
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save(pdb) or self

    def save(self, pdb: Session, commit: bool = True):
        """Save the record."""
        pdb.add(self)
        if commit:
            pdb.commit()
        else:
            pdb.flush()
            pdb.refresh(self)
        return self

    def delete(self, pdb: Session, **kwargs):
        """Remove the record from the database."""
        commit = kwargs.pop("commit", True)
        pdb.delete(self)
        return commit and pdb.commit()

    def expire(self, pdb: Session):
        """Expire the record."""
        pdb.expire(self)

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
