from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField

class UpdateProfile(FlaskForm):
    picture = FileField("Update profile picture", validators=[FileAllowed(["jpg", "png"])])