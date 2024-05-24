import networkx as nx
cutDict = {"v": [(1, 0), (0, 1)], "h": [(0, 1), (1, 0)]}

def pos_add(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] + y[0], x[1] + y[1]


def pos_sub(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] - y[0], x[1] - y[1]

class QuoridorState:

    def __init__(
        self,
        agent_positions: list[tuple[tuple[int, int], str]],
        wall_positions: list[tuple[tuple[int, int], str]],
        agent_to_move: str,
        walls_left: tuple[int, int],
        nxgraph: nx.Graph,
        parent = None,
    ):
        self.agent_positions = agent_positions
        self.wall_positions = wall_positions
        self.agent_to_move = agent_to_move
        self.walls_left = walls_left
        self.graph = nxgraph
        self.parent = parent
        self.path_cost = 0 if parent is None else parent.path_cost + 1

    def free_at(self, position):
        for pos2, char in self.agent_positions:
            if pos2 == position:
                return False
        return True
    
    def not_blocked_by_wall(self, position, dir):
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

    def wall_at(self, position):
        for pos, _ in self.wall_positions:
            if pos == position:
                return True
        return False
    
    def wall_and_orientation_at(self, position, orientation):
        for pos, ori in self.wall_positions:
            if pos == position and ori == orientation:
                return True
        return False
    
    def findVertice(self, position):
        return [x for x,y in self.graph.nodes(data=True) if y['pos'] == position][0]

    def wall_blocks(self, position, orientation):
        cutVertices = [[self.findVertice(position), self.findVertice(pos_add(position, cutDict[orientation][0]))], [self.findVertice(pos_add(position, (1,1))), self.findVertice(pos_add(position, cutDict[orientation][1]))]]
        for vpair in cutVertices:
            self.graph.remove_edge(vpair[0], vpair[1])
        p1_node = self.findVertice(self.agent_positions[0][0])
        p2_node = self.findVertice(self.agent_positions[1][0])
        p1_goal = self.findVertice((-1, -1))
        p2_goal = self.findVertice((-2, -2))
        if not nx.has_path(self.graph, p1_node, p1_goal):
            for vpair in cutVertices:
                self.graph.add_edge(vpair[0], vpair[1])
            return True
        if not nx.has_path(self.graph, p2_node, p2_goal):
            for vpair in cutVertices:
                self.graph.add_edge(vpair[0], vpair[1])
            return True
        return False
    
    def __repr__(self) -> str:
        board = []
        board.append(f"{self.agent_to_move}|({self.walls_left})")
        flatline = ["-" for i in range(19)]
        flatline = "".join(flatline)
        board.append(flatline)
        # Add the grid and the players to the list of strings
        for y in range(9):
            line = []
            for x in range(9):
                line.append("|")
                for position, agent in self.agent_positions:
                    if (x, y) == position:
                        line.append(agent)
                    else:
                        line.append(" ")
            line.append("|")
            board.append("".join(line))
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
        # print the board
        for l in board:
            string = "".join(l)
            print(string)
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