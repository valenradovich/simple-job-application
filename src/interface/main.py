from src.ml_logic.data import data_workflow
from src.ml_logic.model import load_model, run_model
from src.ml_logic.vector_db import load_vector_store, save_vector_store

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from src.params import VECTOR_DB_PATH

def talk_to_link(llm, prompt, file_path=None, vectorstore=None):
    try:
        if vectorstore is None:
            vector_store = FAISS.load_local(file_path, OpenAIEmbeddings())
            chain = run_model(llm, vector_store)
            result = chain({"question": prompt}, return_only_outputs=True)
        else:
            chain = run_model(llm, vectorstore)
            result = chain({"question": prompt}, return_only_outputs=True)

        return result # this function should return the result or this code should be in the streamlit app
    except Exception as e:
        print("❌ Could not run model. Please check your data and try again.")
        print(e)

def prepare_data(list_urls, openai_api_key):
    try:
        ### file_path = "src/ml_logic/vector_store"

        # loading and splitting urls
        docs = data_workflow(list_urls)

        # loading and saving vector store
        vectorstore_openai = load_vector_store(docs, openai_api_key)
        ### save_vector_store(vectorstore_openai, file_path) # saving locally, not the best but it enough for this demo
        print("✅ Data prepared successfully.")

        return vectorstore_openai
    except Exception as e:
        print("❌ Could not prepare data. Please check your url and try again.")
        print(e)

        return False

def main(urls_list, prompt):
    result = talk_to_link(llm=llm, prompt=prompt, file_path=VECTOR_DB_PATH)
    pass

if __name__ == "__main__":
    llm = load_model()
