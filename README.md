# ACEest Fitness & Gym – CI/CD Pipeline Implementation


## Assignment
Name:  Siva Chokkalingam S
reg no: 2024TM93515

## Project Overview

This project implements a complete CI/CD pipeline for a fitness management application. The focus is on ensuring code reliability, automated testing, consistent environments, and reliable build validation using DevOps practices.

The application provides backend APIs for:

* Managing client profiles
* Calculating calorie requirements
* Tracking weekly fitness progress

---

## System Architecture

```
Developer → GitHub → GitHub Actions → Jenkins → Docker
```

* GitHub Actions: Continuous Integration
* Jenkins: Build validation layer
* Docker: Environment consistency
* Pytest: Automated testing

---

## Project Structure

```
project/
│
├── Aceestver.py
├── logic.py
├── test_logic.py
├── test_app.py
├── requirements.txt
├── Dockerfile
├── .github/workflows/main.yml
├── README.md
```

---

## Setup Instructions

### Clone Repository

```
git clone <your-repo-url>
cd project
```

---

### Install Dependencies

```
pip install -r requirements.txt
```

---

### Run Application

```
python app.py
```

Access:

```
http://localhost:5000/init
```

---

## Running Tests

```
pytest -q
```

Expected output:

```
11 passed
```

---

## Docker Setup

### Build Image

```
docker build -t aceest-app .
```

### Run Container

```
docker run -p 5000:5000 aceest-app
```

---

## CI/CD Pipeline

### GitHub Actions

Triggered on:

* push
* pull_request

Pipeline stages:

1. Checkout code
2. Install dependencies
3. Run tests
4. Build Docker image

---

### Jenkins Build Process

Jenkins performs:

1. Pull latest code from GitHub
2. Install dependencies
3. Execute test suite
4. Build Docker image

This acts as a secondary validation layer to ensure the application builds correctly in a clean environment.

---

### Jenkins / Windows Prerequisites

For a local Windows Jenkins agent, ensure the following are installed and available on the agent PATH:

* `python` and `pip`
* `pytest`
* `docker`
* `kubectl`
* `SonarQube Scanner` tool configured in Jenkins as `SonarQubeScanner`
* `SonarQube` server configured in Jenkins with the same name
* Jenkins credentials id `docker-hub-credentials` for Docker Hub login
* `SONAR_TOKEN` available to the pipeline as a secure environment variable or credential

If you are running Jenkins and SonarQube locally on Windows, the pipeline should use `bat` commands instead of Unix `sh` commands.

---

## Key Features Implemented

* Automated testing using Pytest
* Docker-based containerization
* CI pipeline using GitHub Actions
* Build verification using Jenkins
* Modular code design

---

## Design Approach

* Separation of concerns:

  * API layer (Flask)
  * Business logic (logic.py)
  * Testing layer (Pytest)

* Fail-fast strategy:

  * Tests run before Docker build

* Environment consistency:

  * Docker ensures identical runtime

---

## API Endpoints

| Method | Endpoint       | Description         |
| ------ | -------------- | ------------------- |
| GET    | /init          | Initialize database |
| POST   | /client        | Save client         |
| GET    | /client/<name> | Load client         |
| POST   | /progress      | Save progress       |

---

## Validation Strategy

* Unit tests validate core logic
* CI pipeline ensures code integrity
* Jenkins verifies independent build success
* Docker ensures portability

---