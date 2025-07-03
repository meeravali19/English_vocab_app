import streamlit as st
import random
import json
import os

# Load dataset with caching
@st.cache_data
def load_dataset():
    data_path = os.path.join("datasets", "onewords.json")
    with open(data_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

# Generate a new question
def get_new_question():
    vocab_list = load_dataset()
    question = random.choice(vocab_list)
    correct_answer = question["meaning"]

    # Create distractors
    other_meanings = [item["meaning"] for item in vocab_list if item["meaning"] != correct_answer]
    sampled_distractors = random.sample(other_meanings, min(10, len(other_meanings)))
    options = list(set(sampled_distractors + [correct_answer]))

    # Limit to 4 options
    if len(options) > 4:
        options = random.sample(options, 4)
    if correct_answer not in options:
        options[random.randrange(len(options))] = correct_answer
    random.shuffle(options)

    return {
        "word": question["word"],
        "correct_answer": correct_answer,
        "options": options
    }

# Load new question into scoped session keys
def load_new_question():
    st.session_state.oneword_current_question = get_new_question()
    st.session_state.oneword_answered = False
    st.session_state.oneword_user_answer = None
    if "oneword_radio_option" in st.session_state:
        del st.session_state.oneword_radio_option

# Initialize scoped session state
if "oneword_current_question" not in st.session_state:
    load_new_question()
if "oneword_answered" not in st.session_state:
    st.session_state.oneword_answered = False
if "oneword_user_answer" not in st.session_state:
    st.session_state.oneword_user_answer = None

# UI Title
st.title("🧠 One Word Substitution Quiz")

# Get question data
question_data = st.session_state.oneword_current_question
st.markdown(f"### What is the **one word substitution** for: **{question_data['word']}**?")

# Show options
options_with_placeholder = ["Select an option"] + question_data["options"]
user_answer = st.radio("Choose an answer:", options_with_placeholder,
                       key="oneword_radio_option")

# Handle submission
if st.button("Submit"):
    if user_answer == "Select an option":
        st.warning("⚠️ Please select an option before submitting.")
    else:
        st.session_state.oneword_user_answer = user_answer
        st.session_state.oneword_answered = True

# Show result
if st.session_state.oneword_answered:
    if st.session_state.oneword_user_answer == question_data["correct_answer"]:
        st.success("✅ Correct!")
    else:
        st.error(f"❌ Incorrect. The correct answer is: **{question_data['correct_answer']}**")

    # Next question
    if st.button("Next"):
        load_new_question()
        st.rerun()
