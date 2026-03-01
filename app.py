# =============================================================================
# app.py  —  Flask application entry point
# =============================================================================
# Routes are thin: they just pass config data to Jinja2 templates.
# All content lives in config.py. All styling lives in static/css/style.css.
# =============================================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, render_template, request, redirect, url_for, flash
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
