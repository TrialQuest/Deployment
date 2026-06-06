from config import client
from utils import json_parsing
import json
import logging
from tools import tools
from db import save_chat

msgs=[
    {
        "role":"system",
        "content":f"""
        You are mathematics helping Agent,
             
        available tools:
        1.get_table(number)
        2.get_remember(quote)

        -------------------------
        DECISION RULES
        -------------------------
        1. If the user asks for real-time, external, or specific data → use a tool.
        2. If the answer can be given from general knowledge → DO NOT use any tool.
        3. Never guess tool inputs. Extract them clearly from the user query.
 
        -------------------------
        TOOL CALL FORMAT
        -------------------------
        4. When calling a tool, respond with ONLY valid JSON:
        {{"action": "tool_name", "input": "value"}}

        5. Do NOT include any text, explanation, or formatting outside JSON.
        6. Always use lowercase tool names and clean input values.

        -------------------------
        AFTER TOOL RESPONSE
        -------------------------
        7. After receiving a tool result:
        - DO NOT call any tool again
        - DO NOT output JSON
        - Use the tool result to generate a clear, natural language answer

        -------------------------
        ERROR HANDLING
        -------------------------
        8. If required input is missing:
        - Ask the user for clarification
        - DO NOT call a tool

        9. If tool result is unclear or empty:
        - Respond gracefully and explain the issue

        -------------------------
        GENERAL BEHAVIOR
        -------------------------
        10. Keep answers concise and relevant
        11. Maintain context across conversation
        12. Do not repeat tool calls unnecessarily
     
        Tool usage rules:

        - get_table(number):
        Use ONLY for tables

        - get_remember(quote):
        Use ONLY for quotes

        If query is about any other then tools:
        → answer normally (do NOT use any tool)
        """
    }
]

def agent(user_input):
    logging.info(f"User Input:{user_input}")
    msgs.append({"role":"user","content":user_input})

    if len(msgs)>9:
        msgs[:]=[msgs[0]]+msgs[-8:]

    try:
        resp=client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=msgs
        )

        respout=resp.choices[0].message.content
        logging.info(f"Response Output: {respout}")

        data=json_parsing(respout)

        if not data:
            msgs.append({"role":"assistant","content":respout})
            save_chat(user_input, respout)

            return respout
        
        if data and "action" in data:
            tool_name = data["action"]
            tool_value = data["input"]

        if tool_name not in tools:
                return "Invalid tool"
        
        msgs.append({"role": "assistant", "content": respout})

        tool_result = tools[tool_name](tool_value)

        msgs.append({
            "role": "user",
            "content": (
                f"Tool result:\n"
                f"{json.dumps(tool_result)}\n\n"
                f"Use this result to answer the original question."
            )
        })

        final = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=msgs
        )

        finalout = final.choices[0].message.content

        if not finalout or finalout.strip() == "":
            logging.error("Empty final output")
            return "LLM failed to generate response"
            
        logging.info(f"Final Output:{finalout}")

        msgs.append({"role": "assistant", "content": finalout})
        save_chat(user_input, finalout)

        return finalout        

    except Exception as e:
        logging.error(f"Agent error: {e}")
        return f"Something went wrong {str(e)}"