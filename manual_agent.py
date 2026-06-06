from agent import agent
from utils import valid_input

while True:
    user_input = input("Ask: ")

    valid, result = valid_input(user_input)

    if not valid:
        print(result)
        continue

    print(agent(result))