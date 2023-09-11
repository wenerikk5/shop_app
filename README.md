# shop_app

## Description

A draft of e-commerce site.
NOTE. Project in progress.

Main implemented features:
- Categories might include other categories or products;
- Categories with products include extensive filtering (price, brand, various attributes);
- Each product might have several subproducts with different size, color, price etc.;
- Recommendation of complementary products;
- Rating of products;
- Search;
- Stripe payment;
- Generation of pdf invoices and notifications.

Not added yet:
- Product reviews;
- Internationalization;
- Stock information in DB;
- Tests.

## Used stack

- Python 3.10+, JS(ES6);
- Django 4 with Django templates;
- PostgresSQL - main DB, advanced search functionalities;
- Celery with RabbitMQ - email notifications;
- Redis - recommendation engine for compelementary products;
- Docker.

## Set up and use

```
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install weasypring (for MacOs)
brew install weasyprint

# Rename .env-example to .env and amend it's data
mv .env-example .env

# Run services with docker-compose
docker compose up -d --build

# Apply migrations
python3 manage.py migrate

# Fill DB with test data
python3 manage.py load_data

# Collect static
python3 manage.py collectstatic

# Start server
python3 manage.py runserver

# Check page http://127.0.0.1:8000/

```

## DB structure

    <img src="https://github.com/wenerikk5/">


## Previews

    <img src="https://github.com/wenerikk5/">



