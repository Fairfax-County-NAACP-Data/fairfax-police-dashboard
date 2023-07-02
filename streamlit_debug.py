from tqdm import tqdm

class Progress:
    def __init__(self, val, text) -> None:
        self.nrows = 1000
        self.last = 0
        self.bar = tqdm(desc=text, total=self.nrows, leave=False) 

    def progress(self, val, text):
        x = val - self.last
        self.last = val
        self.bar.update(x*self.nrows)



def add_debug(st):
    st.session_state = {}
    st.progress = Progress