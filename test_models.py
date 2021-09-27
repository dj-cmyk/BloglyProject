from unittest import TestCase

from app import app
from models import db, User, Post

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Tests for model for User."""

    def setUp(self):
        """Clean up any existing users."""

        User.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_get_full_name(self):
        """[summary]testing method get_full_name on instance of User
        """
        test_user = User(first_name="TestFirst", last_name="TestLast", image_url='google.com')
        self.assertEquals(test_user.get_full_name(), "TestFirst TestLast")

   
class PostModelTestCase(TestCase):
    """Tests for model for Post."""

    def setUp(self):
        """Clean up any existing users."""

        Post.query.delete()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    # def test_post_model(self):
    #     '''docstring'''
        # is it possible to test just the straight db model without any methods?