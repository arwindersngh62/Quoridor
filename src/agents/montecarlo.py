import random
import domain.actions as actions


def simulate_games(state, agent_number, num_sims=10000):
    agent_wins = 0
    for i in range(num_sims):
        print(i)
        current_state = state.copy()
        while not current_state.is_terminal():
            print(current_state)
            app_actions = current_state.get_applicable_actions(
                actions.DEFAULT_QUORIDOR_ACTION_LIBRARY
            )
            action_index = random.randint(0, len(app_actions) - 1)
            action = app_actions[action_index]
            current_state = current_state.result(action)
        winner = current_state.get_winner()
        if winner == agent_number:
            agent_wins += 1
    return agent_wins / num_sims
