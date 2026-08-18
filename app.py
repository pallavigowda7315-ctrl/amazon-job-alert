"""
app.py
=======
Main entry point. Run with:

    streamlit run app.py

This file is intentionally minimal. Every page (including Home) is
self-contained -- it calls its own `st.set_page_config`, applies the
shared theme, and renders its own sidebar -- because Streamlit executes
each page in `pages/` as an independent script run when selected from
the sidebar (it does NOT run app.py first). Trying to "share" rendering
by importing pages/Home.py's content into app.py causes either duplicate
rendering or a `set_page_config` conflict, depending on how it's wired --
so instead, app.py simply hands off to pages/Home.py immediately via
`st.switch_page`, which starts a fresh, independent run of that page.
"""
import streamlit as st

from config import APP_NAME, APP_ICON

st.set_page_config(
    page_title=f"{APP_NAME} | ECG Clinical Decision Support",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    st.switch_page("pages/Home.py")
except Exception:
    # st.switch_page requires Streamlit >= 1.27. Older versions fall back
    # to asking the user to click through manually.
    st.title(f"{APP_ICON} {APP_NAME}")
    st.write(
        "Please select **Home** from the sidebar page list to continue "
        "(automatic redirect requires Streamlit 1.27 or later -- see requirements.txt)."
    )
