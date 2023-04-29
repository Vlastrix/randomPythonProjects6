from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE IN DB
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# Line below only required once, when creating DB.
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        hashed_and_salted_pass = generate_password_hash(password=data["password"], method="pbkdf2:sha256",
                                                        salt_length=8)
        new_user = User(email=data["email"], password=hashed_and_salted_pass, name=data["name"])
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            flash("The following email has already been registered, try to log in instead!")
            return redirect(url_for("login"))
        login_user(new_user)
        return redirect(url_for("secrets"))
    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        found_user = db.session.query(User).filter_by(email=email).first()
        if found_user is None:
            flash("The email you have entered does not exist in our database, please try again.")
            return redirect(url_for("login"))
        elif not check_password_hash(found_user.password, password):
            flash("The password was incorrect, please try again.")
            return redirect(url_for("login"))
        else:
            login_user(found_user)
            return redirect(url_for("secrets"))
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name, logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory(path="cheat_sheet.pdf", directory="static/files")


if __name__ == "__main__":
    app.run(debug=True)
