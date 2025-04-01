import streamlit as st

st.set_page_config(page_title="Streamlit App", page_icon=":shark:")

st.title("This is a title")
st.write("Hello World!")

st.markdown("""## This is a markdown

### Streamlit is awesome!
マークダウンでかけて便利！
- リスト
> 引用

```python
import streamlit as st
st.title("This is a title")
st.write("Hello World!")
``` 
""")