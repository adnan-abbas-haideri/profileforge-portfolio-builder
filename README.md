# ProfileForge — Portfolio Builder

A responsive Flask portfolio builder. Edit your profile, skills, social links, and project cards. SQLite is the default database; MySQL is optional.

## Features
- Responsive modern portfolio UI
- Update profile details, bio, skills, location, and social links
- Add and delete portfolio projects
- SQLite by default; optional MySQL
- `/health` endpoint
- Dockerfile, Docker Compose, Jenkins declarative pipeline, and unit tests

## Run locally without MySQL
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000. SQLite is stored under `instance/profileforge.db`.

## Run with Docker Compose (SQLite)
```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
docker compose logs -f profileforge
```
Open http://localhost:5000. The named `profileforge-data` volume persists SQLite data.
Stop with `docker compose down`. To delete the database volume too, use `docker compose down -v`.

## Optional MySQL
Edit `.env` and set the URL and credentials below, using a strong password:
```dotenv
DATABASE_URL=mysql+pymysql://profileforge:replace-this-password@mysql:3306/profileforge
MYSQL_DATABASE=profileforge
MYSQL_USER=profileforge
MYSQL_PASSWORD=replace-this-password
MYSQL_ROOT_PASSWORD=replace-this-root-password
```
Then run:
```bash
docker compose --profile mysql up --build -d
docker compose --profile mysql ps
```
The MySQL container is only started when the `mysql` profile is selected. Existing SQLite records are not automatically copied into MySQL.

## Tests
```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Jenkins pipeline
The Jenkinsfile checks out code, installs dependencies, runs tests, builds a Docker image, and can optionally push it to Docker Hub.
1. Replace `YOUR_DOCKERHUB_USERNAME/profileforge` in `Jenkinsfile`.
2. Configure a Jenkins username/password credential with ID `DockerHubCred`; use a Docker Hub access token as the password.
3. Ensure the Jenkins agent has Python 3, Docker CLI, and access to a Docker daemon.
4. Run the job with `PUSH_IMAGE` enabled only when you want to publish the image.

This pipeline builds/pushes an image; it does not deploy to a server or Kubernetes.

## Important security note
This practice app has no login/authentication. Anyone who can access it can edit the same portfolio and delete projects. Do not expose it publicly until authentication and authorization are added. Change `SECRET_KEY` and all passwords before deployment.
