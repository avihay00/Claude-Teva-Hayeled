# =============================================================================
# app.py  —  Flask application entry point
# =============================================================================
# Routes are thin: they just pass config data to Jinja2 templates.
# All content lives in config.py. All styling lives in static/css/style.css.
# =============================================================================

import os
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

import config

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


# ─────────────────────────────────────────────────────────────────────────────
# Context processor — injects global variables into every template
# ─────────────────────────────────────────────────────────────────────────────

@app.context_processor
def inject_globals():
    """Makes these variables available in all templates automatically."""
    return {
        "SITE_NAME":        config.SITE_NAME,
        "SITE_TAGLINE":     config.SITE_TAGLINE,
        "SITE_DESCRIPTION": config.SITE_DESCRIPTION,
        "NAV_LINKS":        config.NAV_LINKS,
        "CONTACT_EMAIL":    config.CONTACT_EMAIL,
        "CONTACT_ADDRESS":  config.CONTACT_ADDRESS,
        "CONTACT_PHONE":    config.CONTACT_PHONE,
        "SCHOOL_YEAR":      config.SCHOOL_YEAR,
        # True when building the static GitHub Pages export (set by freeze.py)
        "STATIC_BUILD":     os.getenv("STATIC_BUILD", "false").lower() == "true",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template(
        "index.html",
        hero=config.HOME_HERO,
        highlights=config.HOME_HIGHLIGHTS,
        stats=config.HOME_STATS,
        intro=config.HOME_INTRO,
        quote=config.HOME_QUOTE,
        quote_author=config.HOME_QUOTE_AUTHOR,
        open_day=config.OPEN_DAY,
    )


@app.route("/about/")
def about():
    return render_template("about.html", page=config.ABOUT_PAGE)


@app.route("/info/")
def info():
    return render_template(
        "info.html",
        page=config.INFO_PAGE,
        start_of_year=config.START_OF_YEAR,
    )


@app.route("/curriculum/")
def curriculum():
    return render_template("curriculum.html", page=config.CURRICULUM_PAGE)


@app.route("/menu/")
def menu():
    return render_template("menu.html", page=config.MENU_PAGE)


@app.route("/calendar/")
def calendar():
    return render_template("calendar.html", page=config.CALENDAR_PAGE)


@app.route("/contact/", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        email   = request.form.get("email", "").strip()
        phone   = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()

        if name and email and message:
            _send_contact_email(name, email, phone, message)
            flash(config.CONTACT_PAGE["form_success"], "success")
            return redirect(url_for("contact"))
        else:
            flash(config.CONTACT_PAGE["form_error"], "error")

    return render_template("contact.html", page=config.CONTACT_PAGE)


@app.route("/gallery/")
def gallery():
    folder = os.path.join(app.root_path, "static", "images", "gallery")
    os.makedirs(folder, exist_ok=True)
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    images = sorted(
        f for f in os.listdir(folder)
        if os.path.splitext(f.lower())[1] in allowed
    )
    return render_template("gallery.html", page=config.GALLERY_PAGE, images=images)


# ─────────────────────────────────────────────────────────────────────────────
# Admin — only registered on the live server (skipped during static build)
# ─────────────────────────────────────────────────────────────────────────────

_STATIC_BUILD = os.getenv("STATIC_BUILD", "false").lower() == "true"

if not _STATIC_BUILD:
    _ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    _GALLERY_FOLDER = os.path.join(os.path.dirname(__file__), "static", "images", "gallery")
    _MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB

    def _require_admin(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get("admin"):
                return redirect(url_for("admin_login"))
            return f(*args, **kwargs)
        return decorated

    @app.route("/admin/login/", methods=["GET", "POST"])
    def admin_login():
        if session.get("admin"):
            return redirect(url_for("admin_gallery"))
        if request.method == "POST":
            password = request.form.get("password", "")
            admin_pw = os.getenv("ADMIN_PASSWORD", "")
            if admin_pw and password == admin_pw:
                session["admin"] = True
                return redirect(url_for("admin_gallery"))
            flash("סיסמה שגויה.", "error")
        return render_template("admin_login.html")

    @app.route("/admin/logout/")
    def admin_logout():
        session.pop("admin", None)
        return redirect(url_for("home"))

    @app.route("/admin/gallery/")
    @_require_admin
    def admin_gallery():
        os.makedirs(_GALLERY_FOLDER, exist_ok=True)
        images = sorted(
            f for f in os.listdir(_GALLERY_FOLDER)
            if os.path.splitext(f.lower())[1] in _ALLOWED_EXTS
        )
        return render_template("admin_gallery.html", images=images)

    @app.route("/admin/gallery/upload/", methods=["POST"])
    @_require_admin
    def admin_upload():
        files = request.files.getlist("images")
        saved = 0
        for file in files:
            if not file or not file.filename:
                continue
            ext = os.path.splitext(file.filename.lower())[1]
            if ext not in _ALLOWED_EXTS:
                flash(f"סוג קובץ לא נתמך: {file.filename}", "error")
                continue
            # Read to check size before saving
            data = file.read()
            if len(data) > _MAX_UPLOAD_BYTES:
                flash(f"הקובץ גדול מדי (מקסימום 8MB): {file.filename}", "error")
                continue
            filename = uuid.uuid4().hex + ext
            dest = os.path.join(_GALLERY_FOLDER, filename)
            with open(dest, "wb") as fh:
                fh.write(data)
            saved += 1
        if saved:
            flash(f"הועלו {saved} תמונות בהצלחה.", "success")
        return redirect(url_for("admin_gallery"))

    @app.route("/admin/gallery/delete/<filename>/", methods=["POST"])
    @_require_admin
    def admin_delete(filename):
        # Validate: no path traversal, must be in gallery folder
        safe = os.path.basename(filename)
        ext = os.path.splitext(safe.lower())[1]
        if ext not in _ALLOWED_EXTS:
            flash("שגיאה: קובץ לא תקין.", "error")
            return redirect(url_for("admin_gallery"))
        path = os.path.join(_GALLERY_FOLDER, safe)
        if os.path.isfile(path):
            os.remove(path)
            flash(f"התמונה נמחקה.", "success")
        else:
            flash("הקובץ לא נמצא.", "error")
        return redirect(url_for("admin_gallery"))


# ─────────────────────────────────────────────────────────────────────────────
# Email helper
# ─────────────────────────────────────────────────────────────────────────────

def _send_contact_email(name: str, email: str, phone: str, message: str) -> None:
    """
    Sends a contact-form submission to CONTACT_EMAIL.
    Configure SMTP credentials in .env to enable real sending.
    Without credentials, submissions are logged to the console only.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not all([smtp_host, smtp_user, smtp_pass]):
        # SMTP not configured — print to console (development mode)
        print(f"\n[Contact Form] ── New submission ──────────────────")
        print(f"  Name:    {name}")
        print(f"  Email:   {email}")
        print(f"  Phone:   {phone}")
        print(f"  Message: {message}")
        print(f"────────────────────────────────────────────────────\n")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"פנייה חדשה מהאתר — {name}"
    msg["From"]    = smtp_user
    msg["To"]      = config.CONTACT_EMAIL
    msg["Reply-To"] = email

    body = (
        f"שם: {name}\n"
        f"אימייל: {email}\n"
        f"טלפון: {phone or '—'}\n\n"
        f"הודעה:\n{message}"
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as exc:
        print(f"[Email error] {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    port  = int(os.getenv("PORT", 5000))
    app.run(debug=debug, port=port, host="0.0.0.0")
