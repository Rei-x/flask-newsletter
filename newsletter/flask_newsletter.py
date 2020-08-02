from flask import request, render_template, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug import exceptions
from flask_mail import Mail
from flask_hashing import Hashing
from smtplib import SMTPRecipientsRefused
from sqlalchemy.exc import IntegrityError, OperationalError
from newsletter.error_codes import error
import re


class Newsletter:

    def __init__(self, app):

        self.db = db = SQLAlchemy(app)
        self.hashing = hashing = Hashing(app)
        self.mail = Mail(app)

        self.mail_username = app.config['MAIL_USERNAME']
        self.template_file = app.config['NEWSLETTER_TEMPLATE']
        self.email_title = app.config['NEWSLETTER_EMAIL_TITLE']
        _SALT = app.config['SECRET_KEY']

        class Client(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(40), nullable=False)
            surname = db.Column(db.String(40), nullable=False)
            email = db.Column(db.String(40), nullable=False, unique=True)
            confirmed = db.Column(db.Boolean, nullable=False, default=False)
            hashed_email = db.Column(db.String(128))

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.__set_hashed_email()

            def __repr__(self):
                return f"User('{self.name}', '{self.surname}', '{self.email}', '{self.confirmed}')"

            def __set_hashed_email(self):
                self.hashed_email = hashing.hash_value(self.email, _SALT)

        self.Client = Client

        try:
            self.Client.query.filter_by(confirmed=True).all()
        except OperationalError:
            db.create_all()

    def new_email_to_newsletter(self):
        try:
            email = request.form['email']
            name = request.form['name']
            surname = request.form['surname']
            website = request.args['redirect']
        except exceptions.BadRequestKeyError as e:
            return e

        if not self.validate_email(email):
            return error("InvalidEmail")

        new_user = self.Client(name=name, surname=surname, email=email)

        if self.client_exists(new_user):
            return error("AlreadySignedUp")
        elif self.email_exists_in_db(new_user):
            return self.send_email(new_user, website)

        try:
            self.db.session.add(new_user)
            self.db.session.commit()
        except IntegrityError:
            return error("AlreadySignedUp")
        except OperationalError:
            return error("Operational")
        except Exception:
            return error("Unexpected")

        return self.send_email(new_user, website)

    def confirm_email(self):
        website = request.args['redirect']
        user = self.Client.query.filter_by(hashed_email=request.args.get("id")).first()
        if user is not None:
            if user.confirmed is True:
                return error("AlreadySignedUp")
            user.confirmed = True
            self.db.session.commit()
            return redirect(website)
        else:
            return error("DoesntExist")

    def remove_email(self):
        user = self.Client.query.filter_by(hashed_email=request.args.get("id"), confirmed=True).first()
        if user is not None:
            user.confirmed = False
            self.db.session.commit()
            return jsonify(succes=True)
        else:
            return error("DoesntExist")

    def send_email(self, user, website):
        try:
            self.mail.send_message('Potwierdź rejestracje',
                                   recipients=[str(user.email)],
                                   html=render_template(self.template_file, id=user.hashed_email, website=website),
                                   sender=self.mail_username)
        except SMTPRecipientsRefused:
            return error("InvalidEmail")
        return jsonify(success=True)

    def create_removal_link(self, email):
        user = self.Client.query.filter_by(email=email).first()
        return str(url_for('remove_email', _external=True, id=user.hashed_email))

    def create_confirm_link(self, email):
        user = self.Client.query.filter_by(email=email).first()
        return str(url_for('confirm_email', _external=True, id=user.hashed_email))

    def client_exists(self, client):
        if self.Client.query.filter_by(email=client.email, confirmed=True).first() is not None:
            return True
        else:
            return False

    def email_exists_in_db(self, email):
        if self.Client.query.filter_by(email=email.email).first() is not None:
            return True
        else:
            return False

    @staticmethod
    def validate_email(email):
        if re.match("^[a-zA-Z0-9_+&*-]+(?:\\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,7}$",
                    email) is not None:
            return True
        return False
