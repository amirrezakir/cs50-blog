from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment
from . import db

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)

@views.route("/create-post", methods=["GET","POST"])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash("Post can\'t be empty!", category="erorr")
        else:
            post = Post(text=text, author=current_user.id)
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

    elif current_user.id == post.id:
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