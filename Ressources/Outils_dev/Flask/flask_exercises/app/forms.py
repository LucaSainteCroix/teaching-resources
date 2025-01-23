import json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional
from app.models import User

REQUIRED_KEYS = {"PULocationID", "DOLocationID", "trip_distance"}

placeholder = {
  "DOLocationID": "239",
  "PULocationID": "236",
  "trip_distance": 1.98
}

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Register')

    # Optional: Custom validation methods to ensure uniqueness
    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        existing_email = User.query.filter_by(email=email.data).first()
        if existing_email:
            raise ValidationError('Please use a different email address.')


class JSONUploadForm(FlaskForm):
    json_file = FileField('Upload JSON File', validators=[Optional()])
    json_text = TextAreaField('Paste JSON', validators=[Optional()], render_kw={"placeholder": json.dumps(placeholder)})
    submit = SubmitField('Submit')

    # We'll store the parsed data here so it's accessible after validation
    ride_data = None

    def validate(self, **kwargs):
        # Run the default validation (check CSRF, etc.)
        if not super().validate():
            return False

        file_provided = (
            self.json_file.data
            and hasattr(self.json_file.data, 'filename')
            and self.json_file.data.filename != ''
        )
        text_provided = (
            self.json_text.data
            and self.json_text.data.strip() != ''
        )

        # Ensure the user has provided either a file or text
        if not file_provided and not text_provided:
            msg = "Please upload a JSON file or paste JSON text."
            self.json_text.errors.append(msg)
            return False

        # Attempt to parse JSON from whichever source is provided
        parsed_data = None
        if file_provided:
            try:
                file_content = self.json_file.data.read().decode('utf-8')
                parsed_data = json.loads(file_content)
            except Exception as e:
                self.json_file.errors.append(f"Could not parse JSON file: {e}")
                return False
        elif text_provided:
            try:
                parsed_data = json.loads(self.json_text.data.strip())
            except json.JSONDecodeError:
                self.json_text.errors.append("Invalid JSON format in text area.")
                return False

        # Now parsed_data should be a Python dict; validate keys
        if not isinstance(parsed_data, dict):
            self.json_text.errors.append("Expected JSON object at the top level.")
            return False

        data_keys = set(parsed_data.keys())
        if data_keys != REQUIRED_KEYS:
            self.json_text.errors.append(
                f"JSON must contain exactly these keys: {REQUIRED_KEYS}. "
                f"Received keys: {data_keys}"
            )
            return False

        # If all checks pass, store the parsed data so the route can access it
        self.ride_data = parsed_data
        return True
