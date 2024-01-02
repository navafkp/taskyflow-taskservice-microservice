FROM python:3.11.3
ENV PYTHONUNBUFFERED 1
WORKDIR /taskapp
RUN pip install psycopg2
COPY requirements.txt /taskapp/requirements.txt
RUN pip install -r requirements.txt
COPY . /taskapp


