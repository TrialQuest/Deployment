from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from agent import agent
from utils import valid_input
from db import get_chat_history, create_table
import logging

app = FastAPI(title="AI Agent")

create_table()

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


@app.get("/history")
def history():
    return {
        "history": get_chat_history()
    }

@app.get("/db-test")
def db_test():
    try:
        rows = get_chat_history()
        return {
            "status": "success",
            "count": len(rows),
            "rows": rows
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/", response_class=HTMLResponse)
def ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Agent</title>

        <style>

            *{
                box-sizing:border-box;
            }

            body{
                margin:0;
                font-family:Arial,sans-serif;
                background:#f5f5f5;
            }

            .container{
                display:flex;
                height:100vh;
            }

            .left{
                flex:2;
                padding:30px;
                background:white;
            }

            .right{
                flex:1;
                border-left:1px solid #ddd;
                background:#fafafa;
                padding:20px;
                overflow-y:auto;
            }

            h2{
                margin-top:0;
            }

            input{
                width:75%;
                padding:12px;
                font-size:16px;
            }

            button{
                padding:12px 18px;
                cursor:pointer;
            }

            #output{
                margin-top:20px;
                padding:15px;
                border:1px solid #ccc;
                background:#f9f9f9;
                min-height:150px;
                white-space:pre-wrap;
            }

            .history-item{
                background:white;
                border:1px solid #ddd;
                border-radius:8px;
                padding:12px;
                margin-bottom:12px;
            }

            .question{
                font-weight:bold;
                margin-bottom:6px;
            }

            .answer{
                color:#333;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <div class="left">

                <h2>AI Agent</h2>

                <input
                    id="q"
                    type="text"
                    placeholder="Ask something..."
                    onkeydown="if(event.key==='Enter') send()"
                />

                <button onclick="send()">Ask</button>

                <div id="output">
                    Ask a question...
                </div>

            </div>

            <div class="right">

                <h2>History</h2>

                <div id="history">
                    Loading...
                </div>

            </div>

        </div>

        <script>

            async function loadHistory() {

                try {

                    const res = await fetch('/history');
                    const data = await res.json();

                    const historyDiv =
                        document.getElementById('history');

                    historyDiv.innerHTML = '';

                    if (!data.history || data.history.length === 0) {

                        historyDiv.innerHTML =
                            '<p>No history found</p>';

                        return;
                    }

                    data.history.forEach(item => {

                        const div =
                            document.createElement('div');

                        div.className = 'history-item';

                        div.innerHTML =
                            '<div class="question">Q: '
                            + item[0] +
                            '</div>' +
                            '<div class="answer">A: '
                            + item[1] +
                            '</div>';

                        historyDiv.appendChild(div);

                    });

                }
                catch (err) {

                    document.getElementById('history').innerHTML =
                        'Failed to load history';

                }
            }


            async function send() {

                const q =
                    document.getElementById('q').value.trim();

                if (!q) {
                    return;
                }

                document.getElementById('output').innerText =
                    'Loading...';

                try {

                    const res = await fetch('/ask', {

                        method: 'POST',

                        headers: {
                            'Content-Type': 'application/json'
                        },

                        body: JSON.stringify({
                            question: q
                        })

                    });

                    const data = await res.json();

                    document.getElementById('output').innerText =
                        data.answer ||
                        data.error ||
                        'No response';

                    document.getElementById('q').value = '';

                    loadHistory();

                }
                catch (err) {

                    document.getElementById('output').innerText =
                        'Request failed: ' + err.message;

                }
            }

            loadHistory();

        </script>

    </body>
    </html>
    """