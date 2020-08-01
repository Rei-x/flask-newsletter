from flask import Flask
from newsletter.flask_newsletter import Newsletter
import config as cfg

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['NEWSLETTER_TEMPLATE'] = 'index.html'
app.config['NEWSLETTER_EMAIL_TITLE'] = "Potwierdź rejestracje"

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=cfg.MAIL_ADDRESS,
    MAIL_PASSWORD=cfg.MAIL_PASSWORD
)

app.config['SECRET_KEY'] = cfg.SECRET

newsletter = Newsletter(app)


@app.route("/", methods=['POST', 'GET'])
def home():
    clients = newsletter.Client.query.filter_by(confirmed=True).all()
    tmp = ""
    for client in clients:
        tmp += str(client) + "<br>"
    return tmp


@app.route("/add_email", methods=["POST"])
def add_email():
    return newsletter.new_email_to_newsletter()


@app.route("/remove_email")
def remove_email():
    return newsletter.remove_email()


@app.route("/confirm_email")
def confirm_email():
    return newsletter.confirm_email()


if __name__ == "__main__":
    app.run(host='192.168.0.100', debug=True)
