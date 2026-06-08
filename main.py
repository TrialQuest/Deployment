from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from agent import agent
from utils import valid_input
import logging

app = FastAPI(
    title="AI Agent"
)

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

    except Exception as e:
        logging.exception("Error in /ask")
        return {"error": str(e)}


@app.get("/", response_class=HTMLResponse)
def ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Agent</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
            }

            h2 {
                text-align: center;
            }

            input {
                width: 70%;
                padding: 10px;
            }

            button {
                padding: 10px 15px;
                cursor: pointer;
            }

            #output {
                margin-top: 20px;
                white-space: pre-wrap;
                word-wrap: break-word;
                overflow-x: auto;
                border: 1px solid #ccc;
                padding: 10px;
                min-height: 50px;
                background: #f9f9f9;
            }
        </style>
    </head>

    <body>
        <h2>AI Agent</h2>

        <input
            id="q"
            type="text"
            placeholder="Ask something..."
            onkeydown="if(event.key==='Enter') send()"
        />

        <button onclick="send()">Ask</button>

        <div id="output"></div>

        <script>
            async function send() {

                const q = document.getElementById("q").value.trim();

                if (!q) {
                    document.getElementById("output").innerText =
                        "Please enter a question.";
                    return;
                }

                document.getElementById("output").innerText =
                    "Loading...";

                try {

                    const res = await fetch("/ask", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            question: q
                        })
                    });

                    const data = await res.json();

                    document.getElementById("output").innerText =
                        data.answer || data.error || "No response";

                } catch (e) {

                    document.getElementById("output").innerText =
                        "Request failed: " + e.message;

                }
            }
        </script>

    </body>
    </html>
    """