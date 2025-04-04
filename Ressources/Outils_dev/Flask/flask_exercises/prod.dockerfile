# Use a Python base image
FROM python:3.10

RUN pip install -U pip
RUN pip install pipenv

# Create a working directory in the container
WORKDIR /app

# Copy only Pipfile and Pipfile.lock first, so Docker can cache this layer
COPY Pipfile Pipfile.lock /app/

# Copy the rest of your code into the image
COPY . /app

# Install the dependencies
RUN pipenv install --system --deploy

# Expose the port Flask runs on (optional, for clarity)
EXPOSE 5000

# Run Flask app in production
CMD ["gunicorn", "flask_example:app", "--bind=0.0.0.0:5000"]
