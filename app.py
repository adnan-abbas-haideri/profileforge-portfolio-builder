import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False, default="Alex Morgan")
    headline = db.Column(db.String(160), nullable=False, default="Cloud & DevOps Engineer")
    bio = db.Column(db.Text, nullable=False, default="I build reliable systems and enjoy turning ideas into useful products.")
    email = db.Column(db.String(160), nullable=False, default="alex@example.com")
    location = db.Column(db.String(120), nullable=False, default="Lahore, Pakistan")
    github = db.Column(db.String(255), nullable=False, default="https://github.com/")
    linkedin = db.Column(db.String(255), nullable=False, default="https://linkedin.com/")
    website = db.Column(db.String(255), nullable=False, default="https://example.com")
    skills = db.Column(db.String(1000), nullable=False, default="Linux, Docker, Jenkins, Kubernetes, AWS")

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(500), nullable=False, default="")
    project_url = db.Column(db.String(255), nullable=False, default="")

def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-in-production")
    uri = os.getenv("DATABASE_URL", "sqlite:///profileforge.db")
    if uri.startswith("mysql://"):
        uri = uri.replace("mysql://", "mysql+pymysql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if test_config:
        app.config.update(test_config)
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if uri.startswith("sqlite:///"):
        db_file = uri.replace("sqlite:///", "", 1)
        if db_file != ":memory:" and not os.path.isabs(db_file):
            Path(app.instance_path).mkdir(parents=True, exist_ok=True)
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(Path(app.instance_path) / db_file)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if Profile.query.count() == 0:
            db.session.add(Profile())
            db.session.commit()
        if Project.query.count() == 0:
            db.session.add_all([
                Project(title="Cloud Notes", description="A notes app packaged for repeatable deployments.", technologies="Flask, Docker, SQLite", project_url="https://github.com/"),
                Project(title="CI/CD Pipeline", description="A pipeline that runs tests and builds a container image.", technologies="Jenkins, Git, Docker", project_url="https://github.com/")
            ])
            db.session.commit()

    @app.get("/")
    def index():
        profile = Profile.query.first()
        projects = Project.query.order_by(Project.id.desc()).all()
        skills = [s.strip() for s in profile.skills.split(",") if s.strip()]
        return render_template("index.html", profile=profile, projects=projects, skills=skills)

    @app.post("/profile")
    def update_profile():
        p = Profile.query.first()
        for field, limit in [("full_name",100),("headline",160),("bio",3000),("email",160),("location",120),("github",255),("linkedin",255),("website",255),("skills",1000)]:
            value = request.form.get(field, "").strip()[:limit]
            setattr(p, field, value)
        if not p.full_name:
            p.full_name = "Your Name"
        if not p.headline:
            p.headline = "Your professional headline"
        try:
            db.session.commit()
            flash("Profile saved successfully.", "success")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Could not save profile. Check database settings.", "error")
        return redirect(url_for("index") + "#edit-profile")

    @app.post("/projects")
    def add_project():
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not description:
            flash("Project title and description are required.", "error")
            return redirect(url_for("index") + "#projects")
        db.session.add(Project(title=title[:120], description=description[:2000],
            technologies=request.form.get("technologies", "").strip()[:500],
            project_url=request.form.get("project_url", "").strip()[:255]))
        try:
            db.session.commit()
            flash("Project added.", "success")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Could not add project.", "error")
        return redirect(url_for("index") + "#projects")

    @app.post("/projects/<int:project_id>/delete")
    def delete_project(project_id):
        p = db.session.get(Project, project_id)
        if p:
            db.session.delete(p)
            db.session.commit()
            flash("Project deleted.", "success")
        return redirect(url_for("index") + "#projects")

    @app.get("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return {"status":"ok","database":"connected"}, 200
        except SQLAlchemyError:
            return {"status":"error","database":"unavailable"}, 503
    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","5000")))
