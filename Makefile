run_app:
	streamlit run streamlit_app.py

run_api:
	uvicorn src.api.fast:app --reload
