# AI Cyber Store

AI Cyber Store is a full-stack e-commerce platform combining WordPress, React, FastAPI and AI-powered features.

The project is built as a developer portfolio application demonstrating modern web development, containerization and scalable application architecture.

## Tech Stack

### Frontend
- React
- TypeScript
- Vite
- SCSS
- React Router
- REST API integration

### Backend / AI Services
- Python
- FastAPI
- PostgreSQL
- AI recommendation services

### CMS / E-commerce
- WordPress
- WooCommerce (planned)

### Infrastructure
- Docker
- Docker Compose
- MySQL
- PostgreSQL

---

# Project Structure

```
ai-cyber-store/

├── frontend/                 # React + TypeScript application
├── recommendation-service/   # FastAPI AI recommendation service
├── wordpress/                # WordPress files and themes
├── docker-compose.yml
├── Makefile
└── README.md
```

---

# Running the Project

## Requirements

- Docker
- Docker Compose

## Start application

Build and start containers:

```bash
docker compose up -d --build
```

Check running services:

```bash
docker compose ps
```

Stop application:

```bash
docker compose down
```

---

# Local URLs

Frontend:

```
http://localhost:5173
```

FastAPI:

```
http://localhost:8000
```

WordPress:

```
http://localhost:8080
```

---

# Development Workflow

## Docker commands

Start:

```bash
docker compose up -d
```

Rebuild after Docker changes:

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f
```

---

## Optional Makefile commands

Linux/macOS users can use:

```bash
make up
```

```bash
make build
```

```bash
make logs
```

---

# Current Features

- React frontend application
- TypeScript configuration
- React Router navigation
- Application layout structure
- SCSS styling system
- Dockerized development environment
- WordPress integration foundation
- FastAPI service foundation

---

# Planned Features

- AI product assistant
- Cybersecurity product catalog
- AI recommendations
- Product search
- User accounts
- WooCommerce integration
- Security dashboard
- Monitoring with Zabbix
- Kubernetes deployment
- CI/CD pipeline

---

# Architecture

```
                 React + TypeScript
                         |
                         |
                    FastAPI API
                         |
              ---------------------
              |                   |
         PostgreSQL          AI Services


              WordPress + MySQL
                    |
              E-commerce CMS
```

---

# Author

Marcin Potoczny

GitHub:

https://github.com/marpot/