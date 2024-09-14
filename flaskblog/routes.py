import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm, InviteUserForm, NewCommentForm, )
from flaskblog.models import User, Post, Comment, Friendship, Category, user_categories, Like  
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flask import jsonify
from flask import current_app
@app.route("/")
@app.route("/home")
def home():
    db.create_all()
    posts = Post.query.all()
    user = current_user
    return render_template('home.html', posts=posts, user = user)
  


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.create_all()
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You are now able to log in', 'success')
        login_user(user)
        return redirect(url_for('interests'))
    else:
         return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# def save_picture(form_picture):
#     random_hex = secrets.token_hex(8)
#     _, f_ext = os.path.splitext(form_picture.filename)
#     picture_fn = random_hex + f_ext
#     picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

#     output_size = (125, 125)
#     i = Image.open(form_picture)
#     i.thumbnail(output_size)
#     i.save(picture_path)

#     return picture_fn
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # Open and save the image without resizing
    i = Image.open(form_picture)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

def save_media(form_media):
    if form_media:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_media.filename)
        media_fn = random_hex + f_ext
        media_path = os.path.join(current_app.root_path, 'static', 'media', media_fn)

        # if f_ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.pdf', '.doc', '.docx', '.xls', '.xlsx']:
        #     if f_ext.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
        #         output_size = (125, 125)
        #         i = Image.open(form_media)
        #         i.thumbnail(output_size)
        #         i.save(media_path)
        if f_ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.pdf', '.doc', '.docx', '.xls', '.xlsx']:
            # Save the media file as it is without resizing
            form_media.save(media_path)
            return media_fn
        else:
            form_media.save(media_path)

            return media_fn

    return None


from datetime import datetime  # Import datetime
from datetime import datetime
from flask import request

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        media_file = None

        if form.file_path.data:
            media_file = save_media(form.file_path.data)

        post = Post(
            title=form.title.data,
            content=form.content.data,
            file_path=media_file,
            author=current_user,
            date_posted=datetime.utcnow()
        )

        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', title='New Post', form=form, legend='New Post')





@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        
        post.title = form.title.data
        post.content = form.content.data
        media_file = save_media(form.file_path.data)
        post.file_path = media_file
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.file_path.data = post.file_path
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user: 
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/account/<int:user_id>/delete", methods = ['GET', 'POST'])
@login_required
def delete_user(user_id):
    user_ = User.query.get(user_id)
    db.session.delete(user_)
    db.session.commit()
    logout_user()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('home'))

def send_reset_email(user):                                         
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():                                               
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)




@login_required
@app.route("/invite_user", methods=['GET', 'POST'])
def invite_user():
    form = InviteUserForm()
    if form.validate_on_submit():
        


        msg = Message('Registration Link For FlaskBlog...',
                    sender='flaskone111@gmail.com',
                    recipients=[form.email.data])

           
        msg.body = f'''Registration Link For FlaskBlog...
        {url_for('register')}
        '''
        mail.send(msg)
        flash('A referral link has been sent to the account!', 'info')
        return redirect(url_for('home'))

    else:
        return render_template('invite_user.html', title = 'Invite User', form = form)


@login_required
@app.route("/create-comment/<post_id>", methods=['POST'])
def create_commment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='danger')
    elif not current_user.is_authenticated:
        flash('Please log in to leave a comment.', category='danger')
    else:
        post = Post.query.get(post_id)

        if post:
            comment = Comment(text=text, user_id=current_user.id, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist', category='error')
    
    return redirect(url_for('home'))

@app.route("/edit-comment/<int:comment_id>", methods=['POST'])
@login_required
def edit_comment(comment_id):
    try:
        data = request.get_json()
        new_text = data.get('text')
        
        comment = Comment.query.get_or_404(comment_id)

        if current_user.id != comment.user_id:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403  # Forbidden

        if not new_text:
            return jsonify({'success': False, 'error': 'Comment cannot be empty'}), 400  # Bad Request

        comment.text = new_text
        db.session.commit()

        return jsonify({'success': True, 'new_comment': comment.text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500  # Internal Server Error

@login_required
@app.route("/delete-comment/<comment_id>")
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    
    if not Comment:
        flash('Comment does not exist', category='error')
    elif current_user.id != comment.user_id and current_user.id != comment.post.user_id:
        flash('You do not have permission to delete this comment', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Your comment has been deleted', 'success')
    return redirect(url_for('home'))


@app.route('/add_friend_/<int:user_id>', methods=['POST'])
@login_required
def add_friend_(user_id):
    user = User.query.get(user_id)
    
    if user and user != current_user:  # Check that the user is not the current user
        current_user.add_friend(user)
        flash(f'You are now friends with {user.username}!', 'success')
    else:
        flash('You cannot be friends with yourself.', 'warning')
    
    return redirect(url_for('friends'))


@app.route('/friends')
@login_required
def friends():
    friends_list = current_user.friendship.all()
    friendsList = []

    for friendshipp in friends_list:
        friend = User.query.filter_by(id=friendshipp.friend_id).first()
        if friend != current_user:  # Exclude the current user from the friends list
            friendsList.append(friend)

    return render_template('friends.html', user=current_user, friends_list=friendsList)

@app.route('/add-friend', methods = ['POST'])
@login_required
def addFriend():
    if request.method == "POST":
        username = request.form['username']
        print(username)
        friend = User.query.filter_by(username=username).first()
        current_user.add_friend(friend)
        return "Success"


@login_required
@app.route('/interests', methods=['GET', 'POST'])
def interests():    
     return render_template('interests.html')
@login_required
@app.route('/submit-selected-cards', methods=['POST'])
def submit_selected_cards():
    data = request.get_json()
    selected_categories = data.get('selectedCards')

    # Log the data received
    print("Received data:", data)
    if selected_categories is not None:
        try:

   
            category_ids_to_delete = [category.id for category in current_user.categories]

            # Delete categories one by one
            for category_id in category_ids_to_delete:
                category = Category.query.get(category_id)
                if category:
                    db.session.delete(category)

            # Commit the changes to the database
            db.session.commit()

            
            new_categories = [Category(name=category_name) for category_name in selected_categories]
            if current_user.categories is not None:
                current_user.categories.extend(new_categories)
            else:
                # If current_user.categories is None, assign new_categories directly
                current_user.categories = new_categories

            db.session.commit()

            return jsonify({"message": "Selected categories updated successfully."})
        except Exception as e:
            # Log the error
            print("Error:", str(e))
            db.session.rollback()
            return jsonify({"message": f"Error updating categories: {str(e)}"}), 500
    else:
        return jsonify({"message": "No categories   selected.", "data":data})

@login_required
@app.route("/like-post/<post_id>", methods=['POST'])

def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        user_id=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.user_id, post.likes)})

# def are_friends(user1, user2):
#     """
#     Check if user1 and user2 are friends.
#     """
#     friendship = Friendship.query.filter(
#         ((Friendship.user_id == user1.id) & (Friendship.friend_id == user2.id)) |
#         ((Friendship.user_id == user2.id) & (Friendship.friend_id == user1.id))
#     ).first()

#     return friendship is not None


# def add_friend(friend_id):
#     friend = User.query.get_or_404(friend_id)
#     current_user.add_friend(friend)
#     flash(f'You are now friends with {friend.username}!', 'success')
#     return redirect(url_for('friends'))

@login_required
@app.route('/remove_friend/<int:friend_id>', methods=['POST'])
def remove_friend(friend_id):
    friend = User.query.get_or_404(friend_id)
    current_user.remove_friend(friend)
    flash(f'You are no longer friends with {friend.username}.', 'success')
    return redirect(url_for('friends'))

# @app.route('/is_friends/<int:user_id>')
# @login_required
# def is_friends(friend_id):
#     friend = User.query.get_or_404(friend_id)
#     are_friends = current_user.is_friends_with(friend)    
#     return render_template('friends.html', friend=friend, are_friends=are_friends)