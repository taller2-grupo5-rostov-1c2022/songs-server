from tests import utils
from src.main import API_VERSION_PREFIX


def test_get_albums_first_page(client, custom_requests_mock, drop_tables):
    utils.post_album(client, name="album_1")
    utils.post_album(client, name="album_2")

    response_get = utils.search_albums(client, offset=0, limit=1)

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_1"


def test_get_albums_second_page(client, custom_requests_mock, drop_tables):
    utils.post_album(client, name="album_1")
    utils.post_album(client, name="album_2")

    response_get = utils.search_albums(client, offset=1, limit=1)

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_get_albums_page_bigger_than_total(client, custom_requests_mock, drop_tables):
    utils.post_album(client, name="album_1")
    utils.post_album(client, name="album_2")

    response_get = utils.search_albums(
        client, offset=2, limit=1
    )

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 0


def test_get_albums_size_bigger_than_total(client, custom_requests_mock, drop_tables):
    utils.post_album(client, name="album_1")
    utils.post_album(client, name="album_2")

    response_get = utils.search_albums(
        client, offset=0, limit=2
    )

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 2
    assert albums[0]["name"] == "album_1"
    assert albums[1]["name"] == "album_2"


def test_get_albums_with_songs_first_page(client, custom_requests_mock, drop_tables):
    song_id_1 = utils.post_song(client, name="song_1")
    song_id_2 = utils.post_song(client, name="song_2")
    song_id_3 = utils.post_song(client, name="song_3")

    utils.post_album(client, name="album_1", songs_ids=[song_id_1, song_id_2])
    utils.post_album(client, name="album_2", songs_ids=[song_id_3])

    response_get = utils.search_albums(
        client, offset=0, limit=1
    )

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_1"


def test_get_albums_with_songs_second_page(client, custom_requests_mock, drop_tables):
    song_id_1 = utils.post_song(client, name="song_1")
    song_id_2 = utils.post_song(client, name="song_2")
    song_id_3 = utils.post_song(client, name="song_3")

    utils.post_album(client, name="album_1", songs_ids=[song_id_1, song_id_2])
    utils.post_album(client, name="album_2", songs_ids=[song_id_3])

    response_get = utils.search_albums(
        client, offset=1, limit=1
    )

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_get_my_albums_first_page(client, custom_requests_mock, drop_tables):
    utils.post_album(client, name="album_1")
    utils.post_album(client, name="album_2")

    response_get = utils.search_albums(
        client, offset=0, limit=1
    )

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_1"


def test_get_my_albums_second_page(client, custom_requests_mock, drop_tables):
    utils.post_album(client, name="album_1")
    utils.post_album(client, name="album_2")

    response_get = utils.search_albums(
        client, offset=1, limit=1
    )

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_get_playlists_first_page(client, custom_requests_mock, drop_tables):
    utils.post_playlist(client, playlist_name="playlist_1")
    utils.post_playlist(client, playlist_name="playlist_2")

    response_get = utils.search_playlists(
        client, offset=0, limit=1
    )

    playlists = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_1"


def test_get_playlists_second_page(client, custom_requests_mock, drop_tables):
    utils.post_playlist(client, playlist_name="playlist_1")
    utils.post_playlist(client, playlist_name="playlist_2")

    response_get = utils.search_playlists(
        client, offset=1, limit=1
    )

    playlists = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_2"


def test_get_my_playlists_first_page(client, custom_requests_mock, drop_tables):
    utils.post_playlist(client, playlist_name="playlist_1")
    utils.post_playlist(client, playlist_name="playlist_2")

    response_get = utils.search_playlists(
        client, offset=0, limit=1
    )

    playlists = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_1"


def test_get_my_playlists_second_page(client, custom_requests_mock, drop_tables):
    utils.post_playlist(client, playlist_name="playlist_1")
    utils.post_playlist(client, playlist_name="playlist_2")

    response_get = utils.search_playlists(
        client, offset=1, limit=1
    )

    playlists = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_2"


def test_get_playlists_with_songs_first_page(client, custom_requests_mock, drop_tables):
    song_id_1 = utils.post_song(client, name="song_1")
    song_id_2 = utils.post_song(client, name="song_2")
    song_id_3 = utils.post_song(client, name="song_3")

    utils.post_playlist(
        client, playlist_name="playlist_1", songs_ids=[song_id_1, song_id_2]
    )
    utils.post_playlist(client, playlist_name="playlist_2", songs_ids=[song_id_3])

    response_get = utils.search_playlists(
        client, offset=0, limit=1
    )

    playlists = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_1"


def test_get_playlists_with_songs_second_page(
    client, custom_requests_mock, drop_tables
):
    song_id_1 = utils.post_song(client, name="song_1")
    song_id_2 = utils.post_song(client, name="song_2")
    song_id_3 = utils.post_song(client, name="song_3")

    utils.post_playlist(
        client, playlist_name="playlist_1", songs_ids=[song_id_1, song_id_2]
    )
    utils.post_playlist(client, playlist_name="playlist_2", songs_ids=[song_id_3])

    response_get = utils.search_playlists(
        client, offset=1, limit=1
    )

    playlists = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_2"


def test_get_songs_first_page(client, custom_requests_mock, drop_tables):
    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2")

    response_get = utils.search_songs(
        client, offset=0, limit=1
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_songs_second_page(client, custom_requests_mock, drop_tables):
    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2")

    response_get = utils.search_songs(
        client, offset=1, limit=1
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_2"


def test_get_songs_filtered_by_name_first_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_song(client, name="foo")
    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2")

    response_get = utils.search_songs(
        client, offset=0, limit=1, name="song_1"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_songs_filtered_by_name_second_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_song(client, name="foo")
    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2")

    response_get = utils.search_songs(
        client, offset=2, limit=1, name="song"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_2"


def test_get_albums_filtered_by_artist_first_page(
    client, custom_requests_mock, drop_tables
):
    song_id_1 = utils.post_song(client, name="song_1", artists=["foo"])
    song_id_2 = utils.post_song(
        client, name="song_2", artists=["artist_1"]
    )
    song_id_3 = utils.post_song(
        client, name="song_2", artists=["artist_1"]
    )

    utils.post_album(client, name="album_1", songs_ids=[song_id_1, song_id_2])
    utils.post_album(client, name="album_2", songs_ids=[song_id_3])

    response_get = utils.search_albums(
        client, offset=0, limit=1, artist="artist_1"
    )

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_1"


def test_get_albums_filtered_by_artist_second_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_user(client, "user_id")

    song_id_1 = utils.post_song(client, name="song_1", artists=["foo"])
    song_id_2 = utils.post_song(
        client, name="song_2", artists=["artist_1"]
    )
    song_id_3 = utils.post_song(
        client, name="song_2", artists=["artist_1"]
    )

    utils.post_album(client, name="album_1", songs_ids=[song_id_1, song_id_2])
    utils.post_album(client, name="album_2", songs_ids=[song_id_3])

    response_get = utils.search_albums(
        client, offset=1, limit=1, artist="artist_1"
    )

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_get_playlists_filtered_by_colab_first_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_users(client, "user_playlist_owner", "user_playlist_colab", "foo_id")

    utils.post_playlist(client, "user_playlist_owner", "playlist_1")
    utils.post_playlist(
        client, "user_playlist_owner", "playlist_2", colabs_ids=["user_playlist_colab"]
    )
    utils.post_playlist(
        client, "user_playlist_owner", "playlist_3", colabs_ids=["user_playlist_colab"]
    )

    response_get = utils.search_playlists(
        client, offset=0, limit=1, colab="user_playlist_colab"
    )

    playlists = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_2"


def test_get_playlists_filtered_by_colab_second_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_users(client, "user_playlist_owner", "user_playlist_colab", "foo_id")

    utils.post_playlist(client, "user_playlist_owner", "playlist_1")
    utils.post_playlist(
        client, "user_playlist_owner", "playlist_2", colabs_ids=["user_playlist_colab"]
    )
    utils.post_playlist(
        client, "user_playlist_owner", "playlist_3", colabs_ids=["user_playlist_colab"]
    )

    response_get = utils.search_playlists(
        client, offset=2, limit=1, colab="user_playlist_colab"
    )

    playlists = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_3"


def test_get_songs_with_blocked_songs_first_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_user(client, "user_id")

    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2", blocked=True)
    utils.post_song(client, name="song_3")

    response_get = utils.search_songs(
        client, offset=0, limit=1, uid="user_id"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_songs_with_blocked_songs_second_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_user(client, "user_id")

    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2", blocked=True)
    utils.post_song(client, name="song_3")

    response_get = utils.search_songs(
        client, offset=1, limit=1, uid="user_id"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_3"


def test_get_my_songs_first_page(client, custom_requests_mock, drop_tables):
    utils.post_user(client, "user_id")

    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2")
    utils.post_song(client, name="song_3")

    response_get = utils.search_songs(
        client, offset=0, limit=1, uid="user_id"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_my_songs_second_page(client, custom_requests_mock, drop_tables):
    utils.post_user(client, "user_id")

    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2")
    utils.post_song(client, name="song_3")

    response_get = utils.search_songs(
        client, offset=1, limit=1, uid="user_id"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_2"


def test_get_my_songs_with_own_blocked_songs_first_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_user(client, "user_id")

    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2", blocked=True)
    utils.post_song(client, name="song_3")

    response_get = utils.search_songs(
        client, offset=0, limit=1, uid="user_id"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_my_songs_with_blocked_songs_second_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_user(client, "user_id")

    utils.post_song(client, name="song_1")
    utils.post_song(client, name="song_2", blocked=True)
    utils.post_song(client, name="song_3")

    response_get = utils.search_songs(
        client, offset=1, limit=1, uid="user_id"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_3"


def test_get_my_songs_with_blocked_songs_of_another_user_first_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_user(client, "user_id")
    utils.post_user(client, "user_id_2", "user_name_2")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id_2", "song_2", blocked=True)
    utils.post_song(client, "user_id", "song_3")

    response_get = utils.get_my_songs(
        client, offset=0, limit=1, uid="user_id"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_my_songs_with_blocked_songs_of_another_user_second_page(
    client, custom_requests_mock, drop_tables
):
    utils.post_user(client, "user_id")
    utils.post_user(client, "user_id_2", "user_name_2")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id_2", "song_2", blocked=True)
    utils.post_song(client, "user_id", "song_3")

    response_get = utils.get_my_songs(
        client, offset=1, limit=1, uid="user_id"
    )

    songs = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_3"


def test_get_albums_filtered_by_artist_name_second_page(
    client, custom_requests_mock, drop_tables
):
    song_id_1 = utils.post_song(client, name="song_1", artists=["artist"])
    song_id_2 = utils.post_song(client, name="song_2", artists=["artist"])

    utils.post_album(client, name="album_1", songs_ids=[song_id_1])
    utils.post_album(client, name="album_2", songs_ids=[song_id_2])

    response_get = utils.search_albums(
        client, offset=1, limit=1, artist="artist"
    )

    albums = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_get_comments_of_album_first_page(client, custom_requests_mock, drop_tables):
    album_id_1 = utils.post_album(client)

    comment_id = utils.post_comment(client, album_id_1, "comment_1")
    utils.post_comment(client, album_id_1, "child_comment", parent_id=comment_id)
    utils.post_comment(client, album_id_1, "comment_2")

    response_get = utils.get_album_comments(
        client, album_id_1, offset=0, limit=1
    )

    comments = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] == "comment_1"


def test_get_comments_of_album_second_page(client, custom_requests_mock, drop_tables):
    album_id_1 = utils.post_album(client)

    comment_id = utils.post_comment(client, album_id_1, "comment_1")
    utils.post_comment(client, album_id_1, "child_comment", parent_id=comment_id)
    utils.post_comment(client, album_id_1, "comment_2")

    response_get = utils.get_album_comments(
        client, album_id_1, offset=1, limit=1
    )

    comments = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] == "comment_2"


def test_get_comments_of_album_bigger_limit(client, custom_requests_mock, drop_tables):
    utils.post_user(client, "user_id")

    album_id_1 = utils.post_album(client)

    comment_id = utils.post_comment(client, album_id_1, "comment_1")

    utils.post_comment(client, album_id_1, "child_comment", parent_id=comment_id)
    utils.post_comment(client, album_id_1, "comment_2")

    response_get = utils.get_album_comments(
        client, album_id_1, offset=0, limit=2
    )

    comments = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(comments) == 2
    assert comments[0]["text"] == "comment_1"
    assert comments[1]["text"] == "comment_2"


def test_get_reviews_of_album_first_page(client, custom_requests_mock, drop_tables):
    utils.post_users(client, "user_id_1", "user_id_2")

    album_id_1 = utils.post_album(client)

    utils.post_review(client, album_id_1, "user_id_1", "review_1")
    utils.post_review(client, album_id_1, "user_id_2", "review_2")

    response_get = utils.get_reviews_of_album(
        client, album_id_1, offset=None, limit=1
    )

    reviews = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(reviews) == 1
    assert reviews[0]["text"] == "review_1"


def test_get_reviews_of_album_second_page(client, custom_requests_mock, drop_tables):
    utils.post_user(client, "user_id_1")
    utils.post_user(client, "user_id_2")

    album_id_1 = utils.post_album(client, name="album_1")

    utils.post_review(client, album_id_1, "user_id_1", "review_1")
    utils.post_review(client, album_id_1, "user_id_2", "review_2")

    response_get = utils.get_reviews_of_album(
        client, album_id_1, offset="user_id_1", limit=1
    )

    reviews = response_get.json()["items"]
    assert response_get.status_code == 200
    assert len(reviews) == 1
    assert reviews[0]["text"] == "review_2"
