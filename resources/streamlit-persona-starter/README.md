# Streamlit Persona App

## Setup

    pip install -r requirements.txt

## Running the apps

All commands use --server.address localhost so the app only runs localy and dosent expose to the network:

    streamlit run app_personas.py --server.address localhost

## Files
- app_personas.py - persona-swapping version with dynamic persona selection
- personas/ - YAML persona files loaded at startup

## Build order
1. Try app_personas.py - add persona selection with YAML-driven personas

## The chat pattern

Every interaction re-runs your script top to bottom. Use st.session_state to persist data between reruns.

The basic chat pattern has 3 blocks - initialize state, display history, handle input. Look at app_echo.py to see it in its simplest form.

## Troubleshooting

- "No module named streamlit" - run pip install streamlit
- "No module named ollama" - run pip install ollama
- Connection error - make sure Ollama is running (ollama serve)
- Port already in use - use streamlit run app.py --server.port 8502
- Model not found - pull the model first with ollama pull llama3.2
