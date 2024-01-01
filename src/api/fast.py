from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.interface.main import prepare_data, talk_to_link
from src.ml_logic.model import load_model

app = FastAPI()

llm = load_model()
print(type(llm))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/data")
async def data(list_urls: list):
    prepare_data(list_urls)
    return {"message": "Data processed successfully"}

@app.get("/chat")
async def chat(prompt: str):
    result = talk_to_link(llm=llm, prompt=prompt)
    return result

@app.get("/")
async def root():
    return {"message": "Talk to link"}


# uvicorn src.api.fast:app --reload
