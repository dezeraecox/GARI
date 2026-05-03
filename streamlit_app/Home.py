import streamlit as st

# ---- App Config ----
st.set_page_config(
    page_title="GARI",
    page_icon="streamlit_app/assets/logo.png",
    layout="wide"
)

# Set up navigation with Material Icons
# Icons at https://fonts.google.com/icons?icon.set=Material+Symbols
homePage = st.Page("pages/_home.py", title="Home", icon=":material/home:", default=True)
calculatorPage = st.Page("pages/_calculator.py", title="Risk Calculator", icon=":material/calculate:")
faqsPage = st.Page("pages/_faqs.py", title="FAQs", icon=":material/help:")
contactPage = st.Page("pages/_contact.py", title="Contact", icon=":material/mail:")

pg = st.navigation([homePage, calculatorPage, faqsPage, contactPage])
pg.run()
