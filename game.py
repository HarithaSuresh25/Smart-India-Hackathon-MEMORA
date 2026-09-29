import random
import streamlit as st
from translations import t

SHAPES = ["🔴", "🔵", "🟢", "🟡", "🟣", "🟠", "⚪", "⚫", "🟤", "🔶"]

def get_sequence_length(difficulty):
    return min(3 + difficulty, 8)

def generate_sequence(length):
    sequence = []
    for _ in range(length):
        choices = [s for s in SHAPES if not sequence or s != sequence[-1]]
        sequence.append(random.choice(choices))
    return sequence

def init_game_state():
    defaults = {
        "difficulty": 1,
        "correct_streak": 0,
        "wrong_streak": 0,
        "correct_count": 0,
        "wrong_count": 0,
        "stage": "show",
        "user_answer": [],
        "scored_this_round": False,
        "just_logged": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "sequence" not in st.session_state:
        length = get_sequence_length(st.session_state.difficulty)
        st.session_state.sequence = generate_sequence(length)

def start_new_round():
    length = get_sequence_length(st.session_state.difficulty)
    st.session_state.sequence = generate_sequence(length)
    st.session_state.stage = "show"
    st.session_state.user_answer = []

def reveal_answer_stage():
    st.session_state.stage = "answer"

def pick_shape(shape):
    st.session_state.user_answer.append(shape)

def adjust_difficulty(was_correct):
    if was_correct:
        st.session_state.correct_streak += 1
        st.session_state.wrong_streak = 0
        st.session_state.correct_count += 1
        if st.session_state.correct_streak >= 2:
            st.session_state.difficulty = min(st.session_state.difficulty + 1, 5)
            st.session_state.correct_streak = 0
    else:
        st.session_state.wrong_streak += 1
        st.session_state.correct_streak = 0
        st.session_state.wrong_count += 1
        if st.session_state.wrong_streak >= 2:
            st.session_state.difficulty = max(st.session_state.difficulty - 1, 1)
            st.session_state.wrong_streak = 0

def render_recall_game(lang_code="en"):
    st.header(t("memory_header", lang_code))
    init_game_state()

    st.write(f"**{t('difficulty_level', lang_code)}** {st.session_state.difficulty}")

    if st.session_state.stage == "show":
        st.write(t("memorize_sequence", lang_code))
        st.markdown(f"## {' '.join(st.session_state.sequence)}")
        st.button(t("hide_sequence_btn", lang_code), on_click=reveal_answer_stage)

    elif st.session_state.stage == "answer":
        length = len(st.session_state.sequence)
        st.write(t("what_was_sequence", lang_code))

        cols = st.columns(len(SHAPES))
        for i, shape in enumerate(SHAPES):
            cols[i].button(shape, key=f"shape_{i}", on_click=pick_shape, args=(shape,))

        st.write(t("your_answer_so_far", lang_code), " ".join(st.session_state.user_answer))

        if len(st.session_state.user_answer) == length:
            was_correct = st.session_state.user_answer == st.session_state.sequence
            if was_correct:
                st.success(t("correct", lang_code))
            else:
                st.error(f"{t('not_quite_seq', lang_code)} {' '.join(st.session_state.sequence)}")

            if not st.session_state.scored_this_round:
                adjust_difficulty(was_correct)
                st.session_state.scored_this_round = True
                st.session_state.just_logged = False

            def next_round():
                st.session_state.scored_this_round = False
                start_new_round()

            st.button(t("next_round", lang_code), on_click=next_round)

            if not st.session_state.get("just_logged", False):
                return was_correct
            return None

    return None

def get_grid_size(difficulty):
    # difficulty 1 = 3x3, difficulty 5 = 6x6
    return min(3 + difficulty - 1, 6)

def generate_grid(size, target_shape="🎯"):
    total_cells = size * size
    target_position = random.randint(0, total_cells - 1)
    grid = []
    for i in range(total_cells):
        if i == target_position:
            grid.append(target_shape)
        else:
            grid.append(random.choice([s for s in SHAPES if s != target_shape]))
    return grid, target_position

def init_attention_state():
    defaults = {
        "att_difficulty": 1,
        "att_correct_streak": 0,
        "att_wrong_streak": 0,
        "att_correct_count": 0,
        "att_wrong_count": 0,
        "att_scored_this_round": False,
        "att_just_logged": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "att_grid" not in st.session_state:
        size = get_grid_size(st.session_state.att_difficulty)
        st.session_state.att_grid, st.session_state.att_target_pos = generate_grid(size)

def att_start_new_round():
    size = get_grid_size(st.session_state.att_difficulty)
    st.session_state.att_grid, st.session_state.att_target_pos = generate_grid(size)
    st.session_state.att_scored_this_round = False
    st.session_state.att_just_logged = False

def att_adjust_difficulty(was_correct):
    if was_correct:
        st.session_state.att_correct_streak += 1
        st.session_state.att_wrong_streak = 0
        st.session_state.att_correct_count += 1
        if st.session_state.att_correct_streak >= 2:
            st.session_state.att_difficulty = min(st.session_state.att_difficulty + 1, 5)
            st.session_state.att_correct_streak = 0
    else:
        st.session_state.att_wrong_streak += 1
        st.session_state.att_correct_streak = 0
        st.session_state.att_wrong_count += 1
        if st.session_state.att_wrong_streak >= 2:
            st.session_state.att_difficulty = max(st.session_state.att_difficulty - 1, 1)
            st.session_state.att_wrong_streak = 0

def att_pick_cell(index):
    if st.session_state.att_scored_this_round:
        return
    was_correct = (index == st.session_state.att_target_pos)
    att_adjust_difficulty(was_correct)
    st.session_state.att_scored_this_round = True
    st.session_state.att_last_correct = was_correct

def render_attention_game(lang_code="en"):
    st.header(t("attention_header", lang_code))
    init_attention_state()

    st.write(f"**{t('difficulty_level', lang_code)}** {st.session_state.att_difficulty}")
    st.write(t("find_target", lang_code))

    grid = st.session_state.att_grid
    size = int(len(grid) ** 0.5)

    for row in range(size):
        cols = st.columns(size)
        for col in range(size):
            index = row * size + col
            if index < len(grid):
                cols[col].button(
                    grid[index],
                    key=f"cell_{index}_{len(grid)}",
                    on_click=att_pick_cell,
                    args=(index,),
                    disabled=st.session_state.att_scored_this_round,
                )

    if st.session_state.att_scored_this_round:
        if st.session_state.att_last_correct:
            st.success(t("correct", lang_code))
        else:
            st.error(t("not_quite_target", lang_code))

        st.button(t("next_round", lang_code), on_click=att_start_new_round)

        if not st.session_state.att_just_logged:
            return st.session_state.att_last_correct
    return None

def init_recognition_state(people):
    defaults = {
        "rec_difficulty": 1,
        "rec_correct_streak": 0,
        "rec_wrong_streak": 0,
        "rec_correct_count": 0,
        "rec_wrong_count": 0,
        "rec_scored_this_round": False,
        "rec_just_logged": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "rec_current_person" not in st.session_state:
        rec_new_round(people)

def rec_new_round(people):
    previous_id = st.session_state.rec_current_person[0] if "rec_current_person" in st.session_state else None
    candidates = [p for p in people if p[0] != previous_id]
    if not candidates:
        candidates = people
    target = random.choice(candidates)
    distractors = random.sample([p for p in people if p[0] != target[0]], min(2, len(people) - 1))
    options = [target] + distractors
    random.shuffle(options)
    st.session_state.rec_current_person = target
    st.session_state.rec_options = options
    st.session_state.rec_scored_this_round = False
    st.session_state.rec_just_logged = False

def rec_pick_answer(picked_id):
    if st.session_state.rec_scored_this_round:
        return
    was_correct = (picked_id == st.session_state.rec_current_person[0])
    if was_correct:
        st.session_state.rec_correct_streak += 1
        st.session_state.rec_wrong_streak = 0
        st.session_state.rec_correct_count += 1
    else:
        st.session_state.rec_wrong_streak += 1
        st.session_state.rec_correct_streak = 0
        st.session_state.rec_wrong_count += 1
    st.session_state.rec_scored_this_round = True
    st.session_state.rec_last_correct = was_correct

def render_recognition_game(people, lang_code="en"):
    st.header(t("recognition_header", lang_code))

    if len(people) < 3:
        st.warning(t("add_3_people", lang_code))
        return None

    init_recognition_state(people)

    _, _, name, relationship, image_path = st.session_state.rec_current_person
    st.write(t("who_is_this", lang_code))

    import os
    if os.path.exists(image_path):
        st.image(image_path, width=250)

    cols = st.columns(len(st.session_state.rec_options))
    for i, person in enumerate(st.session_state.rec_options):
        pid, _, pname, _, _ = person
        cols[i].button(pname, key=f"rec_{pid}", on_click=rec_pick_answer, args=(pid,),
                        disabled=st.session_state.rec_scored_this_round)

    if st.session_state.rec_scored_this_round:
        if st.session_state.rec_last_correct:
            st.success(f"{t('correct', lang_code)} {name}, {relationship.lower()}")
        else:
            st.error(f"{name}, {relationship.lower()}")

        def next_round():
            rec_new_round(people)

        st.button(t("next_round", lang_code), on_click=next_round)

        if not st.session_state.rec_just_logged:
            return st.session_state.rec_last_correct
    return None