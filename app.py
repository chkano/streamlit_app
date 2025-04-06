import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
# import io
from dotenv import load_dotenv
# import textwrap
from IPython.display import Markdown

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(page_title="Chat with your CSV", layout="wide")
st.title("Chat with your CSV data")

# Initialize session state variables
if "df" not in st.session_state:
    st.session_state.df = None
if "data_dict_df" not in st.session_state:
    st.session_state.data_dict_df = None
if "question" not in st.session_state:
    st.session_state.question = ""
if "response" not in st.session_state:
    st.session_state.response = None
if "answer" not in st.session_state:
    st.session_state.answer = None
if "explanation" not in st.session_state:
    st.session_state.explanation = None
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = """
You are a helpful Python code generator.
Your goal is to write Python code snippets based on the user's question
and the provided DataFrame information.

Here's the context:

**User Question:**
{question}

**DataFrame Name:**
{df_name}

**DataFrame Details:**
{data_dict_text}

**Sample Data (Top 2 Rows):**
{example_record}

**Instructions:**

1. Write Python code that addresses the user's question by querying or manipulating the DataFrame.
2. **Crucially, use the `exec()` function to execute the generated code.**
3. Do not import pandas
4. Change date column type to datetime if needed
5. **Store the result of the executed code in a variable named `ANSWER`.** This variable should hold the answer to the user's question (e.g., a filtered DataFrame, a calculated value, etc.).
6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`. Do not include code to load the DataFrame.
7. Keep the generated code concise and focused on answering the question.
8. If the question requires a specific output format (e.g., a list, a single value), ensure the `ANSWER` variable holds that format.
"""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Configure Gemini API
try:
    # Try to get the API key from secrets first (for deployed app)
    try:
        key = st.secrets['gemini_api_key']
    except:
        # Fallback to environment variable (for local development)
        key = os.getenv('GEMINI_API_KEY')
    
    if not key:
        st.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable or configure it in Streamlit secrets.")
    else:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")

# Function to generate data dictionary
def generate_data_dictionary(df):
    # Create a prompt to ask Gemini to generate a data dictionary
    sample_data = df.head(5).to_string()
    prompt = f"""
    Given the following DataFrame sample data, generate a data dictionary with columns:
    1. column_name - The name of each column
    2. data_type - The data type of the column
    3. description - A brief description of what the column represents
    
    Sample data:
    {sample_data}
    
    Return the result in a CSV format without headers, with each row following this pattern:
    column_name,data_type,description
    """
    
    try:
        response = model.generate_content(prompt)
        # Parse the response to create a data dictionary dataframe
        data_dict_lines = response.text.strip().split('\n')
        data_dict_data = []
        
        for line in data_dict_lines:
            if ',' in line:
                parts = line.split(',', 2)  # Split into 3 parts max
                if len(parts) == 3:
                    data_dict_data.append(parts)
        
        # Create DataFrame
        data_dict_df = pd.DataFrame(data_dict_data, columns=['column_name', 'data_type', 'description'])
        return data_dict_df
    except Exception as e:
        st.error(f"Error generating data dictionary: {e}")
        return None

# Function to run the query
def run_query(df, data_dict_df, question, custom_prompt=None):
    df_name = 'df'
    
    # Convert the dataframe to a string representation for the sample
    example_record = df.head(2).to_string()
    
    # Convert data dictionary to text format
    data_dict_text = '\n'.join('- '+ data_dict_df['column_name'] +': '+data_dict_df['data_type'] +'. ' + data_dict_df['description'])
    
    # Create the prompt for generating a query
    if custom_prompt:
        # Use the custom prompt template
        prompt = custom_prompt.format(
            question=question,
            df_name=df_name,
            data_dict_text=data_dict_text,
            example_record=example_record
        )
    else:
        # Use the default prompt template
        prompt = f"""
        You are a helpful Python code generator.
        Your goal is to write Python code snippets based on the user's question
        and the provided DataFrame information.

        Here's the context:

        **User Question:**
        {question}

        **DataFrame Name:**
        {df_name}

        **DataFrame Details:**
        {data_dict_text}

        **Sample Data (Top 2 Rows):**
        {example_record}

        **Instructions:**

        1. Write Python code that addresses the user's question by querying or manipulating the DataFrame.
        2. **Crucially, use the `exec()` function to execute the generated code.**
        3. Do not import pandas
        4. Change date column type to datetime if needed
        5. **Store the result of the executed code in a variable named `ANSWER`.** This variable should hold the answer to the user's question (e.g., a filtered DataFrame, a calculated value, etc.).
        6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`. Do not include code to load the DataFrame.
        7. Keep the generated code concise and focused on answering the question.
        8. If the question requires a specific output format (e.g., a list, a single value), ensure the `ANSWER` variable holds that format.
        """
    
    try:
        response = model.generate_content(prompt)
        query = response.text.replace("```python", "").replace("```", "")
        
        # Create a local namespace for exec
        local_vars = {'df': df, 'pd': pd}
        
        # Execute the query
        exec(query, globals(), local_vars)
        
        # Get the answer from the local namespace
        answer = local_vars.get('ANSWER', "No result found")
        
        # Generate explanation
        explain_prompt = f"""
        The user asked: {question},
        Here is the result: {answer}
        Answer the question and summarize the answer. Include any relevant insights.
        """
        
        explanation_response = model.generate_content(explain_prompt)
        
        return response.text, answer, explanation_response.text
    except Exception as e:
        return f"Error generating or executing query: {e}", None, None

# Function to display the chat message
def display_chat_message(is_user, message, data=None):
    if is_user:
        st.chat_message("user").write(message)
    else:
        with st.chat_message("assistant"):
            st.write(message)
            if data is not None:
                if isinstance(data, pd.DataFrame):
                    st.dataframe(data)
                else:
                    st.write(f"**Result:** {data}")

# Sidebar for file upload and data dictionary
with st.sidebar:
    st.header("Upload your data")
    
    # File uploader for CSV
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.success(f"Successfully loaded CSV with {df.shape[0]} rows and {df.shape[1]} columns")
            
            # Option to upload a data dictionary or generate one
            st.subheader("Data Dictionary")
            data_dict_option = st.radio(
                "Do you have a data dictionary?",
                ["No, generate one for me", "Yes, I'll upload one"]
            )
            
            if data_dict_option == "Yes, I'll upload one":
                data_dict_file = st.file_uploader("Upload your data dictionary CSV", type=["csv"])
                if data_dict_file is not None:
                    data_dict_df = pd.read_csv(data_dict_file)
                    st.session_state.data_dict_df = data_dict_df
                    st.success("Data dictionary loaded successfully")
            else:
                if st.button("Generate Data Dictionary"):
                    with st.spinner("Generating data dictionary..."):
                        data_dict_df = generate_data_dictionary(df)
                        if data_dict_df is not None:
                            st.session_state.data_dict_df = data_dict_df
                            st.success("Data dictionary generated successfully")
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    # Add option to customize prompt
    if st.session_state.df is not None:
        with st.expander("Customize Prompt Template"):
            st.info("You can customize the prompt template used to generate the query. Use placeholders: {question}, {df_name}, {data_dict_text}, {example_record}")
            custom_prompt = st.text_area("Prompt Template", value=st.session_state.custom_prompt, height=400)
            if st.button("Save Prompt Template"):
                st.session_state.custom_prompt = custom_prompt
                st.success("Prompt template saved!")

# Main content area
if st.session_state.df is not None:
    # Show dataframe preview in a collapsible section
    with st.expander("Data Preview", expanded=False):
        st.dataframe(st.session_state.df.head())
    
    # Show data dictionary if available
    if st.session_state.data_dict_df is not None:
        with st.expander("View Data Dictionary", expanded=False):
            st.dataframe(st.session_state.data_dict_df)
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for chat in st.session_state.chat_history:
            display_chat_message(chat["is_user"], chat["message"], chat.get("data"))
    
    # Input for question
    if st.session_state.data_dict_df is not None:
        question = st.chat_input("Ask a question about your data")
        
        if question:
            # Add user message to chat history
            st.session_state.chat_history.append({"is_user": True, "message": question})
            
            # Display the user message
            with chat_container:
                display_chat_message(True, question)
            
            with st.spinner("Processing your question..."):
                response, answer, explanation = run_query(
                    st.session_state.df, 
                    st.session_state.data_dict_df, 
                    question,
                    st.session_state.custom_prompt
                )
                
                # Add assistant message to chat history
                st.session_state.chat_history.append({
                    "is_user": False, 
                    "message": explanation, 
                    "data": answer
                })
                
                # Display the assistant message
                with chat_container:
                    display_chat_message(False, explanation, answer)
                
                # Show generated code in an expander
                with st.expander("View Generated Code", expanded=False):
                    st.code(response, language="python")
    else:
        st.info("Please generate or upload a data dictionary first")
else:
    st.info("Please upload a CSV file to get started")

# Add a button to clear chat history
if st.session_state.chat_history:
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.experimental_rerun()