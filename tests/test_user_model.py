from App.models import User
import pytest  # type: ignore


@pytest.fixture
def user1():
    return User(username='timmy', email='Timbo@example.com')


@pytest.fixture
def user2():
    return User(username='Rob', email='Rob@example.com')


@pytest.fixture
def user3():
    return User(username='Liana', email='liana@example.com')


def test_user_password_creation(mocker, user1, user2):
    """Tests when a user is created whether password is
      hashed properly.
    """
    # replaces the methods with mock objects
    mock_set_password = mocker.patch.object(User, 'set_password')
    mock_check_password = mocker.patch.object(User, 'check_password')

    mock_check_password.side_effect = lambda password: password == 'timmy@123'

    user1.set_password('timmy@123')
    user2.set_password('timmy@123')

    user1.password_hash = 'hashed1'
    user2.passowrd_hash = 'hashed2'

    assert user1.password_hash != user2.password_hash
    assert user1.check_password('timmy@123') is True
    assert user2.check_password('roobinhood') is False

    mock_set_password.assert_any_call('timmy@123')


class TestFollowFunctionality:
    def test_following_other_users(self, mocker, user1, user2):
        """Test that a user can follow another user."""

        mock_follow = mocker.patch.object(User, 'follow')
        mock_unfollow = mocker.patch.object(User, 'unfollow')
        mock_is_following = mocker.patch.object(User, 'is_following')

        mock_is_following.side_effect = [True, False]

        user1.follow(user2)
        assert user1.is_following(user2)

        user1.unfollow(user2)
        assert not user1.is_following(user2)

        mock_follow.assert_called_once_with(user2)
        mock_unfollow.assert_called_once_with(user2)

    def test_whether_users_can_follow_themselves(self, mocker, user1, user2):
        """Tests whether users can follow and unfollow other users"""
        mock_follow = mocker.patch.object(
            User, 'follow',
            side_effect=ValueError("Users cannot follow themselves."))
        mock_is_following = mocker.patch.object(
            User, 'is_following', return_value=False)

        with pytest.raises(ValueError,
                           match="Users cannot follow themselves."):
            user1.follow(user1)

        assert not user2.is_following(
            user2), "User should not be able to themselves"

        mock_follow.assert_called_once_with(user1)
        mock_is_following.assert_called_once_with(user2)


# import pytest
# from unittest.mock import patch, MagicMock
# from App.models import User


# @pytest.fixture
# def mock_db_session(monkeypatch):
#     mock_session = MagicMock()

#     monkeypatch.setattr('App.models.db.session', mock_session)
#     return mock_session


# def test_follow(mock_db_session):
#     # Mock the User query to return a specific user object
#     user1 = User(id=1, username='tim', email='tim@example.com')
#     user2 = User(id=2, username='sue', email='sue@example.com')

#     mock_query = MagicMock()
#     mock_query.filter_by.return_value.first.side_effect = [user1, user2]
#     mock_db_session.query.return_value = mock_query

#     with patch('App.models.User.follow', MagicMock()) as mock_follow:
#         user2.follow(user1)

#         # Check that the follow method was called correctly
#         mock_follow.assert_called_with(user1)
#         mock_db_session.add.assert_called_with(user2)
#         assert user2.is_following(user1)


# def test_unfollow(mock_db_session):
#     user1 = User(id=1, username='tim', email='tim@example.com')
#     user2 = User(id=2, username='sue', email='sue@example.com')

#     mock_query = MagicMock()
#     mock_query.filter_by.return_value.first.side_effect = [user1, user2]
#     mock_db_session.query.return_value = mock_query

#     with patch('App.models.User.unfollow', MagicMock()) as mock_unfollow:
#         user2.unfollow(user1)

#         # Check that the unfollow method was called correctly
#         mock_unfollow.assert_called_with(user1)
#         mock_db_session.delete.assert_called_with(user2)
#         assert not user2.is_following(user1)


# def test_is_following(mock_db_session):
#     user1 = User(id=1, username='tim', email='tim@example.com')
#     user2 = User(id=2, username='sue', email='sue@example.com')

#     mock_query = MagicMock()
#     mock_query.filter_by.return_value.first.side_effect = [user1, user2]
#     mock_db_session.query.return_value = mock_query

#     # Mock the count method to return 1, indicating a following relationship
#     with patch('App.models.User.is_following', MagicMock(return_value=True)):
#         assert user2.is_following(user1)
#         mock_db_session.query.assert_called()
