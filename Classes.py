# from ks.models import (World, Police, Terrorist, Bomb, Position, Constants,
#                      ESoundIntensity, ECell, EAgentStatus)
from ks.models import ECell
import collections


class Node:
    def __init__(self, x, y):  # ___x   (x,y) => cordinates
        self.coordinates = (y, x)  # |
        self.neighbors = []


class Map:
    def __init__(self, board, width,
                 height):  # board , width , height are the game initiate attributes in decide function.
        self.board = board
        self.Nodes = []  # this is the board with nodes.
        self.width = width
        self.height = height
        self.VastBombSites = []
        self.LargeBombSites = []
        self.MediumBombSites = []
        self.SmallBombSites = []
        self.graph = {}
        # self.graph2 = {}
        self._init_map()



    def _init_map(self):  # to initiate Map you must use this;now it used in __init__
        for i in range(self.height):
            self.Nodes.append([])
            for j in range(self.width):
                node = Node(i, j)
                self.Nodes[i].append(node)
                if (self.board[i][j] == ECell.LargeBombSite):
                    self.LargeBombSites.append((i, j))
                elif (self.board[i][j] == ECell.VastBombSite):
                    self.VastBombSites.append((i, j))
                elif (self.board[i][j] == ECell.SmallBombSite):
                    self.SmallBombSites.append((i, j))
                elif (self.board[i][j] == ECell.MediumBombSite):
                    self.MediumBombSites.append((i, j))

        for i in range(self.height):
            for j in range(self.width):
                self._init_neighbors_graph(self.Nodes[i][j])

    def _init_neighbors_graph(self, node):  # this function will be called in _init_map function.s
        i = node.coordinates[0]
        j = node.coordinates[1]

        neighbors = []

        try:

            if (self.board[i + 1][j] == ECell.Empty):
                neighbors.append(self.Nodes[i + 1][j])
            if (self.board[i - 1][j] == ECell.Empty):
                neighbors.append(self.Nodes[i - 1][j])
            if (self.board[i][j + 1] == ECell.Empty):
                neighbors.append(self.Nodes[i][j + 1])
            if (self.board[i][j - 1] == ECell.Empty):
                neighbors.append(self.Nodes[i][j - 1])

            self.graph[self.Nodes[i][j]] = neighbors
            
        except:
            pass


    def GetNodeByPosition(self, position):

        return self.Nodes[position[0]][position[1]]


class BFS:
    def DoBfs(self, root, map, goal):

        graph = map.graph

        parent = {}
        parent[root] = root

        queue = collections.deque([root])
        while queue:
            vertex = queue.popleft()
            i = 0
            for neighbour in graph[vertex]:
                i += 1

                if neighbour == goal:
                    parent[neighbour] = vertex
                    self.print_path(parent, neighbour, root)
                    return

                if neighbour not in parent:
                    # print("hi")
                    parent[neighbour] = vertex
                    queue.append(neighbour)
        print(" No path found ")

    def print_path(self, parent, goal, start):
        path = [goal]
        # trace the path back till we reach start
        while goal != start:
            goal = parent[goal]
            path.insert(0, goal)
        print(path)
