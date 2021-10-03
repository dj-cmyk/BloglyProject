"""Blogly application."""

from flask import Flask, render_template, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'randomString101010'

debug = DebugToolbarExtension(app)

connect_db(app)
# db.create_all()


# ROUTES FOR DISPLAYING ALL USERS AND USER DETAIL ****************************************
@app.route('/')
def display_home():
    """[summary]displays 5 most recent blog posts

    Returns:
        [render template]: [list page with 5 blog posts and links to users and tags]
    """
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('index.html', posts=posts)


@app.route('/users')
def display_all_users():
    """[summary]displays list of all users in db

    Returns:
        [render template]: [user template with list of all users from db]
    """

    users = User.query.all()

    return render_template('users.html', users = users)


@app.route('/users/<int:user_id>')
def display_user_detail(user_id):
    """[summary]displays details about each user - full name and image, as well as buttons to edit or delete the user

    Args:
        user_id ([int]): [primary key of user id from db]

    Returns:
        [render template]: [user details page]
    """

    user = User.query.get_or_404(user_id)
    return render_template('user-detail.html', user=user)


# ROUTES FOR ADDING USERS ******************************
@app.route('/users/new', methods=['GET'])
def add_new_user():
    """[summary]displays page with form to add new user

    Returns:
        [render template]: [add new user form page]
    """
    return render_template('user-form.html')


@app.route('/users/new', methods=['POST'])
def handle_new_user():
    """[summary] handles submission of form data to add new user to db

    Returns:
        [redirect]: [back to list of all users, including the newest addition]
    """

    # get data from form
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    image_url = request.form['image_url']
    
    # create new user with that data
    if (image_url == ''):
        new_user = User(first_name = first_name, last_name = last_name)
    else:
        new_user = User(first_name = first_name, last_name = last_name, image_url = image_url)

    # commit to db
    db.session.add(new_user)
    db.session.commit()

    return redirect('/users')




# ROUTES FOR EDITING USERS AND DELETING USERS ******************
@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    """[summary]displays form pre-populated with user information to be edited if desired

    Args:
        user_id ([int]): [primary key from user table in db] - used to get particular users information

    Returns:
        [render template]: [shows form with user information to be edited]
    """

    user = User.query.get_or_404(user_id)
    return render_template('user-edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['POST'])
def handle_edit_user(user_id):
    """[summary] takes data from user form to edit existing users and updates the selected row with current inputs

    Args:
        user_id ([int]): [primary key from user table in db] - used to know which particular user is being updated

    Returns:
        [redirect]: [sends back to users list page]
    """
    # get user to edit
    edit_user = User.query.get_or_404(user_id)

     # get data from form if there is any, and make changes
    if (request.form['first_name'] != ''):
        edit_user.first_name = request.form['first_name'] 
    if (request.form['last_name'] != ''):
        edit_user.last_name = request.form['last_name']
    if (request.form['image_url'] != ''):
        edit_user.image_url = request.form['image_url']
    
    # commit to db
    db.session.add(edit_user)
    db.session.commit()

    return redirect('/users')
    

@app.route('/users/<int:user_id>/delete', methods=['GET', 'POST'])
def remove_user_from_db(user_id):
    """[summary] delets user from db

    Args:
        user_id ([int]): [primary key from users table in db] - used to select which row will be deleted

    Returns:
        [redirect]: [sends back to list of all users which will now not have the user who has just been deleted]
    """
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    
    return redirect('/users')




# ROUTES FOR BLOG POSTS ****************************************************************
@app.route('/users/<int:user_id>/posts/new')
def add_new_post_form(user_id):
    """[summary]displays form to add a new post

    Args:
        user_id ([int]): [user_id from db]

    Returns:
        [render template]: [shows form to add a new post with tags, associated with a specific user]
    """
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('post-add.html', user=user, tags=tags)


@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def handle_new_post(user_id):
    """[summary]handle submission of new post form 

    Args:
        user_id ([int]): [user_id from db]

    Returns:
        [redirect]: [sends user to detail page of the user who submitted the new post]
    """

    # get data from form
    title = request.form['title']
    content = request.form['content']
    tag_keys = request.form.getlist('tag-keys')
    
    
    # create new post with that data
    new_post = Post(title = title, content = content, user_id = user_id)


    # commit to db
    db.session.add(new_post)
    db.session.commit()


    # add post-tag entry to db
    for tag in tag_keys:
        get_tag = Tag.query.filter(Tag.tag == tag).one()
        new_postTag = PostTag(post_id = new_post.id, tag_id = get_tag.id)
        db.session.add(new_postTag)
        db.session.commit()
    

    return redirect(f'/users/{user_id}')


@app.route('/posts/<int:post_id>')
def show_post_details(post_id):
    """[summary]display post detail

    Args:
        post_id ([int]): [post_id from db]

    Returns:
        [render template]: [shows all details about the specific post being requested - title, content, user full name, created time stamp, tags]
    """
    post = Post.query.get_or_404(post_id)
    return render_template('post-detail.html', post=post)


@app.route('/posts/<int:post_id>/edit')
def display_edit_post(post_id):
    """[summary]display form to edit post - pre-populated with post data

    Args:
        post_id ([int]): [post id from db]

    Returns:
        [render template]: [shows the form to the user]
    """
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('post-edit.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def handle_edit_post(post_id):
    """[summary]handle form data to edit post

    Args:
        post_id ([int]): [post id from db]

    Returns:
        [redirect]: [sends user to post detail page to display updated information]
    """
    # get post to edit
    edit_post = Post.query.get_or_404(post_id)


    # get tag data from form 
    tag_keys = request.form.getlist('tag-keys')

    # check all data from form against original post and make changes if necessary
    if (request.form['title'] != ''):
        edit_post.title = request.form['title'] 
    if (request.form['content'] != ''):
        edit_post.content = request.form['content']
    
    # clear tag list, then append whatever has been checked on the edit. the form populates with the previous tags checked, so they won't change unless the user changes them.
    edit_post.tags = []

    for tag in tag_keys:
        get_tag = Tag.query.filter(Tag.tag == tag).one()
        edit_post.tags.append(get_tag)


    
    # commit to db
    db.session.add(edit_post)
    db.session.commit()

    return redirect(f'/posts/{post_id}')


@app.route('/posts/<int:post_id>/delete', methods=['GET', 'POST'])
def remove_post_from_db(post_id):
    """[summary]delete post from db

    Args:
        post_id ([int]): [post id from db]

    Returns:
        [redirect]: [removes post from db *only if post has no tags* and redirects user back to the list of all users]
    """
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()
    #flash message that post was deleted?
    return redirect('/users')



# ROUTES FOR TAGS **********************************************************
@app.route('/tags')
def show_all_tags():
    """[summary]display list of all tags currently in db as well as button to add new tag

    Returns:
        [render template]: [display list of all tags currently in db]
    """
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)


@app.route('/tags/<int:tag_id>')
def display_tag_detail(tag_id):
    """[summary]display detail about tag including list of posts that are tagged with that specific tag

    Args:
        tag_id ([int]): [tag id from db]

    Returns:
        [render template]: [display detail about specific tag]
    """
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag-detail.html', tag = tag)


@app.route('/tags/new')
def display_add_tag_form():
    """[summary]displays form to add new tag

    Returns:
        [render template]: [displays form to add new tag]
    """
    return render_template('tag-add.html')


@app.route('/tags/new', methods=['POST'])
def handle_add_tag_form():
    """[summary]handle form submission to add new tag to db

    Returns:
        [redirect]: [sends user back to list of tags and displays all tags including most recently added]
    """
    
    # get data from form
    tag = request.form['tag_name']
    
    # create new tag with data
    new_tag = Tag(tag=tag)

    # commit to db
    db.session.add(new_tag)
    db.session.commit()
    
    return redirect('/tags')


@app.route('/tags/<int:tag_id>/edit')
def display_edit_tag(tag_id):
    """[summary] display form to edit tag

    Args:
        tag_id ([int]): [tag id from db]

    Returns:
        [render template]: [display pre-populated form to edit tag]
    """
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag-edit.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def handle_edit_tag(tag_id):
    """[summary]handle form submission to edit tag

    Args:
        tag_id ([int]): [tag id from db]

    Returns:
        [redirect]: [sends user back to list of all tags]
    """
    
    # get tag by id to edit
    edit_tag = Tag.query.get_or_404(tag_id)

     # get data from form 
    edit_tag.tag = request.form['tag_name'] 
    
    # commit to db
    db.session.add(edit_tag)
    db.session.commit()
    return redirect('/tags')


@app.route('/tags/<int:tag_id>/delete', methods=['GET', 'POST'])
def handle_delete_tag(tag_id):
    """[summary]remove tag from db

    Args:
        tag_id ([int]): [tag id from db]

    Returns:
        [redirect]: [removes tag from db if no associated posts exist, and then redirects user to the list of tags]
    """
    Tag.query.filter_by(id=tag_id).delete()
    db.session.commit()
    return redirect('/tags')