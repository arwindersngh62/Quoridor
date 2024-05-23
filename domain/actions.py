
import domain.state as q_state

def pos_add(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] + y[0], x[1] + y[1]


def pos_sub(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] - y[0], x[1] - y[1]

direction_deltas = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1),
}

class MoveAction:

    def __init__(self, agent_direction):
        self.agent_delta = direction_deltas.get(agent_direction)
        self.name = "Move(%s)" % agent_direction

    def calculate_positions(self, current_agent_position: tuple[int, int]) -> tuple[int, int]:
        return pos_add(current_agent_position, self.agent_delta)

    def is_applicable(self, agent_index: int,  state: q_state.QuoridorState) -> bool:
        current_agent_position, _ = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)
        if new_agent_position[0] < 0 or new_agent_position[0] > 8 or new_agent_position[1] < 0 or new_agent_position[1] > 8:
            return False
        if not state.not_blocked_by_wall(current_agent_position, self.name[-2].lower()):
            return False
        return state.free_at(new_agent_position)

    def result(self, agent_index: int, state: q_state.QuoridorState):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)
        state.agent_positions[agent_index] = (new_agent_position, agent_char)

    def __repr__(self):
        return self.name
    
class JumpStraightAction:

    def __init__(self, agent_direction):
        self.agent_delta_midway = direction_deltas.get(agent_direction)
        self.agent_delta = pos_add(direction_deltas.get(agent_direction), direction_deltas.get(agent_direction))
        self.name = "JumpStraight(%s)" % agent_direction

    def calculate_positions(self, current_agent_position: tuple[int, int]) -> tuple[int, int]:
        return pos_add(current_agent_position, self.agent_delta_midway), pos_add(current_agent_position, self.agent_delta)

    def is_applicable(self, agent_index: int,  state: q_state.QuoridorState) -> bool:
        current_agent_position, _ = state.agent_positions[agent_index]
        midway_agent_position, new_agent_position = self.calculate_positions(current_agent_position)
        if new_agent_position[0] < 0 or new_agent_position[0] > 8 or new_agent_position[1] < 0 or new_agent_position[1] > 8:
            return False
        if not midway_agent_position == state.agent_positions[int(not bool(agent_index))][0]:
            return False
        if not state.not_blocked_by_wall(current_agent_position, self.name[-2].lower()):
            return False
        if not state.not_blocked_by_wall(midway_agent_position, self.name[-2].lower()):
            return False
        return True

    def result(self, agent_index: int, state: q_state.QuoridorState):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)[1]
        state.agent_positions[agent_index] = (new_agent_position, agent_char)

    def __repr__(self):
        return self.name
    
class JumpSideAction:

    def __init__(self, agent_direction1, agent_direction2):
        self.agent_delta_midway = direction_deltas.get(agent_direction1)
        self.agent_delta = pos_add(direction_deltas.get(agent_direction1), direction_deltas.get(agent_direction2))
        self.name = "JumpSide(%s, %s)" % (agent_direction1, agent_direction2)

    def calculate_positions(self, current_agent_position: tuple[int, int]) -> tuple[int, int]:
        return pos_add(current_agent_position, self.agent_delta_midway), pos_add(current_agent_position, self.agent_delta)

    def is_applicable(self, agent_index: int,  state: q_state.QuoridorState) -> bool:
        current_agent_position, _ = state.agent_positions[agent_index]
        midway_agent_position, new_agent_position = self.calculate_positions(current_agent_position)
        if new_agent_position[0] < 0 or new_agent_position[0] > 8 or new_agent_position[1] < 0 or new_agent_position[1] > 8:
            return False
        if not midway_agent_position == state.agent_positions[int(not bool(agent_index))][0]:
            return False
        if not state.not_blocked_by_wall(current_agent_position, self.name[-5].lower()):
            return False
        if state.not_blocked_by_wall(midway_agent_position, self.name[-5].lower()):
            return False
        if not state.not_blocked_by_wall(midway_agent_position, self.name[-2].lower()):
            return False
        return True

    def result(self, agent_index: int, state: q_state.QuoridorState):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)[1]
        state.agent_positions[agent_index] = (new_agent_position, agent_char)

    def __repr__(self):
        return self.name
    
# An action library for the multi agent pathfinding
DEFAULT_QUORIDOR_ACTION_LIBRARY = [
    MoveAction("N"),
    MoveAction("S"),
    MoveAction("E"),
    MoveAction("W"),
    JumpStraightAction("N"),
    JumpStraightAction("S"),
    JumpStraightAction("E"),
    JumpStraightAction("W"),
    JumpSideAction("N", "E"),
    JumpSideAction("N", "W"),
    JumpSideAction("S", "E"),
    JumpSideAction("S", "W"),
    JumpSideAction("E", "N"),
    JumpSideAction("E", "S"),
    JumpSideAction("W", "N"),
    JumpSideAction("W", "S"),
]