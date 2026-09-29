import streamlit as st
import os
from database import add_known_person, get_known_people

UPLOAD_DIR = "uploaded_photos"

def render_people_manager(patient_id):
    st.header("👨‍👩‍👧 Manage Family & Friends")
    st.write("Upload photos of people your loved one should practice recognizing.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    with st.form("add_person_form", clear_on_submit=True):
        name = st.text_input("Name")
        relationship = st.text_input("Relationship", placeholder="e.g. Daughter, Grandson, Friend")
        photo = st.file_uploader("Photo", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Add person")

        if submitted and name and relationship and photo:
            file_path = os.path.join(UPLOAD_DIR, f"{patient_id}_{name}_{photo.name}")
            with open(file_path, "wb") as f:
                f.write(photo.getbuffer())
            add_known_person(patient_id, name, relationship, file_path)
            st.success(f"Added {name}!")
            st.rerun()

    st.divider()
    st.subheader("Current people")

    people = get_known_people(patient_id)
    if len(people) == 0:
        st.info("No people added yet. Add at least 3 to unlock the recognition game.")
        return

    cols = st.columns(4)
    for i, person in enumerate(people):
        _, _, name, relationship, image_path = person
        with cols[i % 4]:
            if os.path.exists(image_path):
                st.image(image_path, width=120)
            st.caption(f"{name} ({relationship})")