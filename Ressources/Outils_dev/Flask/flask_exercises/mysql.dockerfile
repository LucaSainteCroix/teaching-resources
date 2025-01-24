# Base image - using the same version as specified in your compose file
FROM mysql:8.0

# Adding descriptive labels to the image
LABEL description="MySQL Database Container"
LABEL version="8.0"

# Setting default environment variables
# Note: These will be overridden by runtime environment variables if provided
ENV MYSQL_ROOT_PASSWORD=default_password
ENV MYSQL_DATABASE=default_db_name

# Expose MySQL port
# Note: This is purely documentational. You still need to map ports when running the container
EXPOSE 3306

# Custom MySQL configuration could go here if needed
# COPY my.cnf /etc/mysql/conf.d/

# The volume mounting point
VOLUME /var/lib/mysql

# MySQL base image already includes necessary CMD/ENTRYPOINT
# so we don't need to specify them unless we want to override
