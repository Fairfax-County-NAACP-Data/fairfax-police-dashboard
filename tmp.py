import streamlit as st

with st.sidebar:
    if st.button(label="Action", 
                     help="This is a very long message that extends to multiple lines\n\nand when it does, it is off the screen!!!"):
        print('hello world')
