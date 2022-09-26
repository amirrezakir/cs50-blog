from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from .form import UpdateProfile
import secrets
import os
from PIL import Image


views = Blueprint("views", __name__)

@views.route("/")
@views.route("/about")
def about():
    return render_template("about.html", user=current_user)


@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    image_file = url_for('static', filename='pictures/' + current_user.image_file)
    form = UpdateProfile()

    if form.profile_pic.data:
            picture_file = save_picture(form.profile_pic.data)
            current_user.image_file = picture_file

    return render_template("home.html", user=current_user, posts=posts, image_file=image_file, form=form)

@views.route("/create-post", methods=["GET","POST"])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        title = request.form.get('title')

        if not text:
            flash("Post can\'t be empty!", category="erorr")
        else:
            post = Post(text=text ,title=title ,author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("Post is created!", category="success")
            return redirect(url_for("views.home"))

    return render_template("create_post.html", user=current_user)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category="erorr")

    elif current_user.id != post.id:
        flash("You can\'n delete this post!", category="erorr")
        
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post Deleted!", category="success")

    return redirect(url_for("views.home"))

@views.route("/posts/<username>")
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("No user with that username!", category="erorr")
        return redirect(url_for("views.home"))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)

@views.route("/create-comment/<post_id>", methods=["POST"])   
@login_required
def create_comment(post_id):
    text = request.form.get("text")

    if not text:
        flash("post cannot be empty!", category="erorr")
    
    else:
        post = Post.query.filter_by(id=post_id)

        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash("Post does not exist")
    
    return redirect(url_for("views.home"))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash("Comment does not exist", category="erorr")
    
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash("You don\'n have permission to do that", category="erorr")

    else:
        db.session.delete(comment)
        db.session.commit()
        

    return redirect(url_for("views.home"))

@views.route("/like-post/<post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()
    
    if not post:
        return jsonify({"erorr": "Post does not exist"}, 400) 

    elif like:
        db.session.delete(like)
        db.session.commit()

    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
    
    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(views.root_path, "static/pictures", picture_fn)

    output_size = (125,125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_fn


@views.route("/profile/<id>", methods=["GET", "POST"])
@login_required
def profile(id):
    image_file = url_for('static', filename='pictures/' + current_user.image_file)
    form = UpdateProfile()
    new_user = User.query.get(id)

    if request.method == "POST":
        new_user.username = request.form.get("username")
        new_user.email = request.form.get("email")
        

        if form.profile_pic.data:
            picture_file = save_picture(form.profile_pic.data)
            current_user.image_file = picture_file

        try:
            db.session.commit()
            flash("User updated!", category="success")
            return render_template("profile.html", new_user=new_user, user=current_user.id, form=form, image_file=image_file)
        except:
            flash("Something went wrong! try again.", category="erorr")
            return redirect(url_for("views.home"))

    else:
        return render_template("profile.html", user=current_user.id, 
        new_user=new_user, form=form, image_file=image_file)
