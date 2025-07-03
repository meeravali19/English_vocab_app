import streamlit as st
import random
import json
import os

# Load dataset with caching
@st.cache_data
def load_idioms_dataset():
    data_path = os.path.join("datasets", "idioms.json")
    with open(data_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

# Generate a new question
def get_new_idiom_question():
    idioms = load_idioms_dataset()
    question = random.choice(idioms)

    # Randomly decide quiz type
    quiz_type = random.choice(["idiom_to_meaning", "meaning_to_idiom"])

    if quiz_type == "idiom_to_meaning":
        prompt = question["idiom"]
        correct_answer = question["meaning"]
        distractors = [item["meaning"] for item in idioms if item["meaning"] != correct_answer]
    else:
        prompt = question["meaning"]
        correct_answer = question["idiom"]
        distractors = [item["idiom"] for item in idioms if item["idiom"] != correct_answer]

    # Prepare options
    sampled_distractors = random.sample(distractors, min(10, len(distractors)))
    options = list(set(sampled_distractors + [correct_answer]))

    if len(options) > 4:
        options = random.sample(options, 4)
    if correct_answer not in options:
        options[random.randrange(len(options))] = correct_answer

    random.shuffle(options)

    return {
        "prompt": prompt,
        "correct_answer": correct_answer,
        "options": options,
        "quiz_type": quiz_type
    }

# Load new question into session state
def load_new_idiom_question():
    st.session_state.idiom_current_question = get_new_idiom_question()
    st.session_state.idiom_answered = False
    st.session_state.idiom_user_answer = None
    if "idiom_radio_option" in st.session_state:
        del st.session_state.idiom_radio_option

# Initialize session state
if "idiom_current_question" not in st.session_state:
    load_new_idiom_question()
if "idiom_answered" not in st.session_state:
    st.session_state.idiom_answered = False
if "idiom_user_answer" not in st.session_state:
    st.session_state.idiom_user_answer = None

# UI Title
st.title("🧠 Idioms MCQ Quiz")

# Get current question
question_data = st.session_state.idiom_current_question
prompt = question_data["prompt"]
quiz_type = question_data["quiz_type"]

if quiz_type == "idiom_to_meaning":
    st.markdown(f"### What is the **meaning** of this idiom:\n\n👉 **{prompt}**?")
else:
    st.markdown(f"### What is the **idiom** for this meaning:\n\n👉 **{prompt}**?")

# Display options with placeholder
options_with_placeholder = ["Select an option"] + question_data["options"]
user_answer = st.radio("Choose an answer:", options_with_placeholder, key="idiom_radio_option")

# Handle submission
if st.button("Submit"):
    if user_answer == "Select an option":
        st.warning("⚠️ Please select an option before submitting.")
    else:
        st.session_state.idiom_user_answer = user_answer
        st.session_state.idiom_answered = True

# Show result
if st.session_state.idiom_answered:
    if st.session_state.idiom_user_answer == question_data["correct_answer"]:
        st.success("✅ Correct!")
    else:
        st.error(f"❌ Incorrect. The correct answer is: **{question_data['correct_answer']}**")

    # Show Next button
    if st.button("Next"):
        load_new_idiom_question()
        st.experimental_rerun()
