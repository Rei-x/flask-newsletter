# Flask Newsletter
Flask Newsletter is a package for Flask microframework to handle: 

 - sending a confirm email to email address
 - adding it to database using SQLAlchemy
 - when user confirms email by clicking in the link in the sent email it marks up email address in database as 'confirmed'
 - removing email from database.

# Setup

 - Clone the source of this library `git clone https://github.com/Rei-666/flask-newsletter.git`
- Install all the dependencies with pip `pip install -r requirements.txt`
- Now you can easily add this to your project by `from newsletter.flask_newsletter import Newsletter`

