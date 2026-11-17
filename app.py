
import streamlit as st
import base64
import os

from database import (
    initialize_database,
    register_user,
    authenticate_user,
    has_secretary
)

from dashboard import show_dashboard


# ---------- PAGE CONFIG ----------

st.set_page_config(
    page_title="Academic Scheduler",
    page_icon="📚",
    layout="wide"
)


# ---------- INITIALIZE DATABASE ----------

initialize_database()


# ---------- SESSION STATE ----------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "show_register" not in st.session_state:
    st.session_state.show_register = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = ""


# ---------- BACKGROUND IMAGE ----------

def get_base64_of_bin_file(filename):

    with open(filename, "rb") as file:
        data = file.read()

    return base64.b64encode(data).decode()


if not st.session_state.logged_in:

    if os.path.exists("background.png"):

        image = get_base64_of_bin_file("background.png")

        st.markdown(f"""
        <style>

        .stApp {{
            background-image:
            url("data:image/png;base64,{image}");

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        </style>
        """, unsafe_allow_html=True)


# ---------- CUSTOM STYLES ----------

if not st.session_state.logged_in:

    st.markdown("""
    <style>

    .hero-title {
        font-family: Arial Black, sans-serif;
        font-size: 65px;
        font-weight: 900;
        color: #004AAD;
        text-shadow: 3px 3px white;
    }

    .hero-tagline {
        font-size: 19px;
        color: white;
        background-color: #004AAD;
        padding: 10px 15px;
        border-radius: 7px;
        display: inline-block;
    }

    .stButton button {
        background-color: #004AAD;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
    }

    </style>
    """, unsafe_allow_html=True)


# ---------- MAIN APPLICATION ----------

if st.session_state.logged_in:

    show_dashboard()

else:

    col_empty, col_main, col_login = st.columns(
        [0.1, 1.4, 1]
    )


    # ---------- WEBSITE TITLE ----------

    with col_main:

        st.markdown(
            '<div style="margin-top:100px;">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<h1 class="hero-title">ACADEMIC<br>SCHEDULER</h1>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<p class="hero-tagline">'
            'Smarter Scheduling, Better Learning!'
            '</p>',
            unsafe_allow_html=True
        )

        st.markdown('</div>', unsafe_allow_html=True)


    # ---------- LOGIN AND REGISTRATION ----------

    with col_login:

        st.markdown(
            '<div style="background-color:rgba(255,255,255,0.93);'
            'padding:30px;border-radius:20px;'
            'margin-top:50px;">',
            unsafe_allow_html=True
        )


        # ---------- FIRST SECRETARY SETUP ----------

        if not has_secretary():

            st.subheader("Department Secretary Setup")

            st.info(
                "Create the first secretary account. "
                "This account will manage the department."
            )

            name = st.text_input(
                "Full Name",
                key="first_name"
            )

            email = st.text_input(
                "Email Address",
                key="first_email"
            )

            password = st.text_input(
                "Password",
                type="password",
                key="first_password"
            )

            confirm = st.text_input(
                "Confirm Password",
                type="password"
            )

            if st.button("Create Secretary Account"):

                if not all([name, email, password, confirm]):

                    st.error("Please complete all fields.")

                elif password != confirm:

                    st.error("Passwords do not match.")

                elif len(password) < 8:

                    st.error("Password must have at least 8 characters.")

                else:

                    success = register_user(
                        name,
                        email,
                        password,
                        "Secretary"
                    )

                    if success:

                        st.success(
                            "Secretary account created! "
                            "Please log in."
                        )

                        st.rerun()

                    else:

                        st.error("Email already registered.")


        # ---------- REGISTRATION ----------

        elif st.session_state.show_register:

            st.subheader("Instructor Registration")

            new_name = st.text_input("Full Name")

            new_email = st.text_input("Email Address")

            new_password = st.text_input(
                "Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            if st.button("Register"):

                if not all([
                    new_name,
                    new_email,
                    new_password,
                    confirm_password
                ]):

                    st.error("Please complete all fields.")

                elif new_password != confirm_password:

                    st.error("Passwords do not match.")

                elif len(new_password) < 8:

                    st.error("Password must have at least 8 characters.")

                else:

                    success = register_user(
                        new_name,
                        new_email,
                        new_password,
                        "Instructor"
                    )

                    if success:

                        st.success("Account successfully registered!")

                        st.session_state.show_register = False

                        st.rerun()

                    else:

                        st.error("Email already registered.")

            if st.button("Back to Login"):

                st.session_state.show_register = False

                st.rerun()


        # ---------- LOGIN ----------

        else:

            st.subheader("Department Login")

            email = st.text_input("Email Address")

            password = st.text_input(
                "Password",
                type="password"
            )

            if st.button("Login"):

                user = authenticate_user(
                    email,
                    password
                )

                if user:

                    st.session_state.logged_in = True

                    st.session_state.user_name = user["name"]

                    st.session_state.user_role = user["role"]

                    st.rerun()

                else:

                    st.error("Invalid email or password.")


            st.markdown("<hr>", unsafe_allow_html=True)

            if st.button("No account? Register Now!"):

                st.session_state.show_register = True

                st.rerun()


        st.markdown('</div>', unsafe_allow_html=True)
