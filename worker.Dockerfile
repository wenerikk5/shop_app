FROM python:3.10

COPY ./ /app/

RUN cd app && pip install -r requirements.txt

WORKDIR /app

ENTRYPOINT celery -A shop_app worker --loglevel=INFO