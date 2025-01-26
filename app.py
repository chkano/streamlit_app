import streamlit as st
import random
import pandas as pd

st.set_page_config(layout="wide")
st.title('Test Streamlit')

# st.write('Hello World')

# if st.button("Generate Random number"):
#     random_number = random.randint(1, 100)
#     st.write(f"Random number : {random_number}")

# col1_1, col1_2 = st.columns(2)
# with col1_1:
#     st.header("AAAAAA")

# with col1_2:
#     st.header("BBBBBB")

# col2_1, col2_2 = st.columns([4, 1], border = True)
# col2_1.header("CCCCCCC")
# col2_2.header("DDDDDD")

# with st.container():
#     st.write("MMMM")

# container = st.container(border = True)
# container.write("NNNN")


# col1, col2 = st.columns([0.3, 0.7], border = True)
# with col1.container():
#     st.write("Container 1 @ Column1")

# cc2 = col2.container(height= 150)
# cc2.write("Container2 @ Column2")


# con1 = st.container()
# for col in con1.columns([1,2,3,4], border = True):
#     col.write("Hello World")

# con2 = st.container(height=100)
# cc2_1, cc2_2, cc2_3 = con2.columns(3)
# cc2_1.write("Column 5 @ container 2")
# cc2_2.write("Column 6 @ container 2")
# cc2_3.write("Column 7 @ container 2")


# st.sidebar.title("Filter")
# st.sidebar.header("Option")
# st.sidebar.selectbox("Please select one", ("Op1", "Opt2", "Opt3"))
# st.sidebar.radio("Please select one", ["cho1","cho2","cho3"])

# df = pd.DataFrame({"first_col":[1,2,3,4], "second_col":[10,20,30,40]})
# st.write("1+1=",2)
# st.write(df)

# st.divider()

# st.header("One")
# st.header("two", )
# st.divider()
# st.subheader("Three", divider = True)

# username_input = st.text_input("username", value="??")
# password_input = st.text_input("password", type = "password", placeholder = "pls give password")
# st.write(username_input, password_input)

text = st.text_area("Text Analyze")
st.write(f"")