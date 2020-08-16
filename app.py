from flask import Flask
from newsletter.flask_newsletter import Newsletter, error
import config as cfg

app = Flask(__name__)

# SQLALchemy config
app.config.update(
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db',
    SQLALCHEMY_TRACK_MODIFICATIONS = False)

# Newsletter config
app.config.update(
    NEWSLETTER_TEMPLATE='email_template.html',
    NEWSLETTER_EMAIL_TITLE='Potwierdź rejestracje',
    NEWSLETTER_RECAPTCHA_V3=True)

# FlaskMail config
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=cfg.MAIL_ADDRESS,
    MAIL_PASSWORD=cfg.MAIL_PASSWORD
)

app.config['SECRET_KEY'] = cfg.SECRET

newsletter = Newsletter(app)


# Listing all of the registered users
@app.route("/", methods=['POST', 'GET'])
def home():
    clients = newsletter.Client.query.filter_by(confirmed=True).all()
    tmp = ""
    for client in clients:
        tmp += str(client) + "<br>"
    return tmp


# Function accepts 3 arguments by POST method from request from form:
# name
# surname
# email - required
@app.route("/add_email", methods=["POST"])
def add_email():
    if newsletter.is_recaptcha_valid(cfg.RECAPTCHA_SECRET):
        return newsletter.new_email_to_newsletter()
    else:
        return error("BadCaptcha")


# Function accepts one argument by GET method
# id - hash of the email
#
# to create removal link use newsletter.create_removal_link(email) method
# that will return link which has to be clicked in order to remove email from database
@app.route("/remove_email")
def remove_email():
    return newsletter.remove_email()


# Function accepts one argument by GET method
# id - hash of the email
#
# to create confirm link use newsletter.create_confirm_link(email) method
# that will return link which has to be clicked in order to confirm email address
@app.route("/confirm_email")
def confirm_email():
    return newsletter.confirm_email()


if __name__ == "__main__":
    app.run(host='192.168.0.100', debug=True)
