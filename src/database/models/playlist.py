from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship, Session, contains_eager
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import or_
from fastapi import HTTPException, status
from . import templates, tables
from .song import SongModel
from .user import UserModel
from ... import roles


class PlaylistModel(templates.ResourceModel):
    __tablename__ = "playlists"

    songs = relationship(
        "SongModel",
        secondary=tables.song_playlist_association_table,
    )

    colabs = relationship(
        "UserModel",
        secondary=tables.colab_playlist_association_table,
        back_populates="other_playlists",
    )
    creator = relationship("UserModel", back_populates="my_playlists")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    favorited_by = relationship(
        "UserModel",
        secondary=tables.playlist_favorite_association_table,
        back_populates="favorite_playlists",
    )

    @classmethod
    def create(cls, pdb: Session, *args, **kwargs):
        creator_id = kwargs.pop("creator_id")
        songs_ids = kwargs.pop("songs_ids")
        colabs_ids = kwargs.pop("colabs_ids")
        role = kwargs.pop("role")

        songs = SongModel.get_many(pdb, ids=songs_ids, role=role)
        colabs = UserModel.get_many(pdb, ids=colabs_ids)
        playlist = super().create(
            pdb,
            creator_id=creator_id,
            songs=songs,
            colabs=colabs,
            **kwargs,
        )
        return playlist

    @classmethod
    def search(cls, pdb: Session, **kwargs):
        query: Query = kwargs.pop("query", None)
        role: roles.Role = kwargs.get("role")
        colab = kwargs.pop("colab", None)

        join_conditions = []
        if query is None:
            query = pdb.query(cls)

        if colab is not None:
            query = query.filter(or_(UserModel.id == colab, cls.creator_id == colab))

        if not role.can_see_blocked():
            join_conditions.append(SongModel.blocked == False)

        query = (
            query.options(contains_eager("songs"))
            .join(cls.songs.and_(*join_conditions), isouter=True)
            .join(cls.colabs, isouter=True)
        )

        return super().search(pdb, query=query, **kwargs)

    @classmethod
    def get(cls, pdb: Session, *args, **kwargs):
        role = kwargs.get("role")
        playlist_id = kwargs.get("_id")

        join_conditions = []
        filters = [playlist_id == cls.id]

        if not role.can_see_blocked():
            join_conditions.append(SongModel.blocked == False)
            filters.append(cls.blocked == False)

        playlists = (
            pdb.query(cls)
            .options(contains_eager("songs"))
            .join(cls.songs.and_(*join_conditions), isouter=True)
            .filter(*filters)
            .all()
        )
        if len(playlists) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found"
            )
        return playlists[0]

    def add_song(self, pdb: Session, song: SongModel):
        if song not in self.songs:
            self.songs.append(song)
            self.save(pdb)
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Song already in playlist"
            )

    def remove_song(self, pdb: Session, song: SongModel):
        if song in self.songs:
            self.songs.remove(song)
            self.save(pdb)
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Song not in playlist"
            )

    def add_colab(self, pdb: Session, colab: UserModel):
        if colab not in self.colabs:
            self.colabs.append(colab)
            self.save(pdb)
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Colab already in playlist"
            )

    def remove_colab(self, pdb: Session, colab: UserModel):
        if colab in self.colabs:
            self.colabs.remove(colab)
            self.save(pdb)
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Colab not in playlist"
            )
