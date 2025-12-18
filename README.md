# Bike4You — Bike Rental Web Application

Bike4You is a full-stack web application built using a microservice architecture.  
The system provides basic functionality for a bike rental service, including user authentication, equipment management, and rental handling.

The project demonstrates backend microservices, frontend integration, REST APIs, and cloud deployment.

To run backend locally:

docker compose up --build

Swagger:
auth-service => http://localhost:8001/docs
inventory-service => http://localhost:8002/docs
rental-service => http://localhost:8003/docs

Frontend:

cd frontend/bike4you-frontend
ng serve
http://localhost:4200/

Render deploy:
https://bike4you-auth.onrender.com/docs
https://bike4you-inventory.onrender.com/docs
https://bike4you-rental.onrender.com/docs
https://bike-4-you-1.onrender.com/


---

## Project Overview

The application consists of:
- Three backend microservices (Auth, Inventory, Rental)
- A single-page Angular frontend
- A shared PostgreSQL database in production

Each backend service is deployed independently and communicates via HTTP APIs.

---

## Core Features

- User registration and login with JWT authentication
- Role-based access control (user / admin)
- Equipment inventory management
- Bike rental and return workflow
- Rental history tracking
- REST APIs documented with Swagger
- Deployed frontend and backend services

---

## Technology Stack

**Backend**
- Python, FastAPI
- SQLAlchemy
- PostgreSQL
- JWT authentication

**Frontend**
- Angular
- TypeScript
- SCSS

**Infrastructure**
- Docker
- Render.com
- Static site hosting

---

## API Documentation

Each backend service exposes Swagger (OpenAPI) documentation.  
Swagger is available both locally and in the deployed environment and supports authenticated requests using JWT tokens.

---

## Deployment

The system is deployed to Render.com:
- Backend services run as Docker-based web services
- The frontend is deployed as a static site
- PostgreSQL is managed by Render

Separate configurations are used for development and production environments.

---

## Testing and Validation

- Manual API testing via Swagger
- End-to-end testing through the Angular frontend
- Authentication, authorization, and business logic validated in production

---


## Educational Context

This project was developed as part of a university course focused on:
- Microservice-based architectures
- Web application development
- REST API design
- Cloud deployment and environment configuration

---

## Author

Oleg Shaltaev  
Bike4You — Final Project

