import copy
import networkx as nx
import matplotlib.pyplot as plt
moveDict = {"d": [0, 1], "u": [0, -1], "l": [-1, 0], "r": [1, 0]}

class Vertice():
    def __init__(self, position):
        self.position = position
        self.neighbors = []
        self.marked = False

class Edge():
    def __init__(self, v1, v2):
        self.vertices = [v1, v2]

class Grid():
    def __init__(self):
        self.G = nx.Graph()
        self.vertices = [Vertice([e1, e2]) for e1 in range(9) for e2 in range(9)]
        for v in self.vertices:
            self.G.add_node(v)
        self.wallPositions = []
        for v1 in self.vertices:
            for v2 in self.vertices:
                if (v1 != v2 and v1 not in v2.neighbors) and abs(v1.position[0] - v2.position[0]) + abs(v1.position[1] - v2.position[1]) == 1:
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

    def findVertice(self, position):
        return self.findVerticeInList(position, self.vertices)
    
    def findVerticeInList(self, position, list1):
        for e in list1:
            if e.position == position:
                return e
        return None
    
    def placeWall(self, position, orientation):
        self.placeWallInList(position, orientation, self.vertices)

    def placeWallInList(self, position, orientation, grid):
        cutDict = {"v": [[1, 0], [0, 1]], "h": [[0, 1], [1, 0]]}
        cutVertices = [[self.findVerticeInList(position, grid), self.findVerticeInList([position[0] + cutDict[orientation][0][0], position[1] + cutDict[orientation][0][1]], grid)], [self.findVerticeInList([position[0] + 1, position[1] + 1], grid), self.findVerticeInList([position[0] + cutDict[orientation][1][0], position[1] + cutDict[orientation][1][1]], grid)]]
        for vpair in cutVertices:
            vpair[0].neighbors.remove(vpair[1])
            vpair[1].neighbors.remove(vpair[0])
            self.G.remove_edge(vpair[0], vpair[1])
        self.wallPositions.append([position, orientation])

    def possibleWallPlacements(self, player):
        orientationDict = {"h": [1, 0], "v": [0, 1]}
        possibilities = [[[pos1, pos2], orientation] for pos1 in range(8) for pos2 in range(8) for orientation in ["v", "h"]]

        for wall in self.wallPositions:
            for orientation in ["v", "h"]:
                if [wall[0], orientation] in possibilities:
                    possibilities.remove([wall[0], orientation])
            nextWallPos1 = [[wall[0][0] + orientationDict[wall[1]][0], wall[0][1] + orientationDict[wall[1]][1]], wall[1]]
            nextWallPos2 = [[wall[0][0] - orientationDict[wall[1]][0], wall[0][1] - orientationDict[wall[1]][1]], wall[1]]
            for nextWallPos in [nextWallPos1, nextWallPos2]:
                if self.isWallPositionLegal(nextWallPos[0]) and (nextWallPos in possibilities):
                    possibilities.remove(nextWallPos)
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

    def isWallPositionLegal(self, newPosition):
        for e in newPosition:
            if e < 0 or e > 7:
                return False
        return True
    
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
    
    def showGraph(self):
        pos = {node:node.position for node in self.vertices}
        nx.draw(self.G, pos)
        plt.show()
    
    
class Piece():
    def __init__(self, position, pnum, game):
        self.position = position
        self.pnum = pnum
        self.game = game
        self.wallsLeft = 10

    def move(self, direction):
        if self.checkNewPosition(direction):
            self.position[0] += moveDict[direction][0]
            self.position[1] += moveDict[direction][1]

    def moveToPosition(self, position):
        self.position = position

    def checkNewPosition(self, direction):
        newPos = self.position.copy()
        newPos[0] += moveDict[direction][0]
        newPos[1] += moveDict[direction][1]
        
        if self.game.nonactivePlayer.position != newPos and (newPos[0] < 9 and newPos[0] > -1) and (newPos[1] < 9 and newPos[1] > -1):
            return True
        return False
    
    def possibleMoves(self):
        moveList = []
        currentVertice = self.game.grid.findVertice(self.position)
        moveList = [[self.position[0] + moveDict[e][0], self.position[1] + moveDict[e][1]] for e in ["d", "u", "l", "r"] if self.checkNewPosition(e)]
        tempList = moveList.copy()
        for move in tempList:
            newVertice = self.game.grid.findVertice(move)
            if newVertice not in currentVertice.neighbors:
                moveList.remove(move)
        if len(moveList) != 4:
            for e in ["d", "u", "l", "r"]:
                verticeInDirection = self.game.grid.findVertice([self.position[0] + moveDict[e][0], self.position[1] + moveDict[e][1]])
                if self.game.nextToEachOtherDir(e) and verticeInDirection in currentVertice.neighbors:
                    posistionVerticeDoubleMove = [self.position[0] + 2 * moveDict[e][0], self.position[1] + 2 * moveDict[e][1]]
                    if self.game.isPositionLegal(posistionVerticeDoubleMove) and self.game.grid.findVertice([self.position[0] + 2 * moveDict[e][0], self.position[1] + 2 * moveDict[e][1]]) in verticeInDirection.neighbors:
                        moveList.append([self.position[0] + 2 * moveDict[e][0], self.position[1] + 2 * moveDict[e][1]])
                    else:
                        for vertice in verticeInDirection.neighbors:
                            if vertice != currentVertice:
                                moveList.append(vertice.position)
                        pass
        return moveList
            
class Quoridor():
    def __init__(self):
        self.p1 = Piece([4, 8], 1, self)
        self.p2 = Piece([4, 0], 2, self)
        self.currentPlayer = self.p1
        self.nonactivePlayer = self.p2
        self.grid = Grid()
        self.game_over = False
        self.won = None

    def nextToEachOther(self):
        if (self.p1.position[0] == self.p2.position[0] and abs(self.p1.position[1] - self.p2.position[1]) == 1) or (self.p1.position[1] == self.p2.position[1] and abs(self.p1.position[0] - self.p2.position[0]) == 1):
            return True
        return False
    
    def isPositionLegal(self, newPosition):
        for e in newPosition:
            if e < 0 or e > 8:
                return False
        return True
    
    def takeTurn(self):
        while(True):
            print("Move your piece or place a wall")
            print("Syntax:")
            print("To move your piece, write the square you want to move it to like this: 0,0")
            print("To place a wall, write the intersection you want to place it at and the orientation as 'v' or 'h': 0,0v\n")
            choice = input("Write your move:\n")
            if len(choice) == 3:
                try:
                    newPos = [int(choice.split(",")[0]), int(choice.split(",")[1])]
                    if newPos in self.currentPlayer.possibleMoves():
                        self.currentPlayer.moveToPosition(newPos)
                        return
                except:
                    print("Illegal move, try again\n\n")
                    continue
            if len(choice) == 4:
                try:
                    newWallPos = [[int(choice.split(",")[0]), int(choice.split(",")[1][0])], choice.split(",")[1][1]]
                    #print(self.currentPlayer.wallsLeft)
                    #print(self.grid.possibleWallPlacements())
                    if self.currentPlayer.wallsLeft > 0 and (newWallPos in self.grid.possibleWallPlacements([self.currentPlayer, self.nonactivePlayer])):
                        self.grid.placeWall(newWallPos[0], newWallPos[1])
                        self.currentPlayer.wallsLeft = self.currentPlayer.wallsLeft - 1
                        return
                except:
                    print("Illegal move, try again\n\n")
                    continue
            print("Illegal move, try again")

    
    def nextToEachOtherDir(self, direction):
        newPos = [self.currentPlayer.position[0] + moveDict[direction][0], self.currentPlayer.position[1] + moveDict[direction][1]]
        if newPos == self.nonactivePlayer.position:
            return True
        return False
    
    def update(self):
        self.printBoard()
        #self.grid.showGraph()
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

    def printBoard(self):
        board = []
        flatline = ["-" for i in range(19)]
        board.append(flatline)
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
        for wall in self.grid.wallPositions:
            x, y = wall[0]
            board[(y+1)*2][(x+1)*2] = '#'
            if wall[1] == "v":
                board[(y+1)*2-1][(x+1)*2] = '#'
                board[(y+2)*2-1][(x+1)*2] = '#'
            else:
                board[(y+1)*2][(x+1)*2-1] = '#'
                board[(y+1)*2][(x+2)*2-1] = '#'
        for l in board:
            string = "".join(l)
            print(string)

    def play(self):
        self.printBoard()
        print()
        while self.game_over != True:
            print(self.currentPlayer.possibleMoves())
            self.takeTurn()
            #direction = input("Player " + str(self.currentPlayer.pnum) + "'s turn. Which direction to go?\n")
            #self.currentPlayer.move(direction)
            self.update()
        print("Player " + str(self.currentPlayer.pnum) + " won!")


game = Quoridor()
#game.grid.showGraph()
# game.grid.wallPositions = [[[1, 1], "v"], [[0, 0], "h"]]
game.play()