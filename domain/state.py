from __future__ import annotations
import networkx as nx
import copy
import domain.actions as actions

def findVertice(graph, position: tuple[int, int]):
        return [x for x,y in graph.nodes(data=True) if y['pos'] == position][0]

class QuoridorState:

    def __init__(
        self,
        agent_positions: list[tuple[tuple[int, int], str]],
        wall_positions: list[tuple[tuple[int, int], str]],
        agent_to_move: int,
        walls_left: tuple[int, int],
        nxgraph: nx.Graph,
        action: actions.AnyAction = None,
        parent = None,
    ):
        self.agent_positions = agent_positions
        self.wall_positions = wall_positions
        self.agent_to_move = agent_to_move
        self.walls_left = walls_left
        self.graph = nxgraph
        self.parent = parent
        self.action_taken_to_state = action
        self.path_cost = 0 if parent is None else parent.path_cost + 1

    def free_at(self, position: tuple[int, int]) -> bool:
        for pos2, char in self.agent_positions:
            if pos2 == position:
                return False
        return True
    
    def not_blocked_by_wall(self, position: tuple[int, int], dir: str) -> bool:
        x, y = position
        for wall_pos, orientation in self.wall_positions:
            if orientation == "v":
                if dir == "e" and wall_pos[0] == x and (wall_pos[1] == y or wall_pos[1] == y - 1):
                    return False
                if dir == "w" and wall_pos[0] == x - 1 and (wall_pos[1] == y or wall_pos[1] == y - 1):
                    return False
            if dir == "n" and wall_pos[1] == y - 1 and (wall_pos[0] == x or wall_pos[0] == x - 1):
                return False
            if dir == "s" and wall_pos[1] == y and (wall_pos[0] == x or wall_pos[0] == x - 1):
                return False
        return True

    def wall_at(self, position: tuple[int, int]) -> bool:
        for pos, _ in self.wall_positions:
            if pos == position:
                return True
        return False
    
    def wall_and_orientation_at(self, position: tuple[int, int], orientation: str) -> bool:
        for pos, ori in self.wall_positions:
            if pos == position and ori == orientation:
                return True
        return False
    
    def findVertice(self, position: tuple[int, int]):
        return findVertice(self.graph, position)

    def wall_blocks(self, position: tuple[int, int], orientation: str) -> bool:
        cutVertices = [[self.findVertice(position), self.findVertice(actions.pos_add(position, actions.cutDict[orientation][0]))], [self.findVertice(actions.pos_add(position, (1,1))), self.findVertice(actions.pos_add(position, actions.cutDict[orientation][1]))]]
        deleted_edges = False
        for vpair in cutVertices:
            if self.graph.has_edge(vpair[0], vpair[1]):
                deleted_edges = True
                self.graph.remove_edge(vpair[0], vpair[1])
        p1_node = self.findVertice(self.agent_positions[0][0])
        p2_node = self.findVertice(self.agent_positions[1][0])
        p1_goal = self.findVertice((-1, -1))
        p2_goal = self.findVertice((-2, -2))
        if not nx.has_path(self.graph, p1_node, p1_goal):
            if deleted_edges:
                for vpair in cutVertices:
                    self.graph.add_edge(vpair[0], vpair[1])
            return True
        if not nx.has_path(self.graph, p2_node, p2_goal):
            if deleted_edges:
                for vpair in cutVertices:
                    self.graph.add_edge(vpair[0], vpair[1])
            return True
        if deleted_edges:
            for vpair in cutVertices:
                self.graph.add_edge(vpair[0], vpair[1])
        return False
    
    def result(self, action: actions.AnyAction):
        """Computes the state resulting from applying a joint action to this state"""
        new_state = QuoridorState(copy.copy(self.agent_positions), copy.copy(self.wall_positions),
                                  copy.copy(self.agent_to_move), copy.copy(self.walls_left),
                                  copy.copy(self.graph), action, self)

        action.result(self.agent_to_move, new_state)
        return new_state

    def is_applicable(self, action: actions.AnyAction) -> bool:
        """Returns whether all individual actions in the joint_action is applicable in this state"""
        if not action.is_applicable(self.agent_to_move, self):
            return False
        return True

    def get_applicable_actions(self, action_set: list[actions.AnyAction]) -> list[actions.AnyAction]:
        """Returns a list of all applicable joint_action in this state"""
        # Determine all applicable actions for each individual agent, i.e. without consideration of conflicts.
        applicable_actions = []
        for action in action_set:
            if action.is_applicable(self.agent_to_move, self):
                applicable_actions.append(action)
        return applicable_actions
    
    def __repr__(self) -> str:
        board = []
        board.append(f"{self.agent_to_move}|({self.walls_left})")
        flatline = ["-" for i in range(19)]
        board.append(flatline)
        # Add the grid and the players to the list of strings
        for y in range(9):
            line = []
            for x in range(9):
                line.append("|")
                if (x, y) == self.agent_positions[0][0]:
                    line.append(self.agent_positions[0][1])
                elif (x, y) == self.agent_positions[1][0]:
                    line.append(self.agent_positions[1][1])
                else:
                    line.append(" ")
            line.append("|")
            board.append(line)
            board.append(flatline.copy())
        # Add the walls
        for wall in self.wall_positions:
            x, y = wall[0]
            board[(y+1)*2][(x+1)*2] = '#'
            if wall[1] == "v":
                board[(y+1)*2-1][(x+1)*2] = '#'
                board[(y+2)*2-1][(x+1)*2] = '#'
            else:
                board[(y+1)*2][(x+1)*2-1] = '#'
                board[(y+1)*2][(x+2)*2-1] = '#'
        board = [''.join(linei) for linei in board]
        return '\n'.join(board)

    def __eq__(self, other) -> bool:
        """
        Notice that we here only compare the agent positions and box positions, but ignore all other fields.
        That means that two states with identical positions but e.g. different parent will be seen as equal.
        """
        if isinstance(other, self.__class__):
            return self.agent_positions == other.agent_positions and self.wall_positions == other.wall_positions and self.agent_to_move == other.agent_to_move and self.walls_left == other.walls_left
        else:
            return False
        
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self):
        """
        Allows the state to be stored in a hash table for efficient lookup.
        Notice that we here only hash the agent positions and box positions, but ignore all other fields.
        That means that two states with identical positions but e.g. different parent will map to the same hash value.
        """
        return hash((tuple(self.agent_positions), tuple(self.box_positions), self.agent_to_move, self.walls_left))
    
initial_graph = nx.Graph()
ids = 0
for x in range(9):
    for y in range(9):
        initial_graph.add_node(ids, pos=(x, y))
        ids += 1
for node1, data1 in initial_graph.nodes(data=True):
    for node2, data2 in initial_graph.nodes(data=True):
        if not initial_graph.has_edge(node1, node2) and abs(data1['pos'][0] - data2['pos'][0]) + abs(data1['pos'][1] - data2['pos'][1]) == 1:
            initial_graph.add_edge(node1, node2)
initial_graph.add_node(-1, pos=(-1, -1))
initial_graph.add_node(-2, pos=(-2, -2))
for i in range(9):
    initial_graph.add_edge(-1, findVertice(initial_graph, (i, 8)))
    initial_graph.add_edge(-2, findVertice(initial_graph, (i, 0)))

initial_state = QuoridorState([((4,0),"1"), ((4,8),"2")],
                              [],
                              0,
                              [10, 10],
                              initial_graph)