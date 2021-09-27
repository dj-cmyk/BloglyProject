"""Blogly application."""

from flask import Flask, render_template, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'randomString101010'

debug = DebugToolbarExtension(app)

connect_db(app)
# db.create_all()


# ROUTES FOR DISPLAYING ALL USERS AND USER DETAIL **********************
@app.route('/')
def display_home():
    """[summary]displays home page -> this will be updated in the next step of the project

    Returns:
        [redirect]: [sends user to users list page]
    """

    return redirect('/users')


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
    #flash message that user was deleted?
    return redirect('/users')