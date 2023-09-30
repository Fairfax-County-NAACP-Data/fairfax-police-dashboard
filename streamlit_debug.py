from tqdm import tqdm
from contextlib import contextmanager, nullcontext

class Progress:
    def __init__(self, val, text) -> None:
        self.nrows = 1000
        self.last = 0
        self.bar = tqdm(desc=text, total=self.nrows, leave=False) 

    def progress(self, val, text):
        x = val - self.last
        self.last = val
        self.bar.update(x*self.nrows)

def set_page_config(*args, **kwargs):
    pass

def cache_data(*args, **kwargs):
    def wrap(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return wrap


@contextmanager
def fake_context_manager(*args, **kwds):
    try:
        yield None
    finally:
        pass

def empty(*args, **kwargs):
    return fake_context_manager()

def columns(count):
    return (fake_context_manager() for _ in range(count))

def tabs(tab_names):
    return (fake_context_manager() for _ in range(len(tab_names)))

def selectbox(*args, **kwargs):
    return "ALL"

def multiselect(*args, default=None, **kwargs):
    return default

def do_nothing(*args, **kwargs):
    pass


def add_debug(st):
    st.session_state = {}
    st.progress = Progress
    st.set_page_config = set_page_config
    st.cache_data = cache_data
    st.columns = columns
    st.empty = empty
    st.sidebar = nullcontext()
    st.selectbox = selectbox
    st.multiselect = multiselect

    st.markdown = do_nothing
    st.warning = do_nothing

def debug_elements(streamlit_elements):
    streamlit_elements.elements = empty