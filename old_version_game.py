import networkx as nx
import matplotlib.pyplot as plt

moveDict = {"d": [0, 1], "u": [0, -1], "l": [-1, 0], "r": [1, 0]}


class Vertice:
    def __init__(self, position):
        self.position = position
        self.neighbors = []
        self.marked = False


class Edge:
    def __init__(self, v1, v2):
        self.vertices = [v1, v2]


class Grid:
    # Defines the grid, adds all nodes and edges between them to a graph representation.
    # Currently does double work by making a nx graph and homemade one.
    # nx graph can be cut out without changes to the code, if the homemade one is cut, code needs to be rewritten
    def __init__(self):
        self.G = nx.Graph()
        self.vertices = [Vertice([e1, e2]) for e1 in range(9) for e2 in range(9)]
        for v in self.vertices:
            self.G.add_node(v)
        self.wallPositions = []
        for v1 in self.vertices:
            for v2 in self.vertices:
                if (v1 != v2 and v1 not in v2.neighbors) and abs(
                    v1.position[0] - v2.position[0]
                ) + abs(v1.position[1] - v2.position[1]) == 1:
                    v1.neighbors.append(v2)
                    v2.neighbors.append(v1)
                    self.G.add_edge(v1, v2)
        self.p1Goal = Vertice([-1, -1])
        self.G.add_node(self.p1Goal)
        self.p2Goal = Vertice([-2, -2])
        self.G.add_node(self.p2Goal)
        self.vertices.append(self.p1Goal)
        self.vertices.append(self.p2Goal)
        for vertice in self.vertices:
            if vertice.position[1] == 0:
                vertice.neighbors.append(self.p1Goal)
                self.p1Goal.neighbors.append(vertice)
                self.G.add_edge(vertice, self.p1Goal)
            if vertice.position[1] == 8:
                vertice.neighbors.append(self.p2Goal)
                self.p2Goal.neighbors.append(vertice)
                self.G.add_edge(vertice, self.p2Goal)

    # Takes a position (list with 2 numbers corresponding to coordinates, eg: [2, 1]) and returns a vertice in the grid
    # with that position
    def findVertice(self, position):
        return self.findVerticeInList(position, self.vertices)

    # Does the same thing but generally
    def findVerticeInList(self, position, list1):
        for e in list1:
            if e.position == position:
                return e
        return None

    # Takes position and orientation eg: ([1, 2], "h") and places a wall with those specifications
    def placeWall(self, position, orientation):
        self.placeWallInList(position, orientation, self.vertices)

    # general version of earlier method
    def placeWallInList(self, position, orientation, grid):
        # Uses a dict to find indexes based on the orientation of the wall
        cutDict = {"v": [[1, 0], [0, 1]], "h": [[0, 1], [1, 0]]}
        # find the 2 pairs of nodes that each will be seperated by the wall
        cutVertices = [
            [
                self.findVerticeInList(position, grid),
                self.findVerticeInList(
                    [
                        position[0] + cutDict[orientation][0][0],
                        position[1] + cutDict[orientation][0][1],
                    ],
                    grid,
                ),
            ],
            [
                self.findVerticeInList([position[0] + 1, position[1] + 1], grid),
                self.findVerticeInList(
                    [
                        position[0] + cutDict[orientation][1][0],
                        position[1] + cutDict[orientation][1][1],
                    ],
                    grid,
                ),
            ],
        ]
        # Remove edges in the graph, add the wall position to the list of walls
        for vpair in cutVertices:
            vpair[0].neighbors.remove(vpair[1])
            vpair[1].neighbors.remove(vpair[0])
            self.G.remove_edge(vpair[0], vpair[1])
        self.wallPositions.append([position, orientation])

    # Returns a list of each possible wall placement
    def possibleWallPlacements(self, player):
        # Generates all general possibilities
        orientationDict = {"h": [1, 0], "v": [0, 1]}
        possibilities = [
            [[pos1, pos2], orientation]
            for pos1 in range(8)
            for pos2 in range(8)
            for orientation in ["v", "h"]
        ]

        # Remove all possibilities that intersect with existing walls
        for wall in self.wallPositions:
            for orientation in ["v", "h"]:
                if [wall[0], orientation] in possibilities:
                    possibilities.remove([wall[0], orientation])
            nextWallPos1 = [
                [
                    wall[0][0] + orientationDict[wall[1]][0],
                    wall[0][1] + orientationDict[wall[1]][1],
                ],
                wall[1],
            ]
            nextWallPos2 = [
                [
                    wall[0][0] - orientationDict[wall[1]][0],
                    wall[0][1] - orientationDict[wall[1]][1],
                ],
                wall[1],
            ]
            for nextWallPos in [nextWallPos1, nextWallPos2]:
                if self.isWallPositionLegal(nextWallPos[0]) and (
                    nextWallPos in possibilities
                ):
                    possibilities.remove(nextWallPos)
        # remove all possibilities that block the path to goals
        for wall in possibilities.copy():
            copyGrid = Grid()
            for w1 in self.wallPositions:
                copyGrid.placeWall(w1[0], w1[1])
            copyGrid.placeWall(wall[0], wall[1])
            for p in player:
                goal = copyGrid.findVertice([-p.pnum, -p.pnum])
                currentPosition = copyGrid.findVertice(p.position)
                if not self.BFS(currentPosition, goal, copyGrid.vertices):
                    possibilities.remove(wall)
        return possibilities

    # checks if wall coordinates lies in the grid
    def isWallPositionLegal(self, newPosition):
        for e in newPosition:
            if e < 0 or e > 7:
                return False
        return True

    # Does a BFS and returns True if a path exists, false otherwise
    def BFS(self, vertice1, vertice2, grid):
        for v in grid:
            v.marked = False
        vertice1.marked = True
        queue = [vertice1]
        while len(queue) > 0:
            currentVertice = queue.pop(0)
            for otherVertice in currentVertice.neighbors:
                if otherVertice == vertice2:
                    return True
                if (otherVertice.marked == False) and otherVertice.position[0] >= 0:
                    queue.append(otherVertice)
                    otherVertice.marked = True
        return False

    # Graph visualization method. Can safely be removed
    def showGraph(self):
        pos = {node: node.position for node in self.vertices}
        nx.draw(self.G, pos)
        plt.show()


# Class for each player
class Piece:
    # Defines the players position, player number, and how many walls they can place
    def __init__(self, position, pnum, game):
        self.position = position
        self.pnum = pnum
        self.game = game
        self.wallsLeft = 10

    # Moves the player "regularly", as in one tile in any direction
    def move(self, direction):
        if self.checkNewPosition(direction):
            self.position[0] += moveDict[direction][0]
            self.position[1] += moveDict[direction][1]

    # Moves the player to a specific position
    def moveToPosition(self, position):
        self.position = position

    # Checks if a move in a specific direction would result in the player being on the board,
    # and not on the same tile as the other player
    def checkNewPosition(self, direction):
        newPos = self.position.copy()
        newPos[0] += moveDict[direction][0]
        newPos[1] += moveDict[direction][1]

        if (
            self.game.nonactivePlayer.position != newPos
            and (newPos[0] < 9 and newPos[0] > -1)
            and (newPos[1] < 9 and newPos[1] > -1)
        ):
            return True
        return False

    # Computes a list of possible moves. This includes the "esoteric" moves, when you jump over the other player
    def possibleMoves(self):
        # compute all the regular moves
        moveList = []
        currentVertice = self.game.grid.findVertice(self.position)
        moveList = [
            [self.position[0] + moveDict[e][0], self.position[1] + moveDict[e][1]]
            for e in ["d", "u", "l", "r"]
            if self.checkNewPosition(e)
        ]
        # Remove the moves where a wall is in the way
        tempList = moveList.copy()
        for move in tempList:
            newVertice = self.game.grid.findVertice(move)
            if newVertice not in currentVertice.neighbors:
                moveList.remove(move)
        # Add esoteric moves
        if len(moveList) != 4:
            for e in ["d", "u", "l", "r"]:
                verticeInDirection = self.game.grid.findVertice(
                    [
                        self.position[0] + moveDict[e][0],
                        self.position[1] + moveDict[e][1],
                    ]
                )
                if (
                    self.game.nextToEachOtherDir(e)
                    and verticeInDirection in currentVertice.neighbors
                ):
                    posistionVerticeDoubleMove = [
                        self.position[0] + 2 * moveDict[e][0],
                        self.position[1] + 2 * moveDict[e][1],
                    ]
                    if (
                        self.game.isPositionLegal(posistionVerticeDoubleMove)
                        and self.game.grid.findVertice(
                            [
                                self.position[0] + 2 * moveDict[e][0],
                                self.position[1] + 2 * moveDict[e][1],
                            ]
                        )
                        in verticeInDirection.neighbors
                    ):
                        moveList.append(
                            [
                                self.position[0] + 2 * moveDict[e][0],
                                self.position[1] + 2 * moveDict[e][1],
                            ]
                        )
                    else:
                        for vertice in verticeInDirection.neighbors:
                            if vertice != currentVertice:
                                moveList.append(vertice.position)
                        pass
        return moveList


# Class for the game itself
class Quoridor:
    # Defines the 2 players, the grid, and additional information
    def __init__(self):
        self.p1 = Piece([4, 8], 1, self)
        self.p2 = Piece([4, 0], 2, self)
        self.currentPlayer = self.p1
        self.nonactivePlayer = self.p2
        self.grid = Grid()
        self.game_over = False
        self.won = None

    # Checks if the 2 players are standing next to each other
    def nextToEachOther(self):
        if (
            self.p1.position[0] == self.p2.position[0]
            and abs(self.p1.position[1] - self.p2.position[1]) == 1
        ) or (
            self.p1.position[1] == self.p2.position[1]
            and abs(self.p1.position[0] - self.p2.position[0]) == 1
        ):
            return True
        return False

    # Checks if a player position is within the grid
    def isPositionLegal(self, newPosition):
        for e in newPosition:
            if e < 0 or e > 8:
                return False
        return True

    # Lets the active player take their turn
    def takeTurn(self):
        while True:
            print("Move your piece or place a wall")
            print("Syntax:")
            print(
                "To move your piece, write the square you want to move it to like this: 0,0"
            )
            print(
                "To place a wall, write the intersection you want to place it at and the orientation as 'v' or 'h': 0,0v\n"
            )
            choice = input("Write your move:\n")
            # Movement action
            if len(choice) == 3:
                try:
                    newPos = [int(choice.split(",")[0]), int(choice.split(",")[1])]
                    if newPos in self.currentPlayer.possibleMoves():
                        self.currentPlayer.moveToPosition(newPos)
                        return
                except:
                    print("Illegal move, try again\n\n")
                    continue
            # Wall action
            if len(choice) == 4:
                try:
                    newWallPos = [
                        [int(choice.split(",")[0]), int(choice.split(",")[1][0])],
                        choice.split(",")[1][1],
                    ]
                    # print(self.currentPlayer.wallsLeft)
                    # print(self.grid.possibleWallPlacements())
                    if self.currentPlayer.wallsLeft > 0 and (
                        newWallPos
                        in self.grid.possibleWallPlacements(
                            [self.currentPlayer, self.nonactivePlayer]
                        )
                    ):
                        self.grid.placeWall(newWallPos[0], newWallPos[1])
                        self.currentPlayer.wallsLeft = self.currentPlayer.wallsLeft - 1
                        return
                except:
                    print("Illegal move, try again\n\n")
                    continue
            print("Illegal move, try again")

    # Checks if the players are next to each other in a specific direction
    def nextToEachOtherDir(self, direction):
        newPos = [
            self.currentPlayer.position[0] + moveDict[direction][0],
            self.currentPlayer.position[1] + moveDict[direction][1],
        ]
        if newPos == self.nonactivePlayer.position:
            return True
        return False

    # Update the state after an action
    def update(self):
        self.printBoard()
        p1walls = self.p1.wallsLeft
        p2walls = self.p2.wallsLeft
        print(f"Player 1 has {p1walls} walls left")
        print(f"Player 2 has {p2walls} walls left")
        # self.grid.showGraph()
        if self.p1.position[1] == 0:
            self.game_over = True
        elif self.p2.position[1] == 8:
            self.game_over = True
        else:
            if self.p1 != self.currentPlayer:
                self.currentPlayer = self.p1
                self.nonactivePlayer = self.p2
            else:
                self.currentPlayer = self.p2
                self.nonactivePlayer = self.p1

    # Prints the board. Should certainly be rewritten to not compute the board each time,
    # but if graphic interface is made, it probably doesn't matter
    def printBoard(self):
        board = []
        flatline = ["-" for i in range(19)]
        board.append(flatline)
        # Add the grid and the players to the list of strings
        for y in range(9):
            line = []
            for x in range(9):
                line.append("|")
                if [x, y] == self.p1.position:
                    line.append("1")
                elif [x, y] == self.p2.position:
                    line.append("2")
                else:
                    line.append(" ")
            line.append("|")
            board.append(line)
            board.append(flatline.copy())
        # Add the walls
        for wall in self.grid.wallPositions:
            x, y = wall[0]
            board[(y + 1) * 2][(x + 1) * 2] = "#"
            if wall[1] == "v":
                board[(y + 1) * 2 - 1][(x + 1) * 2] = "#"
                board[(y + 2) * 2 - 1][(x + 1) * 2] = "#"
            else:
                board[(y + 1) * 2][(x + 1) * 2 - 1] = "#"
                board[(y + 1) * 2][(x + 2) * 2 - 1] = "#"
        # print the board
        for l in board:
            string = "".join(l)
            print(string)

    # This starts the gameplay loop
    def play(self):
        self.printBoard()
        print()
        while self.game_over != True:
            print(self.currentPlayer.possibleMoves())
            self.takeTurn()
            self.update()
        print("Player " + str(self.currentPlayer.pnum) + " won!")


game = Quoridor()
game.play()
