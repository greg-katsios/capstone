# Streamlit Chat App - Demo Code

Chat interface for the Streamlit Fundamentals sesion (Module 5). Uses Ollama so everything runs localy, no API keys needed.

Make sure Ollama is running before you start. You can check by going to http://localhost:11434 in your browser.

## Setup

    pip install -r requirements.txt

## Running the apps

All commands use --server.address localhost so the app only runs localy and dosent expose to the network.

Start with the echo version to test that streamlit works:

    streamlit run app_echo.py --server.address localhost

Then try the real LLM version:

    streamlit run app.py --server.address localhost

If you want to try streaming (strech goal):

    streamlit run app_streaming.py --server.address localhost

## Files

- app_echo.py - echo bot, no LLM needed, good for testing the UI
- app.py - full chat app connected to Ollama
- app_streaming.py - streaming version where responses show up token by token

## Build order

1. Start with app_echo.py - understand the chat patern (session state, display loop, input handler)
2. Move to app.py - add the real LLM call with a spinner
3. Try app_streaming.py - swap the spinner for token by token streaming

## The chat pattern

Every interaction re-runs your script top to bottom. Use st.session_state to persist data between reruns.

The basic chat pattern has 3 blocks - initialize state, display history, handle input. Look at app_echo.py to see it in its simplest form.

## Troubleshooting

- "No module named streamlit" - run pip install streamlit
- "No module named ollama" - run pip install ollama
- Connection error - make sure Ollama is running (ollama serve)
- Port already in use - use streamlit run app.py --server.port 8502
- Model not found - pull the model first with ollama pull llama3.2
