from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import PasswordField,StringField,SubmitField,EmailField,IntegerField



class login_form(FlaskForm):
    username=EmailField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")


class regester(FlaskForm):
    email=EmailField("Email",validators=[DataRequired()])
    username=StringField("Username" , validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_2 = PasswordField("Confirm password", validators=[DataRequired()])
    phone=StringField("Phone Number",validators=[DataRequired()])
    submit=SubmitField("  Submit  ")
