import smtplib
from email.message import EmailMessage
import streamlit as st

logo_col, title_col = st.columns([1, 4])
with logo_col:
    st.image("streamlit_app/assets/logo.png", width=200)
with title_col:
    st.markdown("<h1 style='margin-bottom: 0;'>Contact</h1>", unsafe_allow_html=True)
    st.subheader("|*Questions, feedback, or suggestions? Get in touch!*")


def _get_contact_config():
    try:
        return st.secrets.get("contact", {})
    except Exception:
        return {}


def _send_contact_email(name, sender_email, message):
    cfg = _get_contact_config()
    if not cfg.get("enabled", False):
        return False, "Contact form is not configured yet."

    required_fields = ["recipient_email", "smtp_host", "smtp_port", "smtp_username", "smtp_password", "from_email"]
    missing = [field for field in required_fields if not cfg.get(field)]
    if missing:
        return False, "Contact form is not fully configured in Streamlit secrets."

    recipient_email = cfg.get("recipient_email")
    smtp_host = cfg.get("smtp_host")
    smtp_port = int(cfg.get("smtp_port"))
    smtp_username = cfg.get("smtp_username")
    smtp_password = cfg.get("smtp_password")
    from_email = cfg.get("from_email")
    use_starttls = bool(cfg.get("use_starttls", False))
    subject_prefix = cfg.get("subject_prefix", "[GARI Contact]")

    email_message = EmailMessage()
    email_message["Subject"] = f"{subject_prefix} New enquiry"
    email_message["From"] = from_email
    email_message["To"] = recipient_email
    if sender_email:
        email_message["Reply-To"] = sender_email

    body = (
        "New message submitted from the GARI app contact form.\n\n"
        f"Name: {name}\n"
        f"Email: {sender_email or 'Not provided'}\n\n"
        "Message:\n"
        f"{message}\n"
    )
    email_message.set_content(body)

    try:
        if use_starttls:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_username, smtp_password)
                server.send_message(email_message)
        else:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(email_message)
    except Exception:
        return False, "Could not send your message right now. Please try again later."

    return True, "Your message has been sent to the GARI team."




with st.form("contact_form", clear_on_submit=True):
    sender_name = st.text_input("Your name")
    sender_email = st.text_input("Your email")
    sender_message = st.text_area("Message", height=180)
    submitted = st.form_submit_button("Send message")

if submitted:
    if not sender_name.strip() or not sender_email.strip() or not sender_message.strip():
        st.error("Please enter your name, email, and message before submitting.")
    else:
        sent, feedback = _send_contact_email(
            name=sender_name.strip(),
            sender_email=sender_email.strip(),
            message=sender_message.strip(),
        )
        if sent:
            st.success(feedback)
        else:
            st.warning(feedback)
