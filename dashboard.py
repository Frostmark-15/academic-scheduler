
import streamlit as st
import pandas as pd

from database import get_connection

from scheduler import generate_schedule


# ---------- DASHBOARD ----------

def show_dashboard():

    user_name = st.session_state.user_name

    user_role = st.session_state.user_role


    # ---------- SIDEBAR ----------

    st.sidebar.title("📚 Academic Scheduler")

    st.sidebar.write(
        f"Welcome, **{user_name}**"
    )

    st.sidebar.caption(user_role)

    st.sidebar.divider()

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False

        st.session_state.user_name = ""

        st.session_state.user_role = ""

        st.rerun()


    # ---------- MAIN HEADER ----------

    st.title("📅 Academic Scheduling Dashboard")

    st.write(
        "Manage subjects, classrooms, and academic schedules."
    )

    st.divider()


    # ---------- NAVIGATION ----------

    if user_role == "Secretary":

        menu = st.sidebar.radio(
            "Navigation",
            [
                "Overview",
                "Classroom Management",
                "Subject Management",
                "Generate Timetable",
                "Master Schedule"
            ]
        )

    else:

        menu = st.sidebar.radio(
            "Navigation",
            [
                "Overview",
                "Submit Subject",
                "Master Schedule"
            ]
        )


    # ---------- LOAD DATA ----------

    with get_connection() as conn:

        subjects = pd.read_sql_query(
            "SELECT * FROM subjects",
            conn
        )

        rooms = pd.read_sql_query(
            "SELECT * FROM rooms",
            conn
        )

        schedules = pd.read_sql_query("""

            SELECT
                schedules.day,
                schedules.start_hour,
                schedules.end_hour,
                schedules.room,
                subjects.subject_code,
                subjects.subject_name,
                subjects.instructor,
                subjects.section

            FROM schedules

            JOIN subjects
            ON schedules.subject_id = subjects.id

        """, conn)


    # ---------- OVERVIEW ----------

    if menu == "Overview":

        st.subheader("Department Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Subjects",
            len(subjects)
        )

        col2.metric(
            "Available Classrooms",
            len(rooms)
        )

        col3.metric(
            "Scheduled Meetings",
            len(schedules)
        )

        st.divider()

        st.subheader("Recent Subject Submissions")

        if not subjects.empty:

            st.dataframe(
                subjects,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No subjects submitted yet.")


    # ---------- CLASSROOM MANAGEMENT ----------

    elif menu == "Classroom Management":

        st.subheader("🏫 Classroom Management")

        with st.form("room_form"):

            room_name = st.text_input(
                "Classroom Name",
                placeholder="Room 101"
            )

            capacity = st.number_input(
                "Classroom Capacity",
                min_value=1,
                value=30
            )

            submitted = st.form_submit_button(
                "Add Classroom"
            )

            if submitted:

                if not room_name.strip():

                    st.error("Enter a classroom name.")

                else:

                    try:

                        with get_connection() as conn:

                            conn.execute("""
                                INSERT INTO rooms(
                                    room_name,
                                    capacity
                                )
                                VALUES (?, ?)
                            """, (
                                room_name.strip(),
                                capacity
                            ))

                        st.success("Classroom added!")

                        st.rerun()

                    except Exception:

                        st.error(
                            "Classroom already exists or could not be saved."
                        )


        st.subheader("Available Classrooms")

        st.dataframe(
            rooms,
            use_container_width=True,
            hide_index=True
        )


    # ---------- SUBJECT SUBMISSION ----------

    elif menu == "Submit Subject":

        st.subheader("📖 Submit Subject Requirements")

        with st.form("instructor_subject_form"):

            code = st.text_input("Subject Code")

            name = st.text_input("Subject Name")

            instructor = st.text_input(
                "Instructor Name",
                value=user_name,
                disabled=True
            )

            section = st.text_input(
                "Class / Section",
                placeholder="2nd Year - A"
            )

            duration = st.number_input(
                "Hours per Meeting",
                min_value=1,
                max_value=8,
                value=2
            )

            meetings = st.number_input(
                "Meetings per Week",
                min_value=1,
                max_value=5,
                value=2
            )

            days = st.multiselect(
                "Preferred Meeting Days",
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday"
                ]
            )

            submitted = st.form_submit_button(
                "Submit Subject"
            )

            if submitted:

                if not all([code, name, section]):

                    st.error("Complete all required fields.")

                else:

                    with get_connection() as conn:

                        conn.execute("""

                            INSERT INTO subjects(
                                subject_code,
                                subject_name,
                                instructor,
                                section,
                                duration,
                                meetings,
                                preferred_days
                            )

                            VALUES (?, ?, ?, ?, ?, ?, ?)

                        """, (
                            code.strip(),
                            name.strip(),
                            user_name,
                            section.strip(),
                            duration,
                            meetings,
                            ",".join(days)
                        ))

                    st.success(
                        "Subject requirements submitted successfully!"
                    )

                    st.rerun()


    # ---------- SUBJECT MANAGEMENT ----------

    elif menu == "Subject Management":

        st.subheader("📚 Submitted Subjects")

        if subjects.empty:

            st.info("No subjects submitted.")

        else:

            st.dataframe(
                subjects,
                use_container_width=True,
                hide_index=True
            )

            subject_id = st.number_input(
                "Subject ID to delete",
                min_value=1,
                step=1
            )

            if st.button("Delete Subject"):

                with get_connection() as conn:

                    conn.execute(
                        "DELETE FROM schedules WHERE subject_id = ?",
                        (subject_id,)
                    )

                    conn.execute(
                        "DELETE FROM subjects WHERE id = ?",
                        (subject_id,)
                    )

                st.success("Subject deleted.")

                st.rerun()


    # ---------- GENERATE TIMETABLE ----------

    elif menu == "Generate Timetable":

        st.subheader("⚙️ Automatic Schedule Generator")

        st.write(
            "The system will evaluate instructor, "
            "class-section, and classroom availability."
        )

        if st.button(
            "Generate Department Timetable",
            type="primary"
        ):

            with get_connection() as conn:

                subject_records = [
                    dict(row)
                    for row in conn.execute(
                        "SELECT * FROM subjects"
                    ).fetchall()
                ]

                room_records = [
                    dict(row)
                    for row in conn.execute(
                        "SELECT * FROM rooms"
                    ).fetchall()
                ]

                result = generate_schedule(
                    subject_records,
                    room_records
                )

                if result is None:

                    st.error(
                        "No complete timetable could be generated. "
                        "Try adding rooms or adjusting requirements."
                    )

                else:

                    conn.execute(
                        "DELETE FROM schedules"
                    )

                    for item in result:

                        conn.execute("""

                            INSERT INTO schedules(
                                subject_id,
                                meeting_no,
                                day,
                                start_hour,
                                end_hour,
                                room
                            )

                            VALUES (?, ?, ?, ?, ?, ?)

                        """, (
                            item["subject_id"],
                            item["meeting_no"],
                            item["day"],
                            item["start_hour"],
                            item["end_hour"],
                            item["room"]
                        ))

                    st.success(
                        "Draft timetable generated successfully!"
                    )

                    st.rerun()


    # ---------- MASTER SCHEDULE ----------

    elif menu == "Master Schedule":

        st.subheader("📅 Department Master Timetable")

        if schedules.empty:

            st.info(
                "No timetable available. "
                "The secretary must generate one first."
            )

        else:

            days_order = {
                "Monday": 1,
                "Tuesday": 2,
                "Wednesday": 3,
                "Thursday": 4,
                "Friday": 5
            }

            schedules["day_order"] = (
                schedules["day"].map(days_order)
            )

            schedules = schedules.sort_values(
                ["day_order", "start_hour"]
            )

            display = schedules.drop(
                columns=["day_order"]
            ).copy()

            display["Time"] = display.apply(
                lambda row:
                f'{int(row["start_hour"]):02d}:00 - '
                f'{int(row["end_hour"]):02d}:00',
                axis=1
            )

            st.dataframe(
                display[
                    [
                        "day",
                        "Time",
                        "subject_code",
                        "subject_name",
                        "instructor",
                        "section",
                        "room"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            csv = display.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download Master Schedule",
                data=csv,
                file_name="department_schedule.csv",
                mime="text/csv"
            )
