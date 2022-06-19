from .resource import ResourceBase, ResourceUpdate
from .resource_creator import ResourceCreatorBase, ResourceCreatorUpdate
from .song import SongBase, SongUpdate, SongGet, SongPost, SongUpdateFile
from .album import AlbumBase, AlbumUpdate, AlbumGet, Album, AlbumPost, AlbumUpdateCover
from .user import UserBase, User, UserUpdate, UserUpdateSub, UserPost, UserPostComplete
from .comment import CommentGet, CommentPost, CommentUpdate
from .artist import ArtistBase
from .review import ReviewBase, ReviewGet, ReviewUpdate, ReviewMyReviews
from .playlist import PlaylistBase, PlaylistUpdate, PlaylistPost, PlaylistGet
from .streaming import StreamingBase
from .subscription import SubscriptionBase
