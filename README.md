# Overview

This is a small project that provides a REST API for a meme generator service. It uses Django DRF and PostgreSQL.
The service allows users to create, retrieve, and rate memes. It also provides a swagger documentation for the API.
The application, the database, and the swagger application are all dockerized.

# Requirements
Make sure you have Docker installed and running.

# How to run the project
To run the project, you need to clone the repository and run the following command in the root directory of the project:
```
docker-compose up --build
```

# API documentation
To access the API documentation, run the project and go to the following URL:
```
http://localhost:8000
```

# Notes
- The surprise-me endpoint will work correctly only if there are meme templates with valid URLs in the database. Also, it should be noted that the endpoint works rather slowly and in real application it should be optimized (via websockets or message queues).
- Tests are launched automatically before running the server, so if the server is running, the tests are successfully passed.
- I've committed the .env file to allow anyone to run the project without any additional configurations for demonstration purposes only. In a real-world scenario, the file should be kept secret.
