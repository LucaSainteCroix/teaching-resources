import json
from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import login_user, current_user, login_required
from werkzeug.security import check_password_hash
from app import login_manager, csrf
from app.forms import LoginForm, RegistrationForm, JSONUploadForm
from app.models import User
from app.utils import model_utils as mu
from app.services import create_user, check_existing_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def register_routes(app):
    @app.route('/')
    @app.route('/index')
    def index():
        # placeholder posts, implement your own logic
        posts = [
            {
                'author': {'username': 'John'},
                'body': 'Beautiful day in Portland!'
            },
            {
                'author': {'username': 'Susan'},
                'body': 'The Avengers movie was so cool!'
            }
        ]
        return render_template('index.html', title='Home', user=current_user, posts=posts)


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            flash('Login requested for user {}, remember_me={}'.format(
                form.username.data, form.remember_me.data))

            user = check_existing_user(form.username.data)

            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('Logged in successfully!')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.')


        return render_template('login.html', title='Sign In', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():

            new_user = create_user(form)

            login_user(new_user)
            flash('You are now registered and logged in!')

            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)



    @app.route('/upload_json', methods=['GET'])
    def upload_json():
        """
        Renders the form for uploading/pasting JSON.
        """
        form = JSONUploadForm()
        return render_template('upload_json.html', form=form)


    @app.route('/submit_json', methods=['POST'])
    def submit_json():
        """
        Handles the form submission from /upload_json.
        Validates the JSON, calls predict, then shows the result.
        """
        form = JSONUploadForm()
        if form.validate_on_submit():
            # Retrieve the parsed data stored in form.ride_data
            ride_data = form.ride_data

            # Pass it to your existing logic
            features = mu.prepare_features(ride_data)
            prediction_value = mu.predict(features)

            # Show the prediction in a result template
            return render_template('predict_result.html', duration=prediction_value)
        else:
            # Validation failed: re-render the form with errors
            return render_template('upload_json.html', form=form)


    @app.route('/predict', methods=['POST'])
    @csrf.exempt
    def predict_endpoint():
        """
        A direct JSON endpoint for e.g. Postman or curl:
        POST /predict
        Content-Type: application/json
        {
            "PULocationID": "236",
            "DOLocationID": "239",
            "trip_distance": 1.98
        }
        """
        # 1. Parse the raw JSON body
        ride_data = request.get_json()
        if not ride_data:
            return jsonify({"error": "No JSON body or invalid JSON"}), 400

        # 2. Create an instance of the same form.
        form = JSONUploadForm(meta={'csrf': False})

        # 3. We won't be using the file field. Instead, we "inject" the JSON body
        #    as if it were pasted text. The form will then parse and validate it.
        form.json_text.data = json.dumps(ride_data)

        # 4. Validate the form. If it passes, we get validated data in form.ride_data
        if form.validate():
            # form.ride_data now has exactly the 3 keys you require
            features = mu.prepare_features(form.ride_data)
            pred_value = mu.predict(features)
            return jsonify({"duration": pred_value})
        else:
            # If validation fails, return the form errors in JSON
            return jsonify({"errors": form.errors}), 400
