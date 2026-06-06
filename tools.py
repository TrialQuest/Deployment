import logging

def get_table(number):
    number = int(number)
    logging.info(f"Executing get_table with value:{number}")
    return {
        "number": number,
        "table": [number * i for i in range(1, 11)]
    }

def get_remember(qoute):
    logging.info(f"Executing get_remember with value:{qoute}")
    return ({"qoute":"The magic you are looking for is in the work you are avoiding"})

tools={
    "get_table":get_table,
    "get_remember":get_remember
}