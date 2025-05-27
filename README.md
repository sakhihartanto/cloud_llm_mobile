## Project Overview

This project is a Python-based application utilizing FastAPI, designed with two main components:
- **API Service** (includes web interface and SSE)
- **Executor Service** (code execution)

It is containerized using Docker and deployed with Docker Compose on an EC2 instance. SSL is enabled via self-signed certificates and reverse proxy is handled by Nginx.

---

## Directory Structure

```
cloud_llm/
├── api/
│   ├── Dockerfile
│   ├── server.py
│   ├── index.html
│   ├── requirements.txt
│   ├── static/
│   └── ...
├── executor/
│   ├── Dockerfile
│   ├── executor.py
│   └── requirements-executor.txt
├── scripts/
├── test/
├── docker-compose.yml
└── DEPLOY.md
```

---

## Deployment Steps

### 1. Prerequisites

Ensure the following tools are installed on your EC2 instance (Ubuntu, t2.micro):
- Docker
- Docker Compose
- OpenSSL (for generating self-signed certificates)

### 2. Generate Self-Signed SSL Certificate

```bash
mkdir -p nginx
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/privkey.pem \
  -out nginx/fullchain.pem \
  -subj "/CN=localhost"
```

### 3. Nginx Configuration

Create a file `nginx/default.conf`:

```nginx
server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;

    location / {
        proxy_pass http://api:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection keep-alive;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Docker Compose

Example `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    image: api-service
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - executor
    environment:
      - EXECUTOR_URL=http://executor:9000/execute
    networks:
      - cloud_llm_network

  executor:
    image: executor-service
    build:
      context: ./executor
      dockerfile: Dockerfile
    ports:
      - "9000:9000"
    networks:
      - cloud_llm_network

networks:
  cloud_llm_network:
    driver: bridge
```

---

## Build and Run

```bash
docker compose up --build -d
```

---

## Access the App

Open your browser and navigate to:

```
https://<EC2_PUBLIC_IP>/
```

> Note: You may get a browser warning due to the use of a self-signed certificate.

---

## Tips

- Make sure port **443** is open in the EC2 Security Group.
- Adjust the `EXECUTOR_URL` inside your FastAPI app if needed (e.g., `http://executor:9000`).
