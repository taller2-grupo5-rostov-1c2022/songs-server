from src.main import API_VERSION_PREFIX
from tests import utils


def test_get_all_comments_of_album_without_comments(client, custom_requests_mock):
    album_id = utils.post_album(client)

    response_get = utils.get_album_comments(client, album_id)
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 0


def test_get_all_comments_of_album_with_comments(client, custom_requests_mock):
    album_id = utils.post_album(client)

    response_post = utils.post_comment(
        client,
        album_id,
        "comment_text",
        unwrap_id=False,
    )
    assert response_post.status_code == 200

    response_get = utils.get_album_comments(client, album_id)
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] == "comment_text"
    assert comments[0]["created_at"] is not None


def test_get_all_comments_of_album_with_comments_and_sub_comments(
    client, custom_requests_mock
):
    album_id = utils.post_album(client)

    comment_id = utils.post_comment(
        client,
        album_id,
        "comment_text",
    )

    response_post = utils.post_comment(
        client,
        album_id,
        "sub_comment_text",
        parent_id=comment_id,
        unwrap_id=False,
    )
    assert response_post.status_code == 200

    response_get = utils.get_album_comments(client, album_id)
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] == "comment_text"
    assert len(comments[0]["responses"]) == 1
    assert comments[0]["responses"][0]["text"] == "sub_comment_text"


def test_get_all_comments_of_album_with_many_root_comments(
    client, custom_requests_mock
):
    album_id = utils.post_album(client)

    utils.post_comment(
        client,
        album_id,
        "comment_text",
        parent_id=None,
    )

    utils.post_comment(
        client,
        album_id,
        "comment_text_2",
        parent_id=None,
    )

    utils.post_comment(
        client,
        album_id,
        "comment_text_3",
        parent_id=None,
    )

    response_get = utils.get_album_comments(client, album_id)
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 3


def get_all_comments_of_album_with_many_sub_comments(client, custom_requests_mock):
    utils.post_user(client, "creator_id")

    album_id = utils.post_album(client, uid="creator_id")

    comment_id = utils.post_comment(
        client,
        uid="creator_id",
        album_id=album_id,
        message="comment_text",
        parent_id=None,
    )

    for i in [1, 2]:
        utils.post_comment(
            client,
            uid="creator_id",
            album_id=album_id,
            message=f"sub_comment_text_{i}",
            parent_id=comment_id,
        )

    response_get = utils.get_album_comments(client, album_id)
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] == "comment_text"
    assert len(comments[0]["responses"]) == 2
    assert comments[0]["responses"][0]["text"] == "sub_comment_text_1"
    assert comments[0]["responses"][1]["text"] == "sub_comment_text_2"


def test_get_all_comments_only_return_comments_of_album(client, custom_requests_mock):
    album_id = utils.post_album(client)
    utils.post_comment(
        client,
        album_id=album_id,
        message="comment_text",
        parent_id=None,
    )

    album_id_2 = utils.post_album(client)

    response_get = utils.get_album_comments(client, album_id_2)
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 0


def test_get_all_comments_of_album_with_sub_sub_comments(client, custom_requests_mock):
    album_id = utils.post_album(client)

    comment_id = utils.post_comment(
        client,
        album_id=album_id,
        message="comment_text",
        parent_id=None,
    )

    sub_comment_id = utils.post_comment(
        client,
        album_id=album_id,
        message="sub_comment_text",
        parent_id=comment_id,
    )

    utils.post_comment(
        client,
        album_id=album_id,
        message="sub_sub_comment_text",
        parent_id=sub_comment_id,
    )

    response_get = utils.get_album_comments(client, album_id)
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] == "comment_text"
    assert len(comments[0]["responses"]) == 1
    assert comments[0]["responses"][0]["text"] == "sub_comment_text"
    assert len(comments[0]["responses"][0]["responses"]) == 1
    assert comments[0]["responses"][0]["responses"][0]["text"] == "sub_sub_comment_text"


def test_delete_comment(client, custom_requests_mock):
    utils.post_user(client, "creator_id")

    album_id = utils.post_album(client, uid="creator_id")

    comment_id = utils.post_comment(
        client,
        uid="creator_id",
        album_id=album_id,
    )

    response_delete = utils.delete_comment(client, comment_id, uid="creator_id")
    assert response_delete.status_code == 200

    response_get = utils.get_album_comments(client, album_id)
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] is None


def test_another_user_cannot_delete_comment(client, custom_requests_mock):
    utils.post_user(client, "creator_id")
    utils.post_user(client, "another_user_id", "another_user_name")

    album_id = utils.post_album(client, uid="creator_id")

    comment_id = utils.post_comment(
        client,
        uid="creator_id",
        album_id=album_id,
        message="comment_text",
    )

    response_delete = utils.delete_comment(
        client,
        comment_id,
        uid="another_user_id",
    )
    assert response_delete.status_code == 403


def test_edit_comment(client, custom_requests_mock):
    utils.post_user(client, "creator_id")

    album_id = utils.post_album(client, uid="creator_id")

    comment_id = utils.post_comment(
        client,
        uid="creator_id",
        album_id=album_id,
        message="comment_text",
    )

    response_put = utils.put_comment(
        client,
        uid="creator_id",
        comment_id=comment_id,
        message="new_comment_text",
    )

    assert response_put.status_code == 200
    assert response_put.json()["text"] == "new_comment_text"


def test_another_user_cannot_edit_comment(client, custom_requests_mock):
    utils.post_users(client, "creator_id", "another_user_id")

    album_id = utils.post_album(client, uid="creator_id")

    comment_id = utils.post_comment(
        client,
        uid="creator_id",
        album_id=album_id,
        message="comment_text",
    )

    response_put = utils.put_comment(
        client,
        uid="another_user_id",
        comment_id=comment_id,
        message="new_comment_text",
    )

    assert response_put.status_code == 403


def test_listener_cannot_post_comment_in_blocked_album(client, custom_requests_mock):
    utils.post_users(client, "creator_id", "listener_id")
    album_id = utils.post_album(client, uid="creator_id")

    utils.block_album(client, id=album_id)

    response_post = utils.post_comment(
        client,
        uid="listener_id",
        album_id=album_id,
        message="comment_text",
        unwrap_id=False,
    )
    assert response_post.status_code == 404


def test_admin_can_post_comment_in_blocked_album(client, custom_requests_mock):
    utils.post_user(client, "creator_id")
    utils.post_user(client, "admin_id", "admin_name")

    album_id = utils.post_album(client, uid="creator_id")

    utils.block_album(client, id=album_id)

    response_post = utils.post_comment(
        client,
        uid="admin_id",
        album_id=album_id,
        message="comment_text",
        role="admin",
        unwrap_id=False,
    )

    assert response_post.status_code == 200


def test_listener_cannot_edit_comment_in_blocked_album(client, custom_requests_mock):
    utils.post_users(client, "creator_id", "listener_id")

    album_id = utils.post_album(client, uid="creator_id")
    comment_id = utils.post_comment(
        client,
        uid="listener_id",
        album_id=album_id,
        message="comment_text",
        parent_id=None,
    )

    utils.block_album(client, id=album_id)

    response_put = utils.put_comment(
        client,
        uid="listener_id",
        comment_id=comment_id,
        message="new_comment_text",
    )
    assert response_put.status_code == 404


def test_admin_can_edit_comment_in_blocked_album(client, custom_requests_mock):
    utils.post_users(client, "creator_id", "admin_id")

    album_id = utils.post_album(client, uid="creator_id")

    comment_id = utils.post_comment(
        client,
        uid="admin_id",
        album_id=album_id,
        message="comment_text",
        parent_id=None,
    )

    utils.block_album(client, id=album_id)

    response_put = utils.put_comment(
        client,
        uid="admin_id",
        comment_id=comment_id,
        message="new_comment_text",
        role="admin",
    )

    assert response_put.status_code == 200


def test_listener_cannot_delete_comment_in_blocked_album(client, custom_requests_mock):
    utils.post_user(client, "creator_id")
    utils.post_user(client, "listener_id", "listener_name")

    album_id = utils.post_album(client, uid="creator_id")

    comment_id = utils.post_comment(
        client,
        uid="creator_id",
        album_id=album_id,
        message="comment_text",
        parent_id=None,
    )

    utils.block_album(client, id=album_id)

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/albums/comments/{comment_id}/",
        headers={"uid": "listener_id", "api_key": "key"},
    )
    assert response_delete.status_code == 404


def test_get_comments_of_user(client, custom_requests_mock):
    utils.post_user(client, "creator_id")
    utils.post_user(client, "listener_id", "listener_name")

    album_id = utils.post_album(client, uid="creator_id", name="album_name")

    comment_id = utils.post_comment(
        client,
        uid="creator_id",
        album_id=album_id,
        message="creator_comment",
        parent_id=None,
    )

    utils.post_comment(
        client,
        uid="listener_id",
        album_id=album_id,
        message="listener_comment",
        parent_id=comment_id,
    )

    response_get = utils.get_user_comments(client, "listener_id")
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] == "listener_comment"


def test_comment_of_deleted_user_gets_deleted(client, custom_requests_mock):
    utils.post_users(client, "creator_id", "listener_id", "another_id")

    album_id = utils.post_album(client, uid="creator_id")

    comment_id = utils.post_comment(
        client,
        uid="creator_id",
        album_id=album_id,
        message="creator_comment",
        parent_id=None,
    )

    utils.post_comment(
        client,
        uid="listener_id",
        album_id=album_id,
        message="listener_comment",
        parent_id=comment_id,
    )

    response = utils.delete_user(client, "listener_id")
    assert response.status_code == 200

    response_get = utils.get_user_comments(client, "listener_id")

    assert response_get.status_code == 404

    response_get = utils.get_album_comments(client, album_id)
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 1
    assert len(comments[0]["responses"]) == 1
    assert comments[0]["responses"][0]["text"] == "listener_comment"


def test_delete_album_with_comments(client, custom_requests_mock):
    utils.post_users(client, "creator_id", "listener_id")

    album_id = utils.post_album(client, uid="creator_id")

    comment_id = utils.post_comment(
        client,
        uid="creator_id",
        album_id=album_id,
        message="creator_comment",
        parent_id=None,
    )

    utils.post_comment(
        client,
        uid="listener_id",
        album_id=album_id,
        message="listener_comment",
        parent_id=comment_id,
    )

    response_delete = utils.delete_album(client, album_id)
    assert response_delete.status_code == 200

    response_get = utils.get_album_comments(client, album_id)
    assert response_get.status_code == 404
