from domain import *

agent = None

def get_action_from_string(string):
    action = None
    if len(string) == 2:
        if string[0].lower() == "m":
            if string[1].lower() in ['n', 's', 'e', 'w']:
                action = MoveAction(string[1].upper())
        elif string[0].lower() == "j":
            if string[1].lower() in ['n', 's', 'e', 'w']:
                action = JumpStraightAction(string[1].upper())
    elif len(string) == 3 and string[0].lower() == "j":
        temp_action = JumpSideAction(string[1].upper(), string[2].upper())
        if temp_action in DEFAULT_QUORIDOR_ACTION_LIBRARY:
            action = temp_action
    elif len(string) == 4 and string[0].lower() == "w":
        if string[1] in [str(i) for i in range(9)] and string[2] in [str(i) for i in range(9)] and string[3].lower() in ["v", "h"]:
            action = WallAction((int(string[1]), int(string[2])), string[3])
    return action

current_state = initial_state

while True:
    print(current_state)
    if current_state.is_terminal():
        winner = current_state.get_winner()
        print("Player %i has won the game!" % winner)
        break
    #print(current_state.get_applicable_actions(DEFAULT_QUORIDOR_ACTION_LIBRARY))
    input_string = input("What is your move?\n")
    action = get_action_from_string(input_string)
    if action == None:
        print("Not legal input")
        continue
    if action not in current_state.get_applicable_actions(DEFAULT_QUORIDOR_ACTION_LIBRARY):
        #print(action)
        print("Not legal action")
        continue
    current_state = current_state.result(action)
    print(current_state)
    if current_state.is_terminal():
        winner = current_state.get_winner()
        print("Player %i has won the game!" % winner)
        break
    agent_action = agent.get_action(current_state)
    current_state = current_state.result(agent_action)