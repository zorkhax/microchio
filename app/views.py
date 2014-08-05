# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid, socketio, thread, background_thread
from models import User, ROLE_USER, ROLE_ADMIN, Post
from forms import LoginForm, EditForm, PostForm
from datetime import datetime
from threading import Thread
from flask.ext.socketio import emit, join_room, leave_room
from urlparse import urlparse, parse_qs


@socketio.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})

@socketio.on('new post event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    if message['data']:
        post = Post(body = message['data'], timestamp = datetime.utcnow(), author = current_user)
        db.session.add(post)
        db.session.commit()
        g.user = current_user
        emit('new post added',
            {'data': render_template('post.html',
            post = post, hide_delete = True), 
            'owner_data': render_template('post.html',
            post = post, hide_delete = False), 
            'userid': g.user.id}, 
            broadcast=True)

@socketio.on('delete post event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    if message['data']:
        g.user = current_user
        delete(int(message['data']))

@socketio.on('like post event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    if message['data']:
        g.user = current_user    
        like(int(message['data']))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

def video_id(value):
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()
        
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data, timestamp = datetime.utcnow(), author = g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    youtubelink = video_id("http://www.youtube.com/watch?v=z4hyZcdaCqU")

    return render_template('index.html',
        title = 'Home',
        form = form,
        posts = posts,
        youtubelink = youtubelink)

@app.route('/like/<int:id>')
@login_required
def like(id):
    post = Post.query.get(id)
    if post == None:
        flash('Post not found.')
        return redirect(url_for('index'))
    u = post.switch_like(g.user)
    if u is None:
        flash('Cannot like post.')
        return redirect(url_for('index'))
    db.session.add(u)
    db.session.commit()
    flash('Post has been liked.')
    emit('post liked',
        {'data': id, 'likes_count': post.likes_count()},
        broadcast=True)
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post == None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    emit('post deleted',
        {'data': id},
        broadcast=True)
    return redirect(url_for('index'))

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
  if g.user is not None and g.user.is_authenticated():
      return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
      session['remember_me'] = form.remember_me.data
      return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
  return render_template('login.html', 
      title = 'Sign In',
      form = form,
      providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# @app.route('/user/<nickname>')
# @login_required
# def user(nickname):
#     user = User.query.filter_by(nickname = nickname).first()
#     if user == None:
#         flash('User ' + nickname + ' not found.')
#         return redirect(url_for('index'))
#     posts = [
#         { 'author': user, 'body': 'Test post #1' },
#         { 'author': user, 'body': 'Test post #2' }
#     ]
#     return render_template('user.html',
#         user = user,
#         posts = posts)

@app.route('/userid/<int:id>')
@login_required
def userid(id):
    user = User.query.filter_by(id = id).first()
    if user == None:
        flash('User ' + id + ' not found.')
        return redirect(url_for('index'))
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',
        user = user,
        posts = posts)


@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
        form = form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500