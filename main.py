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
                margin:0;
                padding:0;
            }

            body{
                font-family:Arial,sans-serif;
                background:linear-gradient(
                    135deg,
                    #0f172a,
                    #111827,
                    #020617
                );
                color:white;
                height:100vh;
                overflow:hidden;
            }

            .container{
                display:flex;
                height:100vh;
            }

            .left{
                flex:2;
                padding:30px;
                background:rgba(255,255,255,0.03);
                backdrop-filter:blur(10px);
            }

            .right{
                flex:1;
                padding:20px;
                overflow-y:auto;

                background:rgba(255,255,255,0.05);

                border-left:1px solid rgba(255,255,255,0.1);

                backdrop-filter:blur(10px);
            }

            h2{
                margin-bottom:20px;
                color:#60a5fa;
                font-size:28px;
            }

            .input-row{
                display:flex;
                gap:10px;
                margin-bottom:20px;
            }

            input{
                flex:1;
                padding:14px;

                background:#1e293b;
                color:white;

                border:1px solid #334155;
                border-radius:10px;

                font-size:16px;
                outline:none;

                transition:0.3s;
            }

            input:focus{
                border-color:#3b82f6;
                box-shadow:0 0 10px rgba(59,130,246,.4);
            }

            button{
                padding:14px 22px;

                border:none;
                border-radius:10px;

                background:#2563eb;
                color:white;

                font-weight:bold;

                cursor:pointer;

                transition:0.3s;
            }

            button:hover{
                background:#1d4ed8;
                transform:translateY(-2px);
            }

            #output{
                margin-top:10px;

                min-height:250px;

                padding:20px;

                background:rgba(255,255,255,0.05);

                border:1px solid rgba(255,255,255,0.08);

                border-radius:12px;

                white-space:pre-wrap;
                line-height:1.7;

                color:#e2e8f0;

                backdrop-filter:blur(10px);
            }

            #history{
                margin-top:10px;
            }

            .history-item{
                background:rgba(255,255,255,0.05);

                border:1px solid rgba(255,255,255,0.08);

                border-radius:12px;

                padding:15px;
                margin-bottom:15px;

                transition:0.3s;
            }

            .history-item:hover{
                transform:translateY(-2px);

                border-color:#3b82f6;

                background:rgba(59,130,246,0.08);
            }

            .question{
                font-weight:bold;
                color:#60a5fa;
                margin-bottom:8px;
            }

            .answer{
                color:#cbd5e1;
                line-height:1.5;
            }

            ::-webkit-scrollbar{
                width:8px;
            }

            ::-webkit-scrollbar-track{
                background:#111827;
            }

            ::-webkit-scrollbar-thumb{
                background:#334155;
                border-radius:10px;
            }

            ::-webkit-scrollbar-thumb:hover{
                background:#475569;
            }

            @media(max-width:900px){

                .container{
                    flex-direction:column;
                }

                .right{
                    height:40vh;
                    border-left:none;
                    border-top:1px solid rgba(255,255,255,0.1);
                }

                .input-row{
                    flex-direction:column;
                }

                button{
                    width:100%;
                }
            }

        </style>

    </head>

    <body>

        <div class="container">

            <div class="left">

                <h2>🤖 AI Agent</h2>

                <div class="input-row">

                    <input
                        id="q"
                        type="text"
                        placeholder="Ask something..."
                        onkeydown="if(event.key==='Enter') send()"
                    />

                    <button onclick="send()">
                        Ask
                    </button>

                </div>

                <div id="output">
                    Welcome. Ask me anything...
                </div>

            </div>

            <div class="right">

                <h2>📜 History</h2>

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
                    'Thinking...';

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