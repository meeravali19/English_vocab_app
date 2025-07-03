import streamlit as st
import random
import json
from utils import load_dataset

# Initialize session state
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "radio_option" not in st.session_state:
    st.session_state.radio_option = "Select an option"

QUESTION_TYPES = ["meaning", "synonym", "antonym"]

def get_new_question():
    vocab_list = load_dataset()
    question = random.choice(vocab_list)
    
    # Randomly select question type based on data availability
    possible_types = ["meaning"]
    if "synonyms" in question and question["synonyms"]:
        possible_types.append("synonym")
    if "antonyms" in question and question["antonyms"]:
        possible_types.append("antonym")
    
    question_type = random.choice(possible_types)

    # Build options
    if question_type == "meaning":
        correct_answer = question["meaning"]
        other_meanings = [
            item["meaning"] for item in vocab_list if item["meaning"] != correct_answer
        ]
        sampled_distractors = random.sample(other_meanings, min(10, len(other_meanings)))
        options = sampled_distractors + [correct_answer]
    elif question_type == "synonym":
        correct_answer = random.choice(question["synonyms"])
        other_options = [
            syn for item in vocab_list for syn in item.get("synonyms", [])
            if syn != correct_answer
        ]
        sampled_distractors = random.sample(other_options, min(10, len(other_options)))
        options = sampled_distractors + [correct_answer]
    else:  # antonym
        correct_answer = random.choice(question["antonyms"])
        other_options = [
            ant for item in vocab_list for ant in item.get("antonyms", [])
            if ant != correct_answer
        ]
        sampled_distractors = random.sample(other_options, min(10, len(other_options)))
        options = sampled_distractors + [correct_answer]

    # Remove duplicates, shuffle and finalize options
    options = list(set(options))
    if len(options) > 4:
        options = random.sample(options, 4)
    if correct_answer not in options:
        options[random.randrange(len(options))] = correct_answer
    random.shuffle(options)

    return {
        "word": question["word"],
        "question_type": question_type,
        "correct_answer": correct_answer,
        "options": options
    }

def load_new_question():
    st.session_state.current_question = get_new_question()
    st.session_state.answered = False
    st.session_state.user_answer = None
    st.session_state.radio_option = "Select an option"

def vocabulary_practice():
    st.header("📝 Vocabulary Practice")

    # Safety check for any old session data
    if st.session_state.current_question is None or 'question_type' not in st.session_state.current_question:
        load_new_question()

    question_data = st.session_state.current_question
    word = question_data['word']
    question_type = question_data['question_type']

    question_text = {
        "meaning": f"What is the meaning of **{word}**?",
        "synonym": f"Choose a synonym for **{word}**:",
        "antonym": f"Choose an antonym for **{word}**:"
    }[question_type]

    st.write(question_text)

    options_with_placeholder = ["Select an option"] + question_data['options']
    user_answer = st.radio("Choose:", options_with_placeholder, 
                            index=options_with_placeholder.index(st.session_state.radio_option), 
                            key="radio_option")

    if st.button("Submit"):
        if user_answer == "Select an option":
            st.warning("⚠️ Please select an option before submitting.")
        else:
            st.session_state.user_answer = user_answer
            st.session_state.answered = True

    if st.session_state.answered:
        if st.session_state.user_answer == question_data['correct_answer']:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. Correct answer: {question_data['correct_answer']}")

        st.button("Next", on_click=load_new_question)

vocabulary_practice()
