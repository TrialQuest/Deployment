import logging
import json

def extract_json(text):
    start = text.find("{")
    if start == -1:
        return None

    stack = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            stack += 1
        elif text[i] == "}":
            stack -= 1

        if stack == 0:
            return text[start:i+1]

    return None

def json_parsing(text):
    try:
        return json.loads(text)
    except Exception as e:
        logging.error(f"JSON parsing failed: {e}")

        extracted=extract_json(text)
        if extracted:
            try:
                return json.loads(extracted)
            except Exception as e:
                logging.error(f"JSON extraction failed: {e}")
    return None

def valid_input(user_input):
    if not user_input:
        return False, "User input is empty"
    
    cleaned=user_input.strip()

    if not cleaned:
        return False, "User input is empty"
    
    if len(cleaned)>200:
        return False, "User input is too long"
    
    return True, cleaned

