# AI Cyber Store

AI Cyber Store is a full-stack e-commerce project combining WordPress, React, FastAPI and AI features.

The project is built as a developer portfolio application demonstrating modern web development, containerization and cloud-native technologies.

## Tech Stack

### Frontend
- React
- TypeScript
- Vite
- SCSS
- REST API integration

### Backend
- Python
- FastAPI
- PostgreSQL
- AI integrations

### CMS / E-commerce
- WordPress
- WooCommerce (planned)

### Infrastructure
- Docker
- Docker Compose
- MySQL
- PostgreSQL

## Project Structure

```

ai-cyber-store/

├── backend/          # FastAPI application
├── database/         # Database related files
├── frontend/         # React application
├── wordpress/       # WordPress installation
└── docker-compose.yml

````

## Running the Project

Start containers:

```bash
docker compose up -d
````

Frontend:

```
http://localhost:5173
```

Backend API:

```
http://localhost:8000
```

WordPress:

```
http://localhost:8080
```

## Development

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend:

```bash
cd backend
uvicorn main:app --reload
```

## Planned Features

* AI product assistant
* Cybersecurity product catalog
* AI recommendations
* Security dashboard
* User accounts
* WooCommerce integration
* Monitoring with Zabbix
* Kubernetes deployment
* CI/CD pipeline

## Architecture

```
              React + TypeScript
                    |
                    |
                 FastAPI
                    |
          -------------------
          |                 |
     PostgreSQL          AI Services


WordPress + MySQL
        |
   E-commerce CMS
```

## Author

Marcin Potoczny

GitHub:
[https://github.com/marpot/](https://github.com/marpot/)

