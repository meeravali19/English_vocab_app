import streamlit as st
import json
import os
from rapidfuzz import fuzz

# Dataset path
DATASET_PATH = "datasets/vocab.json"

# Utility functions
def load_dataset():
    if not os.path.exists(DATASET_PATH):
        return []
    with open(DATASET_PATH, "r") as f:
        return json.load(f)

def save_dataset(data):
    with open(DATASET_PATH, "w") as f:
        json.dump(data, f, indent=4)

def add_word(word, meaning, synonyms, antonyms):
    data = load_dataset()
    existing_words = [entry["word"].lower() for entry in data]
    if word.lower() in existing_words:
        return False
    new_entry = {
        "word": word,
        "meaning": meaning,
        "synonyms": synonyms,
        "antonyms": antonyms
    }
    data.append(new_entry)
    save_dataset(data)
    return True

def update_word(index, word, meaning, synonyms, antonyms):
    data = load_dataset()
    data[index] = {
        "word": word,
        "meaning": meaning,
        "synonyms": synonyms,
        "antonyms": antonyms
    }
    save_dataset(data)

def delete_word(index):
    data = load_dataset()
    del data[index]
    save_dataset(data)

# Initialize session state
for key in ["synonyms", "antonyms", "edit_mode", "edit_index", "edit_loaded"]:
    if key not in st.session_state:
        if key in ["synonyms", "antonyms"]:
            st.session_state[key] = []
        elif key == "edit_loaded":
            st.session_state[key] = False
        else:
            st.session_state[key] = None

# Sidebar navigation
st.sidebar.title("📚 Vocabulary Manager")
menu = st.sidebar.radio("Go to", ["Add Word", "View Words", "Search"])

# ADD WORD PAGE
if menu == "Add Word":

    st.title("➕ Add / Edit Vocabulary Word")

    if st.session_state.edit_mode and not st.session_state.edit_loaded:
        data = load_dataset()
        entry = data[st.session_state.edit_index]
        st.session_state.word = entry['word']
        st.session_state.meaning = entry['meaning']
        st.session_state.synonyms = entry['synonyms']
        st.session_state.antonyms = entry['antonyms']
        st.session_state.edit_loaded = True

    word = st.text_input("Word", value=st.session_state.get("word", ""))
    meaning = st.text_area("Meaning", value=st.session_state.get("meaning", ""))

    # Synonyms form
    with st.form("synonym_form", clear_on_submit=True):
        syn_input = st.text_input("Enter synonym")
        submitted_syn = st.form_submit_button("Add Synonym")
        if submitted_syn and syn_input and syn_input not in st.session_state.synonyms:
            st.session_state.synonyms.append(syn_input)
    st.write("Current Synonyms:", st.session_state.synonyms)

    # Antonyms form
    with st.form("antonym_form", clear_on_submit=True):
        ant_input = st.text_input("Enter antonym")
        submitted_ant = st.form_submit_button("Add Antonym")
        if submitted_ant and ant_input and ant_input not in st.session_state.antonyms:
            st.session_state.antonyms.append(ant_input)
    st.write("Current Antonyms:", st.session_state.antonyms)

    if st.button("Save Word"):
        if word and meaning:
            if st.session_state.edit_mode:
                update_word(
                    st.session_state.edit_index,
                    word, meaning, st.session_state.synonyms, st.session_state.antonyms
                )
                st.success(f"✅ Word '{word}' updated successfully!")
            else:
                success = add_word(word, meaning, st.session_state.synonyms, st.session_state.antonyms)
                if success:
                    st.success(f"✅ Word '{word}' added successfully!")
                else:
                    st.warning(f"⚠️ The word '{word}' already exists.")
            # Reset everything
            st.session_state.synonyms = []
            st.session_state.antonyms = []
            st.session_state.word = ""
            st.session_state.meaning = ""
            st.session_state.edit_mode = None
            st.session_state.edit_index = None
            st.session_state.edit_loaded = False
        else:
            st.warning("⚠️ Please fill both word and meaning.")

# VIEW WORDS PAGE
elif menu == "View Words":
    st.title("📖 All Vocabulary Words")
    data = load_dataset()
    if data:
        for i, entry in enumerate(data):
            st.subheader(f"{i+1}. {entry['word']}")
            st.write("Meaning:", entry['meaning'])
            st.write("Synonyms:", ", ".join(entry['synonyms']))
            st.write("Antonyms:", ", ".join(entry['antonyms']))
            col1, col2 = st.columns(2)
            if col1.button("Edit", key=f"edit_{i}"):
                st.session_state.edit_mode = True
                st.session_state.edit_index = i
                st.session_state.edit_loaded = False  # very important!
                st.experimental_rerun()
            if col2.button("Delete", key=f"delete_{i}"):
                delete_word(i)
                st.experimental_rerun()
    else:
        st.info("No words in the dataset yet.")

# SEARCH PAGE with multiselect autocomplete + fuzzy search
elif menu == "Search":
    st.title("🔍 Search Vocabulary")

    data = load_dataset()
    all_words = [entry['word'] for entry in data]

    query = st.text_input("Start typing a word")

    selected_word = None
    if query:
        suggestions = [w for w in all_words if query.lower() in w.lower()]
        selected_list = st.multiselect("Suggestions (click one):", suggestions)

        if selected_list:
            selected_word = selected_list[0]
        else:
            selected_word = query
    else:
        selected_word = None

    if selected_word:
        query_lower = selected_word.lower()
        results = []

        for entry in data:
            score_word = fuzz.partial_ratio(query_lower, entry['word'].lower())
            score_meaning = fuzz.partial_ratio(query_lower, entry['meaning'].lower())
            score_syn = max([fuzz.partial_ratio(query_lower, syn.lower()) for syn in entry['synonyms']] + [0])
            score_ant = max([fuzz.partial_ratio(query_lower, ant.lower()) for ant in entry['antonyms']] + [0])

            if max(score_word, score_meaning, score_syn, score_ant) >= 60:
                results.append(entry)

        if results:
            st.success(f"Found {len(results)} approximate match(es):")
            for entry in results:
                st.subheader(entry['word'])
                st.write("Meaning:", entry['meaning'])
                st.write("Synonyms:", ", ".join(entry['synonyms']))
                st.write("Antonyms:", ", ".join(entry['antonyms']))
        else:
            st.warning("No matching words found.")
