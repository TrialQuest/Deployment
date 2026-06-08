from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from agent import agent
from utils import valid_input
import logging

app = FastAPI()

class Query(BaseModel):
    question: str


@app.post("/ask")
def ask(query: Query):
    logging.info(f"Received question: {query.question}")

    valid, result = valid_input(query.question)

    if not valid:
        logging.warning(f"Invalid input: {result}")
        return {"error": result}

    try:
        response = agent(result)

        logging.info(f"Response generated: {response}")

        return {
            "question": result,
            "answer": response
        }

    except Exception:
        logging.exception("Error in /ask")
        return {"error": "Something went wrong"}


@app.get("/", response_class=HTMLResponse)
def ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Agent</title>
        ...
    </head>
    <body>
        ...
    </body>
    </html>
    """