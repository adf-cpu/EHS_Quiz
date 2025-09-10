import streamlit as st
import pandas as pd
import sqlite3
import random
from datetime import datetime
import json

# ---- Streamlit rerun compatibility ----
try:
    from streamlit import rerun as st_rerun
except ImportError:
    from streamlit import experimental_rerun as st_rerun

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Huawei Quiz App",
    page_icon="📝",
    layout="wide"
)

# Allowed usernames (change as needed)
ALLOWED_USERS = ["Farrukh Hussain", "Muhammad Shoaib", "Zafar Iqbal", "Kinza","Aqsa Kiran Latif","Attiq Ur Rehman Akbar"]
# ---------------- LOGIN ----------------
# CNIC to Name mapping
CNIC_TO_NAME = {
    "17301-5574430-1": "Bilal Shah",
    "35301-4576857-7": "Zafar Hayat",
    "35202-3657598-9": "Hafiz Ammar Zahid",
    "35202-7562070-9": "Muhammad Abdullah Qayyum",
    "35202-1937072-7": "Muhammad Subhan",
    "15607-0449650-5": "Shehryar Khan",
    "Kinza":"Kinza",
    "Attiq Ur Rehman Akbar":"Attiq Ur Rehman Akbar",
    "Farrukh Hussain":"Farrukh Hussain",
    "Muhammad Shoaib":"Muhammad Shoaib"
}

ALLOWED_CNICS = set(CNIC_TO_NAME.keys())

# ---------------- DATABASE ----------------
def init_database():
    """Initialize SQLite database for storing quiz results"""
    conn = sqlite3.connect('MegaHICquiz_results.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            quiz_file TEXT NOT NULL,
            score REAL NOT NULL,
            total_marks INTEGER NOT NULL,
            percentage REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            answers TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_quiz_result(username, quiz_file, score, total_marks, answers):
    conn = sqlite3.connect('MegaHICquiz_results.db')  # same DB use karo
    cursor = conn.cursor()
    percentage = (score / total_marks) * 100
    answers_json = json.dumps(answers)
    cursor.execute('''
        INSERT INTO quiz_results (username, quiz_file, score, total_marks, percentage, answers)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, quiz_file, score, total_marks, percentage, answers_json))
    conn.commit()
    conn.close()


# ---------------- HELPER: CHECK SUBMISSION ----------------
def has_already_submitted(cnic):
    """Check if this CNIC has already submitted the quiz"""
    conn = sqlite3.connect('MegaHICquiz_results.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM quiz_results WHERE username = ?', (CNIC_TO_NAME[cnic],))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# ---------------- QUIZ HELPERS ----------------
def load_questions_from_excel(file_path):
    """Load questions from Excel file"""
    try:
        df = pd.read_excel(file_path, header=1)  # Start from row 2 (row 1 = title)
        required_columns = ['question', 'question_type', 'options', 'correct_answer']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Excel file must contain columns: {', '.join(required_columns)}")
            return None
        # Normalize question_type just once
        df['question_type'] = df['question_type'].astype(str).str.strip()
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error loading quiz file: {str(e)}")
        return None

def parse_options(options_str, question_type):
    qt = str(question_type).lower()
    if qt == 'true/false':
        return ['True', 'False']
    elif qt in ['single_choice', 'multiple_choice']:
        if isinstance(options_str, str):
            options = [opt.strip() for opt in options_str.replace(';', ',').split(',')]
            return [opt for opt in options if opt]
        return []
    return []

def parse_correct_answer(correct_str, question_type):
    if str(question_type).lower() == 'multiple_choice':
        if isinstance(correct_str, str):
            return [ans.strip() for ans in correct_str.replace(';', ',').split(',')]
        return [correct_str]
    return correct_str

def check_answer(user_answer, correct_answer, question_type):
    if user_answer is None:
        return False
    question_type = str(question_type).lower()
    if question_type == 'multiple_choice':
        correct_set = set(parse_correct_answer(correct_answer, question_type))
        user_set = set(user_answer) if isinstance(user_answer, list) else {user_answer}
        return correct_set == user_set
    else:
        return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

def marks_for_type(question_type):
    qt = str(question_type).lower()
    if qt in ['true/false', 'single_choice']:
        return 2
    if qt == 'multiple_choice':
        return 5
    return 1  # fallback

# ---------------- DISPLAY FUNCTIONS ----------------
def display_question_progress():
    st.sidebar.markdown("### 📊 Quiz Progress")
    total_questions = len(st.session_state.shuffled_questions)
    current_question = st.session_state.current_question + 1
    st.sidebar.progress(current_question / total_questions if total_questions else 0)
    st.sidebar.markdown(f"Question **{current_question}** of **{total_questions}**")

    st.sidebar.markdown("### 📝 Question Status")
    for i in range(total_questions):
        answer = st.session_state.user_answers.get(i)
        if i == st.session_state.current_question:
            status = "🔹 Current"
            if answer:
                status = "🔹 Current (Answered)"
        elif answer:
            status = "✅ Answered"
        else:
            status = "⭕ Not Answered"
        if st.sidebar.button(f"Q{i+1}: {status}", key=f"nav_q_{i}", use_container_width=True):
            st.session_state.current_question = i
            st_rerun()

def display_current_question():
    current_idx = st.session_state.current_question
    question_data = st.session_state.shuffled_questions[current_idx]
    question_num = current_idx + 1
    st.markdown(f"### Question {question_num}")
    st.markdown(f"**{question_data['question']}**")

    question_type = str(question_data['question_type']).lower()
    options = parse_options(question_data['options'], question_type)
    current_answer = st.session_state.user_answers.get(current_idx)
    user_answer = None

    if question_type in ['true/false', 'single_choice']:
        # Default to first option if none selected (avoids Streamlit None index error)
        current_index = options.index(current_answer) if (current_answer in options) else 0
        user_answer = st.radio(
            "Select your answer:",
            options,
            key=f"q_{question_num}_radio",
            index=current_index
        )
    elif question_type == 'multiple_choice':
        st.write("Select all correct answers:")
        selected_options = []
        current_answer_list = current_answer if isinstance(current_answer, list) else []
        for i, option in enumerate(options):
            default_value = option in current_answer_list
            if st.checkbox(option, key=f"q_{question_num}_opt_{i}", value=default_value):
                selected_options.append(option)
        user_answer = selected_options

    if user_answer is not None:
        st.session_state.user_answers[current_idx] = user_answer

def display_navigation_buttons():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.current_question > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_question -= 1
                st_rerun()
        else:
            st.button("⬅️ Previous", disabled=True, use_container_width=True)
    with col3:
        total_questions = len(st.session_state.shuffled_questions)
        if st.session_state.current_question < total_questions - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.current_question += 1
                st_rerun()
        else:
            st.button("Next ➡️", disabled=True, use_container_width=True)
    with col2:
        total_questions = len(st.session_state.shuffled_questions)
        answered_count = sum(1 for ans in st.session_state.user_answers.values() if ans)
        if st.session_state.current_question == total_questions - 1 or answered_count == total_questions:
            if st.button("📋 Submit Quiz", type="primary", use_container_width=True):
                submit_quiz()

def submit_quiz():
    total_questions = len(st.session_state.shuffled_questions)
    score = 0
    total_marks = 0
    detailed_results = []
    questions = st.session_state.shuffled_questions

    for i, q in enumerate(questions):
        user_answer = st.session_state.user_answers.get(i, "Not Answered")  # default answer
        correct_answer = q['correct_answer']
        q_type = q['question_type']
        marks = marks_for_type(q_type)

        is_correct = False
        if user_answer != "Not Answered":
            is_correct = check_answer(user_answer, correct_answer, q_type)
            if is_correct:
                score += marks

        total_marks += marks

        detailed_results.append({
            'question': q['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'question_type': q_type,
            'marks': marks
        })

    save_quiz_result(st.session_state.username, st.session_state.quiz_file, score, total_marks, detailed_results)
    st.session_state.quiz_submitted = True
    st.session_state.final_score = score
    st.session_state.total_marks = total_marks
    st.session_state.detailed_results = detailed_results
    st_rerun()


def display_results():
    score = st.session_state.final_score
    total = st.session_state.total_marks
    percentage = (score / total) * 100 if total else 0.0
    st.success("🎉 Quiz Submitted Successfully!")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score}/{total}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        grade = "Needs Improvement 📚"
        if percentage >= 80:
            grade = "Excellent! 🌟"
        elif percentage >= 60:
            grade = "Good! 👍"
        st.metric("Grade", grade)

    st.markdown("### 📊 Detailed Results")
    for i, result in enumerate(st.session_state.detailed_results, 1):
        with st.expander(f"Question {i}: {'✅ Correct' if result['is_correct'] else '❌ Incorrect'}"):
            st.markdown(f"**Question:** {result['question']}")
            st.markdown(f"**Your Answer:** {result['user_answer']}")
            #st.markdown(f"**Correct Answer:** {result['correct_answer']}")
            st.markdown(f"**Marks for this question:** {result['marks']}")

    if st.button("🔄 Take Quiz Again", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st_rerun()

# ---------------- LOGIN ----------------

def login_screen():
    st.title("📝 Huawei Quiz App")
    st.subheader("Login Required")

    # Only CNIC input
    cnic = st.text_input("Enter your CNIC (e.g., 11111-1111111-1):")
    if st.button("Login"):
        cnic = cnic.strip()
        if cnic == "":
            st.error("⚠️ Please enter your CNIC")
        elif cnic not in ALLOWED_CNICS:
            st.error("❌ You are not authorized to take this quiz")
        elif has_already_submitted(cnic):
            st.warning(f"⚠️ {CNIC_TO_NAME[cnic]} has already submitted the quiz. You cannot take it again.")
        else:
            st.session_state.logged_in = True
            st.session_state.cnic = cnic
            st.session_state.username = CNIC_TO_NAME[cnic]  # Name from CNIC
            import os
            APP_DIR = r"D:\New_HICQuizApp"
            st.session_state.quiz_file = os.path.join(APP_DIR, "MEGA_QUIZ.xlsx")
            st_rerun()


# ---------------- MAIN ----------------
def main():
    init_database()
    if not st.session_state.get("logged_in", False):
        login_screen()
        return

    quiz_file = st.session_state.quiz_file
    username = st.session_state.username
    quiz_name = pd.read_excel(quiz_file, header=None, nrows=1).iloc[0, 0]
    st.title("📝 " + quiz_name)

    questions = load_questions_from_excel(quiz_file)
    if questions is None:
        return

    # -------- Category-wise selection + shuffle --------
    if 'shuffled_questions' not in st.session_state:
        # Normalize categories (support both styles from Excel)
        def norm(qt):
            return str(qt).strip().lower()

        tf_questions = [q for q in questions if norm(q['question_type']) in ['true/false', 'true_false']]
        sc_questions = [q for q in questions if norm(q['question_type']) in ['single_choice', 'single choice']]
        mc_questions = [q for q in questions if norm(q['question_type']) in ['multiple_choice', 'multiple choice']]

        needed_tf, needed_sc, needed_mc = 25, 25, 20

        if len(tf_questions) < needed_tf or len(sc_questions) < needed_sc or len(mc_questions) < needed_mc:
            st.warning(
                f"Not enough questions available for one or more categories. "
                f"Found TF={len(tf_questions)}, SC={len(sc_questions)}, MC={len(mc_questions)}. "
                f"Will select as many as available."
            )


        # Shuffle within each category
        random.shuffle(tf_questions)
        random.shuffle(sc_questions)
        random.shuffle(mc_questions)

        # Select required number of questions from each
        selected_tf = tf_questions[:needed_tf]
        selected_sc = sc_questions[:needed_sc]
        selected_mc = mc_questions[:needed_mc]

        # Combine in order: TF → SC → MC
        ordered_questions = selected_tf + selected_sc + selected_mc
        st.session_state.shuffled_questions = ordered_questions



        st.session_state.user_answers = {}
        st.session_state.current_question = 0
        st.session_state.quiz_submitted = False

    st.sidebar.markdown(f"**👤 User:** {st.session_state.username}")
    if 'cnic' in st.session_state:
        st.sidebar.markdown(f"**🆔 CNIC:** {st.session_state.cnic}")

    st.sidebar.markdown("---")

    if not st.session_state.quiz_submitted:
        display_question_progress()
        st.markdown("---")
        display_current_question()
        st.markdown("---")
        display_navigation_buttons()
    else:
        display_results()

if __name__ == "__main__":
    main()
