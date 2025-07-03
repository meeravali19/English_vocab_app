import streamlit as st
import random
from utils import load_dataset

# Utility function to create spelling mistakes
def generate_misspellings(word):
    mistakes = set()

    if len(word) > 2:
        i = random.randint(0, len(word)-2)
        swapped = list(word)
        swapped[i], swapped[i+1] = swapped[i+1], swapped[i]
        mistakes.add(''.join(swapped))

    if len(word) > 3:
        i = random.randint(0, len(word)-1)
        removed = word[:i] + word[i+1:]
        mistakes.add(removed)

    i = random.randint(0, len(word))
    c = random.choice('abcdefghijklmnopqrstuvwxyz')
    added = word[:i] + c + word[i:]
    mistakes.add(added)

    i = random.randint(0, len(word)-1)
    c = random.choice('abcdefghijklmnopqrstuvwxyz')
    replaced = word[:i] + c + word[i+1:]
    mistakes.add(replaced)

    mistakes = list(mistakes)
    random.shuffle(mistakes)
    return mistakes[:3]

# Build word list from dataset
def collect_all_words(vocab_list):
    words = set()
    for entry in vocab_list:
        words.add(entry["word"])
        words.update(entry.get("synonyms", []))
        words.update(entry.get("antonyms", []))
    return list(words)

# Initialize session state
if 'spelling_question' not in st.session_state:
    st.session_state.spelling_question = None
if 'spelling_answered' not in st.session_state:
    st.session_state.spelling_answered = False

# Generate new question
def generate_new_spelling_question():
    vocab_list = load_dataset()
    all_words = collect_all_words(vocab_list)
    correct_word = random.choice(all_words)
    misspellings = generate_misspellings(correct_word)
    options = misspellings + [correct_word]
    random.shuffle(options)

    st.session_state.spelling_question = {
        'word': correct_word,
        'options': options
    }
    st.session_state.spelling_answered = False
    # 🔥 No direct reset of radio key here!

# Main spelling practice function
def spelling_quiz():
    st.header("📝 Spelling Practice (Endless Mode)")

    if st.session_state.spelling_question is None:
        generate_new_spelling_question()

    st.write("Select the correctly spelt word:")
    options = st.session_state.spelling_question['options']
    
    # Use unique key per question to reset radio each time!
    unique_key = f"spelling_option_{st.session_state.spelling_question['word']}"
    user_answer = st.radio("Choose:", options, key=unique_key)

    if st.button("Submit") and not st.session_state.spelling_answered:
        st.session_state.spelling_answered = True
        correct_word = st.session_state.spelling_question['word']
        if user_answer == correct_word:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. Correct answer: {correct_word}")

    if st.session_state.spelling_answered:
        if st.button("Next"):
            generate_new_spelling_question()
            st.experimental_rerun()  # 🔄 Force rerun to reset state cleanly

spelling_quiz()
