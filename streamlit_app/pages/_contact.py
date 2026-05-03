import streamlit as st
import urllib.request
import urllib.parse
import urllib.error

logo_col, title_col = st.columns([1, 4])
with logo_col:
    st.image("streamlit_app/assets/logo.png", width=200)
with title_col:
    st.markdown("<h1 style='margin-bottom: 0;'>Contact</h1>", unsafe_allow_html=True)
    st.subheader("|*Questions, feedback, or suggestions? Get in touch!*")


def _get_basin_endpoint():
    try:
        return st.secrets.get("contact", {}).get("basin_endpoint", "")
    except Exception:
        return ""


def _send_contact_form(name, sender_email, message):
    endpoint = _get_basin_endpoint()
    if not endpoint:
        return False, "Contact form is not configured."

    try:
        data = urllib.parse.urlencode({
            "name": name,
            "email": sender_email,
            "message": message,
        }).encode('utf-8')

        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'GARI-Streamlit/1.0'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            if status in [200, 201]:
                return True, "Your message has been sent to the GARI team. Thank you!"
            else:
                return False, f"Basin returned status {status}. Please try again later."
    except urllib.error.HTTPError as e:
        return False, f"HTTP error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection error: {e.reason}"
    except Exception as e:
        return False, f"Error: {str(e)}"




with st.form("contact_form", clear_on_submit=True):
    sender_name = st.text_input("Your name")
    sender_email = st.text_input("Your email")
    sender_message = st.text_area("Message", height=180)
    submitted = st.form_submit_button("Send message")

if submitted:
    if not sender_name.strip() or not sender_email.strip() or not sender_message.strip():
        st.error("Please enter your name, email, and message before submitting.")
    else:
        sent, feedback = _send_contact_form(
            name=sender_name.strip(),
            sender_email=sender_email.strip(),
            message=sender_message.strip(),
        )
        if sent:
            st.success(feedback)
        else:
            st.warning(feedback)
