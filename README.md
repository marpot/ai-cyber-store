# AI Cyber Store 🤖🛒

**Experimental e-commerce application combining React, WordPress/WooCommerce and a FastAPI recommendation service.**

AI Cyber Store is a portfolio project exploring how an AI-assisted product discovery experience can be integrated with a modern storefront and WordPress-based commerce stack.

Unlike a static AI demo, the project includes a dedicated recommendation service, multilingual product recommendations, a React chat interface and a containerized WordPress environment.

## ✨ Implemented Features

- React + TypeScript storefront foundation
- Responsive AI recommendation chat interface
- FastAPI recommendation service
- Polish and English recommendation flow
- Localized product names, descriptions and pricing
- Product recommendation cards embedded directly in assistant messages
- Confidence thresholding for low-confidence/general queries
- Frontend language synchronization with the recommendation API
- WordPress/WooCommerce API integration foundation
- Dockerized WordPress, frontend and recommendation-service environment
- Automatic local MySQL initialization from a development database seed
- Frontend type checking and linting workflow
- Pytest-based recommendation-service tests and coverage commands

## 🧱 Architecture

```text
React + TypeScript storefront
          │
          ├──────────────► WordPress / WooCommerce
          │                    │
          │                    ▼
          │                  MySQL
          │
          ▼
FastAPI Recommendation Service
          │
          ├── recommendation / language logic
          ├── product matching
          └── AI integration layer
```

The React application owns the customer-facing experience. WordPress/WooCommerce provides the commerce integration layer, while the Python service is responsible for recommendation-specific logic rather than placing AI behavior directly inside the frontend.

## 🛠 Tech Stack

**Frontend:** React · TypeScript · Vite · SCSS · React Router · react-i18next  
**Backend / AI:** Python · FastAPI · PostgreSQL  
**CMS / Commerce:** WordPress · WooCommerce · MySQL  
**Testing / Quality:** Pytest · pytest-cov · TypeScript type checking · oxlint  
**Infrastructure:** Docker · Docker Compose · Make

## 📂 Project Structure

```text
ai-cyber-store/
├── frontend/                 # React + TypeScript storefront
├── recommendation-service/   # FastAPI recommendation service
├── wordpress/                # WordPress files / integration
├── docker-compose.yml
├── Makefile
└── README.md
```

## 🚀 Running Locally

### Requirements

- Docker
- Docker Compose

Create local environment files from the included examples:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
cp recommendation-service/.env.example recommendation-service/.env
```

Do not commit real `.env` files or credentials.

Build and start the application:

```bash
docker compose up -d --build
```

Check services:

```bash
docker compose ps
```

Stop the stack:

```bash
docker compose down
```

### Local Services

```text
Frontend:  http://localhost:5173
FastAPI:   http://localhost:8000
WordPress: http://localhost:8080
```

## 🧪 Code Quality & Tests

Frontend checks:

```bash
make typecheck
make lint
make test
```

Recommendation-service tests:

```bash
make test-pytest
make test-coverage
```

Useful Docker commands are also exposed through the Makefile for building, starting and inspecting the local environment.

## 🌍 Recommendation Experience

The recommendation UI supports both Polish and English. The selected frontend language is sent to the FastAPI service, allowing responses, product data and pricing presentation to follow the active locale.

Recommended products are rendered inside assistant messages, keeping the product-discovery flow conversational instead of separating AI responses from a disconnected result grid.

A confidence threshold prevents the recommendation layer from forcing a product intent when the input is a greeting or does not match the supported recommendation categories strongly enough.

## 📌 Project Status

**Functional prototype / active portfolio project.**

The recommendation service, multilingual chat experience and containerized application foundation are implemented. The repository should be treated as an experimental AI-commerce project rather than a production-ready store.

Potential future work includes deeper WooCommerce integration, user accounts, broader catalog/search capabilities, deployment automation and monitoring.

## 📸 Screenshots

Screenshots will be added during the final portfolio-polish stage.

## 👨‍💻 Author

**Marcin Potoczny**  
[GitHub profile](https://github.com/marpot)
