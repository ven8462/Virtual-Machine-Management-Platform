# Virtual Machine Management Platform

## Overview
The **Virtual Machine Management Platform** is a Django-based system designed for managing virtual machines (VMs), backups, snapshots, billing, and subscriptions. The platform features user management with role-based access, VM automation, subscription billing, audit logging, and automated deployment using CI/CD pipelines on Kubernetes.

## Key Features
- **Virtual Machine Management**: Create, update, delete, and move virtual machines.
- **Backup & Snapshot Management**: Manage VM backups and snapshots.
- **Billing & Subscriptions**: Subscription-based model for VMs, automated billing, and payment history.
- **User Authentication**: JWT-based user signup, login, and role-based access.
- **Audit Logging**: Logs all user activities for auditing purposes.
- **CI/CD & Kubernetes Orchestration**: Automated deployments using pipelines and Kubernetes orchestration.

## Table of Contents
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Dependencies](#dependencies)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [CI/CD Pipelines](#ci-cd-pipelines)
- [Kubernetes Orchestration](#kubernetes-orchestration)
- [Troubleshooting](#troubleshooting)

## Tech Stack
- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **CI/CD**: GitHub Actions, Docker
- **Deployment**: Kubernetes Cluster
- **Orchestration**: Kubernetes (GKE or similar)
- **Containerization**: Docker

## Installation

### Clone the Repository
```bash
git clone https://github.com/ven8462/vm-server.git
cd vm-backend
```

### Environment Variables
Create a `.env` file in the root of your project and define the following variables:
```bash
DB_NAME="DB name"
DB_USER="DB username"
DB_PASSWORD="DB password"
DB_HOST="DB Host"
DB_PORT=port
SECRET_KEY="JWT generation secret key"
DB_URI="DB URI"
```

### Install Dependencies
Make sure you have Python 3.11+ and `pip` installed, then install the project dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies

The application uses `requirements.txt` to manage dependencies. Key dependencies include:
- Django 5.1.1
- djangorestframework 3.15.2
- psycopg2 2.9.9
- PyJWT 2.9.0
- django-environ for environment variable management

## Database Setup
Create the PostgreSQL database and run migrations:
```bash
psql -U postgres
CREATE DATABASE vm_management;
python manage.py migrate
```

## Running the Application
To run the application locally:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/signup/`: User signup
- `POST /api/login/`: User login

### Virtual Machines
- `POST /api/create-vms/`: Create a virtual machine
- `GET /api/my-vms/`: View all virtual machines for a user
- `PUT /api/vms/update/<vm_id>/`: Update a virtual machine
- `DELETE /api/vms/delete/<vm_id>/`: Delete a virtual machine
- `POST /api/virtual-machines/<vm_id>/move/`: Move a virtual machine to another server

### Backups & Snapshots
- `POST /api/create-backup/`: Create a backup for a virtual machine
- `GET /api/backups/`: Get all backups
- `GET /api/snapshots/`: Get all snapshots

### Subscription & Billing
- `POST /api/subscribe/`: Subscribe to a plan
- `GET /api/subscription/`: View current subscription
- `POST /api/payment/`: Mock payment endpoint
- `GET /api/payment-history/`: View payment history

## CI/CD Pipelines

The CI/CD pipeline automates the building, testing, and deployment of the application using **GitHub Actions** and **Docker**.

### GitHub Actions Workflow
The `main.yml` workflow file includes the following stages:
1. **Build and Test**: Installs dependencies, runs tests.
2. **Build Docker Image**: Builds a Docker image of the application.
3. **Push to Docker Hub**: Pushes the built image to Docker Hub.
4. **Deploy to Kubernetes**: Deploys the Docker image to the Kubernetes cluster.

### Sample GitHub Actions Workflow
```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          python manage.py test

  docker:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Log in to Docker Hub
        run: echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin

      - name: Build Docker image
        run: docker build -t vm-backend:${{ github.sha }} .

      - name: Push Docker image
        run: docker push vm-backend:${{ github.sha }}
        
  deploy:
    runs-on: ubuntu-latest
    needs: docker
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/deployment.yaml
```

## Kubernetes Orchestration

The deployment is automated using **Kubernetes**, providing scalability and high availability. The setup involves:

1. **Kubernetes Cluster**: The application is deployed on a Kubernetes cluster using **GKE** or a similar provider.
2. **Docker Images**: The application is containerized using Docker and the images are stored in Docker Hub.
3. **Deployment Files**: Kubernetes deployment files include deployment specs, services, and ingress configurations.

### Containerizing the Application
```
# Build the Docker image
docker build -t <your-docker-username>/your-app:latest .

# Push the image to Docker Hub
docker push <your-docker-username>/your-app:latest

```

### Configure SSL for Secure Communication
```
sudo microk8s.enable cert-manager
sudo microk8s.kubectl apply -f issuer.yaml
sudo microk8s.kubectl apply -f ingress.yaml

```

### Deploy to Kubernetes Cluster

```
sudo microk8s.kubectl apply -f django-deployment.yaml
sudo microk8s.kubectl get pods
sudo microk8s.kubectl get services

```
### Set Up CI/CD Pipeline with GitHub Actions
Create a .github/workflows/deploy.yml file in your repository to automate testing, building, and deployment.

### Sample Kubernetes Deployment
Create the following `deployment.yaml` file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vm-backend-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vm-backend
  template:
    metadata:
      labels:
        app: vm-backend
    spec:
      containers:
      - name: vm-backend
        image: vm-backend:latest
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: vm-backend-service
spec:
  type: LoadBalancer
  ports:
    - port: 8000
  selector:
    app: vm-backend
```

## Troubleshooting
If you encounter SSH connection issues during pipeline deployment, follow these steps:
1. Check server accessibility.
2. Verify SSH port (ensure port 2112 is open).
3. Check firewall settings.

## License
This application is under MIT license as attached

## Developer
This application has been developed by Lavender Anyango