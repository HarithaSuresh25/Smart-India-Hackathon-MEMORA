import base64
import streamlit as st
from database import init_db, add_patient, log_session, get_sessions, get_all_patients, get_known_people
from game import render_recall_game, render_attention_game, render_recognition_game
from dashboard import render_dashboard
from reminders import render_reminders
from translations import t
from people_manager import render_people_manager

init_db()

# --- AUDIO HELPER FUNCTION ---
def play_audio(audio_filename):
    if st.session_state.get("current_audio") != audio_filename:
        st.session_state.current_audio = audio_filename
        try:
            with open(audio_filename, "rb") as f:
                audio_bytes = f.read()
                audio_b64 = base64.b64encode(audio_bytes).decode()
                audio_html = f"""
                    <audio autoplay style="display:none;">
                        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                    </audio>
                """
                st.components.v1.html(audio_html, height=0, width=0)
        except Exception as e:
            st.sidebar.warning(f"⚠️ Audio file not found: {audio_filename}")

# --- PATIENT SELECTOR ---
patients = get_all_patients()
if len(patients) == 0:
    patient_id = add_patient("Demo Patient")
else:
    patient_names = {p[0]: p[1] for p in patients}
    selected_name = st.sidebar.selectbox("Select patient", list(patient_names.values()))
    patient_id = [pid for pid, name in patient_names.items() if name == selected_name][0]

# --- LANGUAGE SELECTOR ---
lang = st.sidebar.selectbox("Language / ভাষা", ["English", "অসমীয়া (Assamese)"])
lang_code = "en" if lang == "English" else "as"

st.title(t("app_title", lang_code))

# --- VIEW SELECTOR ---
view = st.sidebar.radio("View", ["Play", "Manage Family & Friends", "Reminders", "Caregiver Dashboard"])

target_audio = None
game_choice = None

# --- DETERMINE AUDIO & GAME SELECTION ---
if "welcome_played" not in st.session_state:
    st.session_state.welcome_played = True
    target_audio = "welcome.mp3"

if view == "Play":
    game_options = {
        t("game_memory", lang_code): "Memory Recall",
        t("game_attention", lang_code): "Attention & Focus",
        t("game_recognition", lang_code): "Family & Friends Recognition",
    }
    # Unique key added to prevent DuplicateElementId error
    game_display_choice = st.selectbox(
        t("choose_game", lang_code), 
        list(game_options.keys()), 
        key="game_selector_selectbox"
    )
    game_choice = game_options[game_display_choice]

    if game_choice == "Memory Recall":
        target_audio = target_audio or "game_memory.mp3"
    elif game_choice == "Attention & Focus":
        target_audio = target_audio or "game_attention.mp3"
    else:
        target_audio = target_audio or "game_recognition.mp3"

elif view == "Manage Family & Friends":
    target_audio = target_audio or "view_manage.mp3"
elif view == "Reminders":
    target_audio = target_audio or "view_reminders.mp3"
elif view == "Caregiver Dashboard":
    target_audio = target_audio or "view_dashboard.mp3"

# --- GLOBAL AUDIO PLAYER COMPONENT ---
if target_audio:
    play_audio(target_audio)

# --- VIEW & GAME RENDERING ---
if view == "Play":
    if game_choice == "Memory Recall":
        result = render_recall_game(lang_code)

        if result is not None:
            correct = st.session_state.correct_count
            wrong = st.session_state.wrong_count
            difficulty = st.session_state.difficulty
            total = correct + wrong
            score = round((correct / total) * 100, 1) if total > 0 else 0

            log_session(
                patient_id=patient_id,
                game_type="memory_recall",
                difficulty_level=difficulty,
                correct_count=correct,
                wrong_count=wrong,
                domain="memory",
                score=score,
            )
            st.session_state.just_logged = True

        st.divider()
        with st.expander("🔍 Debug: view logged sessions"):
            sessions = get_sessions(patient_id)
            st.write(sessions)

    elif game_choice == "Attention & Focus":
        result = render_attention_game(lang_code)

        if result is not None:
            correct = st.session_state.att_correct_count
            wrong = st.session_state.att_wrong_count
            difficulty = st.session_state.att_difficulty
            total = correct + wrong
            score = round((correct / total) * 100, 1) if total > 0 else 0

            log_session(
                patient_id=patient_id,
                game_type="attention_focus",
                difficulty_level=difficulty,
                correct_count=correct,
                wrong_count=wrong,
                domain="attention",
                score=score,
            )
            st.session_state.att_just_logged = True

        st.divider()
        with st.expander("🔍 Debug: view logged sessions"):
            sessions = get_sessions(patient_id)
            st.write(sessions)

    else:
        people = get_known_people(patient_id)
        result = render_recognition_game(people, lang_code)

        if result is not None:
            correct = st.session_state.rec_correct_count
            wrong = st.session_state.rec_wrong_count
            difficulty = st.session_state.rec_difficulty
            total = correct + wrong
            score = round((correct / total) * 100, 1) if total > 0 else 0

            log_session(
                patient_id=patient_id,
                game_type="recognition",
                difficulty_level=difficulty,
                correct_count=correct,
                wrong_count=wrong,
                domain="recognition",
                score=score,
            )
            st.session_state.rec_just_logged = True

        st.divider()
        with st.expander("Debug: view logged sessions"):
            sessions = get_sessions(patient_id)
            st.write(sessions)

elif view == "Reminders":
    render_reminders(patient_id)

elif view == "Manage Family & Friends":
    render_people_manager(patient_id)

else:
    render_dashboard(patient_id)