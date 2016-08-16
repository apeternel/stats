DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ific',                      # Or path to database file if using sqlite3.
        'USER': 'ific',                      # Not used with sqlite3.
        'PASSWORD': 'EeZ3audu',                  # Not used with sqlite3.
        'HOST': '172.16.42.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

CELERY_RESULT_BACKEND = "amqp"

BROKER_BACKEND = "amqplib"

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "ific"
BROKER_PASSWORD = "hci3coh8Mo5ahXi"
BROKER_VHOST = "/ific"
