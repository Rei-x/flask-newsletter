from flask import Flask, request, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug import exceptions
from flask_mail import Mail
from flask_hashing import Hashing
from smtplib import SMTPRecipientsRefused
from sqlalchemy.exc import IntegrityError, OperationalError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
hashing = Hashing(app)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = '***REMOVED***',
    MAIL_PASSWORD='***REMOVED***'
)
mail = Mail(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return "<Task %r>" % self.id


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False, unique=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    hashed_email = db.Column(db.String(128))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__set_hashed_email()

    def __repr__(self):
        return f"User('{self.name}', '{self.surname}', '{self.email}', '{self.confirmed}')"

    def __set_hashed_email(self):
        self.hashed_email = hashing.hash_value(self.email, "pieseczek")


@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'Lipa się stała'
    else:
        print()
        clients = Client.query.all()
        tmp = ""
        for client in clients:
            tmp += str(client) + "\n"
        return tmp


@app.route("/add_email", methods=["POST"])
def new_email_to_newsletter():

    try:
        email = request.form['email']
        name = request.form['name']
        surname = request.form['surname']
    except exceptions.BadRequestKeyError as e:
        return e

    new_user = Client(name=name, surname=surname, email=email)

    if client_exists(new_user):
        return jsonify("{'Succes': False,"
                       "'Error': 'Email is already signed up'}")
    elif email_exists(new_user):
        return send_email(new_user)

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        return jsonify("{'Succes': False,"
                       "'Error': Email}")
    except OperationalError:
        return jsonify("{'Succes': False,"
                       "'Error' : 'OperationalError' }")

    return send_email(new_user)


@app.route("/confirm_email?id=<email_hash>")
def confirm_email(email_hash):
    user = Client.query.filter_by(hashed_email=email_hash, confirmed=False).first()
    if user is not None:
        user.confirmed = True
        db.session.commit()
        return f"Jej udało Ci się zarejestrować do naszego newslettera {user.name}!!!!!"
    else:
        return jsonify("'Succes': False,"
                       "'Error': 'Email doesn't exist'")


@app.route("/remove_email?id=<hashed>")
def remove_email(hashed):
    user = Client.query.filter_by(hashed_email=hashed, confirmed=True).first()
    if user is not None:
        user.confirmed = False
        db.session.commit()
        return f"Wypisaliśmy Cię z naszego newslettera kurwo"
    else:
        return "co xd"


def send_email(user):
    try:
        mail.send_message('Potwierdź rejestracje',
                          recipients=[str(user.email)],
                          html=render_template("index.html", url=request.url_root, email_hash=user.hashed_email),
                          sender="***REMOVED***")
    except SMTPRecipientsRefused:
        return jsonify("{'Succes': False,"
                       "'Error': 'Bad email address'")
    return jsonify("{'Succes': True}")


def client_exists(client):
    if Client.query.filter_by(email=client.email, confirmed=True).first() is not None:
        return True
    else:
        return False
def email_exists(email):
    if Client.query.filter_by(email=email.email).first() is not None:
        return True
    else:
        return False

if __name__ == "__main__":
    app.run(debug=True)
