from unittest import TestCase

from app import app
from models import db, User, Post

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class UserViewsTestCase(TestCase):
    """Tests for views for Users."""

    def setUp(self):
        """Add sample user."""

        User.query.delete()

        test_user = User(first_name="TestFirst", last_name="TestLast", image_url='google.com')
        db.session.add(test_user)
        db.session.commit()

        self.user_id = test_user.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_list_users(self):
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('TestFirst', html)

    def test_show_user(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>TestFirst TestLast</h1>', html)

    def test_add_user(self):
        with app.test_client() as client:
            d = {"first_name": "FirstName", "last_name": "LastName", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png"}
            resp = client.post("/users/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("FirstName LastName", html)



class PostViewsTestCase(TestCase):
    """Tests for views for Posts."""

    def setUp(self):
        """Add sample Post."""

        User.query.delete()
        test_user = User(first_name="TestFirst", last_name="TestLast", image_url='google.com')
        db.session.add(test_user)
        db.session.commit()

        Post.query.delete()
        test_post = Post(title="title", content="text content", user_id = test_user.id)
        db.session.add(test_post)
        db.session.commit()

        self.post_id = test_post.id


    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()


    def test_add_post(self):
        with app.test_client() as client:
            d = {"title": "TestTitle", "content": "TestContent", "user_id": 1}
            resp = client.post("/users/1/posts/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("TestTitle", html)


    def test_show_post(self):
        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>title</h1>', html)

