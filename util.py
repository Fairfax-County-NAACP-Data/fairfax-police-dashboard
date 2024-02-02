import streamlit as st

stops_per_1000_txt = "Number of stops that occur per year (for a group) for every 1000 people (of that group) in the county population. "+\
    "See the About section for details on the population estimates."

def text_file(file):
    with open(file) as f:
        text = f.read()

    return text


def _get_index(filter, data, default=0):
    if 'query' in st.session_state and filter in st.session_state['query']:
        val = st.session_state['query'][filter]
        val = int(val) if val.isnumeric() else val
    if 'query' in st.session_state and filter in st.session_state['query'] and val in data:
        return [k for k,x in enumerate(data) if x==val][0]
    else:
        return default