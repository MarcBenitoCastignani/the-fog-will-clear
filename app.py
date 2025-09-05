import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB and migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(50), nullable=False)  # store username of commenter
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

# --- Context Processor ---
@app.context_processor
def inject_now():
    return {'current_year': datetime.now().year}

# --- Routes ---
@app.route('/')
def home():
    latest_post = Post.query.order_by(Post.created_at.desc()).first()
    return render_template('index.html', latest_post=latest_post)


@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('blog.html', posts=posts)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    return render_template('view_post.html', post=post, comments=comments)


@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash("Only admin can add posts.", "warning")
        return redirect(url_for('blog'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blog'))

    return render_template('new_post.html')


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash("Only admin can edit posts.", "warning")
        return redirect(url_for('blog'))

    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('view_post', post_id=post.id))

    return render_template('edit_post.html', post=post)


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash("Only admin can delete posts.", "warning")
        return redirect(url_for('blog'))

    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog'))


@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('view_post', post_id=post.id))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            error = "Username or email already exists."
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for('login'))

    return render_template('signup.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Admin login
        if email == os.environ.get("ADMIN_USER") and password == os.environ.get("ADMIN_PASS"):
            session['logged_in'] = True
            session['is_admin'] = True
            session['username'] = "Admin"
            return redirect(url_for('blog'))

        # Regular user login (email only)
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['logged_in'] = True
            session['username'] = user.username
            session['is_admin'] = False
            return redirect(url_for('blog'))
        else:
            error = "Invalid email or password"

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if not session.get('logged_in'):
        flash("Please log in to comment.", "warning")
        return redirect(url_for('login'))

    content = request.form['content']
    if content:
        new_comment = Comment(
            content=content,
            post_id=post_id,
            username=session.get('username')
        )
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('view_post', post_id=post_id))


@app.route('/tips')
def tips():
    return render_template('tips.html')


@app.route('/motivation')
def motivation():
    return render_template('motivation.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# --- Run App ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
