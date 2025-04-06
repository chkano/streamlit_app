# Chat with Your CSV App

A Streamlit application that allows you to upload CSV data and ask questions about it in natural language, powered by Gemini AI.

## Features

- Upload any CSV file
- Automatically generate a data dictionary or upload your own
- Ask questions about your data in natural language using a chat-style interface
- Customize the prompt template used to generate queries
- View code used to answer questions
- Chat history with user queries on the right and AI responses on the left

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your API key:
   - Create a `.env` file in the root directory
   - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`

## Running the App

Run the Streamlit app with:
```
streamlit run app.py
```

## How to Use

1. Upload a CSV file using the uploader in the sidebar
2. Either generate a data dictionary automatically or upload your own
3. Type your questions in the chat input at the bottom
4. (Optional) Customize the prompt template in the sidebar to improve query results
5. View the chat conversation with your questions (right) and AI answers (left)
6. Expand "View Generated Code" to see the Python code used to generate answers

## Example Questions

- "How many rows are in the dataset?"
- "What is the average value of [column]?"
- "Show me the top 5 rows sorted by [column]"
- "What is the correlation between [column1] and [column2]?"
- "Group the data by [column] and show the count"

## Requirements

- Python 3.7+
- Streamlit
- Pandas
- Google Generative AI (Gemini)
- Python-dotenv
- IPython