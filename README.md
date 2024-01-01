# DRF API Practice

Exercises on building a REST API using Django Rest Framework and other technologies.

## Technologies Used
- Django REST Framework
- Simple-JWT
- Celery & Celery Beat
- RabbitMQ
- DRF-Spectacular

## Basic Features
- API Documentation using [DRF-Spectacular](https://github.com/tfranzel/drf-spectacular)
- Email verification on user registration
- Scheduled tasks at regular intervals
- Custom JWT authentication for HttpOnly attribute
- CRUD operations for Posts, Comments, and Users
- Dockerization for local development

## ER-Diagram
> Implemented a simple structure using SQLite3 to practice integrating API CRUD operations and other technologies.

Entity-Relationship Diagram generated using [dbdiagram.io](https://dbdiagram.io/)

![drf-api-practice](https://github.com/JiHongKim98/drf-api-practice/assets/144337839/39c978ce-4458-48ec-adaf-55fdbbfa0399)

## Getting Started

Clone this repository to your local machine, rename the `.env.example` file to `.env`, and update the environment variables accordingly.<br/>
Then, run the following command:

```bash
$ docker-compose up
```

And you can navigate to [`http://localhost:8000/docs/swagger/`](http://localhost:8000/docs/swagger/) or [`http://localhost:8000/docs/redoc/`](http://localhost:8000/docs/redoc/) to view the the API documentation.

<br/>

If you want start test or create super user:

```bash
# start test
$ docker-compose exec web python3 manage.py test

# create super user
$ docker-compose exec web python3 manage.py createsuperuser
```

<br/>

If you encounter the `exec /code/entrypoint.sh: no such file or directory` error while running `docker-compose up` on Windows.<br/>
Execute the following command to disable automatic conversion from LF to CRLF:

```bash
$ git config --global core.autocrlf false
```

After running this command, clone the repository again to ensure proper configuration.
