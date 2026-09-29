import streamlit as st
from database import add_reminder, get_reminders, mark_reminder_done

def render_reminders(patient_id):
    st.header("💊 Daily Reminders")

    with st.form("add_reminder_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        title = col1.text_input("Reminder", placeholder="e.g. Take morning medication")
        time_of_day = col2.text_input("Time", placeholder="e.g. 8:00 AM")
        submitted = st.form_submit_button("Add reminder")
        if submitted and title and time_of_day:
            add_reminder(patient_id, title, time_of_day)
            st.rerun()

    st.divider()

    reminders = get_reminders(patient_id)

    if len(reminders) == 0:
        st.info("No reminders set yet. Add one above.")
        return

    for r in reminders:
        reminder_id, _, title, time_of_day, is_done, _ = r
        label = f"**{time_of_day}** — {title}"
        checked = st.checkbox(label, value=bool(is_done), key=f"reminder_{reminder_id}")
        if checked != bool(is_done):
            mark_reminder_done(reminder_id, checked)
            st.rerun()