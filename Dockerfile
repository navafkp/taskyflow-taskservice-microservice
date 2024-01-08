FROM python:3.11.3
ENV PYTHONUNBUFFERED 1
WORKDIR /taskapp
COPY requirements.txt /taskapp/requirements.txt

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /taskapp

# Copy the .env file into the image
COPY .env /taskapp/.env

# Install netcat
RUN apt-get update && apt-get install -y netcat
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /taskapp/entrypoint.sh
RUN chmod +x /taskapp/entrypoint.sh
CMD ["bash", "/taskapp/entrypoint.sh"]
EXPOSE 8200

