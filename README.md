# ðŸš€ Resume Analyzer API

[![Python Version](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-ready **Resume Analyzer API** engineered with **Python 3.13**, **FastAPI**, **PostgreSQL**, **PyMuPDF**, and **spaCy NLP**. 

Designed specifically to help software engineering internship candidates optimize their resumes for **Applicant Tracking Systems (ATS)** and match their profiles against targeted job descriptions.

---

## ðŸ“Œ Architecture Overview

```mermaid
graph TD
    User([User / Client Application]) -->|HTTP Requests / Auth Header| API[FastAPI Web Application]
    
    subgraph Security & Auth
        API -->|JWT Authentication| AuthModule[Auth Service / Security]
    end

    subgraph Document Processing & NLP Engine
        API -->|Upload PDF| Uploads[(File Storage /uploads)]
        API -->|Extract Text| PyMuPDF[PyMuPDF Text Parser]
        PyMuPDF -->|Parsed Text| NLPEngine[spaCy & Regex NLP Engine]
        NLPEngine -->|Extract Skills & Keywords| ScoreEngine[ATS Scoring & Suggestions Engine]
        NLPEngine -->|Job Match Request| JobMatcher[Job Matcher Engine]
    end

    subgraph Data Persistence
        API -->|Async ORM queries| SQLAlchemy[SQLAlchemy 2.0]
        SQLAlchemy -->|Asyncpg / Aiosqlite| DB[(PostgreSQL / SQLite Database)]
        Alembic[Alembic Database Migrations] --> DB
    end
```

---

## âœ¨ Features

- **ðŸ” JWT User Authentication**: Secure registration (`POST /auth/register`) and login (`POST /auth/login`) with password hashing using `bcrypt`.
- **ðŸ“„ Resume PDF Upload**: Validates and stores PDF resumes securely with file metadata logging (`POST /upload-resume`).
- **ðŸ§  Automated ATS Resume Scoring**: Evaluates resumes on a **0â€“100 ATS Score scale** based on contact details, education, project impact metrics, skill density, and presence of key sections (`POST /analyze/{resume_id}`).
- **ðŸ› ï¸ Technical Skill & Missing Skill Detection**: Automatically categorizes 30+ technical skills (Python, FastAPI, Docker, SQL, React, etc.) and highlights critical missing competencies for software engineering internships.
- **ðŸ’¡ Actionable Suggestions Engine**: Provides automated advice (e.g. adding quantified project metrics, GitHub/LinkedIn links, cloud deployments).
- **ðŸŽ¯ Job Description Matcher (Bonus)**: Matches candidate resumes directly against specific job postings to output a **Match Percentage**, missing keywords, and tailored recommendations (`POST /job-match`).
- **ðŸ“œ Resume History**: Allows users to inspect all their past uploads and historical scores (`GET /my-resumes`).

---

## ðŸ› ï¸ Tech Stack

- **Framework**: Python 3.13 + [FastAPI](https://fastapi.tiangolo.com/)
- **Database & ORM**: PostgreSQL + [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/) + [Alembic](https://alembic.sqlalchemy.org/)
- **PDF Extraction**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- **NLP & Keyword Analytics**: [spaCy](https://spacy.io/) (`en_core_web_sm`) & Custom NLP Parsers
- **Authentication**: JWT (JSON Web Tokens) with `passlib` & `bcrypt`
- **Testing**: `pytest`, `pytest-asyncio`, and `httpx`
- **Containerization & CI/CD**: Docker, Docker Compose, GitHub Actions

---

## ðŸ“‚ Repository Structure

```
resume-analyzer-api/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ main.py                  # FastAPI Application Entrypoint
â”‚   â”œâ”€â”€ database.py              # Async SQLAlchemy Engine & Session
â”‚   â”œâ”€â”€ core/                    # App Settings & Structured Logger
â”‚   â”œâ”€â”€ dependencies/            # DB & JWT Auth Injections
â”‚   â”œâ”€â”€ models/                  # SQLAlchemy Database Models (User, Resume, Analysis)
â”‚   â”œâ”€â”€ schemas/                 # Pydantic Input/Output Validation Schemas
â”‚   â”œâ”€â”€ services/                # Business Logic (PDF, spaCy NLP, ATS Engine, Job Matcher)
â”‚   â”œâ”€â”€ routers/                 # API Endpoint Handlers
â”‚   â””â”€â”€ utils/                   # Security & Password Hashing Utilities
â”œâ”€â”€ uploads/                     # Stored Resume PDF Files
â”œâ”€â”€ tests/                       # Complete Pytest Test Suite
â”œâ”€â”€ alembic/                     # Alembic Database Migrations
â”œâ”€â”€ api/
â”‚   â””â”€â”€ index.py                 # Vercel Serverless Entrypoint
â”œâ”€â”€ Dockerfile                   # Production Multi-Stage Dockerfile
â”œâ”€â”€ docker-compose.yml           # PostgreSQL & API Orchestration
â”œâ”€â”€ render.yaml                  # Render Blueprint Configuration
â”œâ”€â”€ vercel.json                  # Vercel Serverless Deployment Config
â”œâ”€â”€ requirements.txt             # Python Package Dependencies
â”œâ”€â”€ .env.example                 # Environment Variable Blueprint
â””â”€â”€ README.md                    # Project Documentation
```

---

## ðŸ”Œ API Endpoints Reference

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/auth/register` | âŒ No | Register a new user account |
| `POST` | `/auth/login` | âŒ No | Authenticate user and receive JWT bearer token |
| `POST` | `/upload-resume` | âœ… Yes | Upload a PDF resume |
| `POST` | `/analyze/{resume_id}` | âœ… Yes | Perform PDF extraction, skill parsing, and ATS scoring |
| `GET` | `/score/{resume_id}` | âœ… Yes | Retrieve ATS score and detailed feedback |
| `GET` | `/my-resumes` | âœ… Yes | List all uploaded resumes for current user |
| `POST` | `/job-match` | âœ… Yes | Match resume against job description text |
| `GET` | `/` | âŒ No | Health check endpoint |

---

## ðŸš€ Local Setup & Installation Guide

### Prerequisites
- Python 3.13+
- Git
- Docker & Docker Compose (Optional for containerized run)

### Step 1: Clone Repository
```bash
git clone https://github.com/narendrakp222/Resume-Analyzer-API.git
cd "Resume Analyzer API"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies & Download spaCy Model
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Step 5: Run Database Migrations
```bash
alembic upgrade head
```

### Step 6: Start FastAPI Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open interactive API Documentation at: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## ðŸ³ Docker Setup

Run PostgreSQL and FastAPI seamlessly using Docker Compose:

```bash
docker-compose up --build -d
```
The API will be available at `http://localhost:8000/docs`.

---

## ðŸ§ª Running Automated Tests

Run unit, API integration, and validation tests using `pytest`:

```bash
pytest -v
```

---

## ðŸŒ Deployment Instructions

### 1. GitHub Push Commands
```bash
git init
git add .
git commit -m "feat: complete production-ready Resume Analyzer API"
git branch -M main
git remote add origin https://github.com/narendrakp222/Resume-Analyzer-API.git
git push -u origin main
```

### 2. Render Deployment (Recommended)
1. Log into [Render.com](https://render.com/).
2. Create a new **Blueprint** service connected to your GitHub repository.
3. Select `render.yaml` â€” Render will automatically set up the PostgreSQL database and FastAPI Web Service.
4. Set production environment variables:
   - `SECRET_KEY`: `<your-random-jwt-secret>`
   - `ALLOWED_ORIGINS`: `*`

### 3. Vercel Serverless Deployment
1. Import your GitHub repository into [Vercel](https://vercel.com/).
2. Vercel automatically detects `vercel.json` and routes requests to `api/index.py`.
3. Add environment variables in Vercel project settings:
   - `SECRET_KEY`
   - `DATABASE_URL` (PostgreSQL connection string from Supabase/Neon/Render PostgreSQL)

---

## ðŸ”® Future Improvements

- [ ] Support for DOCX resume file uploads.
- [ ] Integration with OpenAI / LLM APIs for AI-driven rewrite recommendations.
- [ ] Visual PDF resume formatting grader (font size, margin analysis).
- [ ] Multi-lingual skill extraction capabilities.
