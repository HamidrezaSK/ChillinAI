# from ks.models import (World, Police, Terrorist, Bomb, Position, Constants,
#                      ESoundIntensity, ECell, EAgentStatus)
from ks.models import ECell
import collections
from dijkstar import Graph, find_path


class Node:
    def __init__(self, x, y, width):  # ___x   (x,y) => cordinates
        self.coordinates = (y, x)  # |
        self.neighbors = []
        self.id = y + x * width


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
        self.bombs = []
        self._init_map()

    # find all paths from destination node with specific length
    # first argument is the graph, second is source node, third is the length
    def all_paths_from_source_node(self, G, u, n):
        if n == 0:
            return [[u]]
        paths = []
        for neighbor in G[u]:
            for path in self.all_paths_from_source_node(G, neighbor, n - 1):
                if u not in path:
                    paths.append([u] + path)
        return paths

    # generates all zone nodes from paths
    def final_zone(self, paths):
        zone = []
        for i in paths:
            for j in i:
                zone.append(j)
        zone = list(dict.fromkeys(zone))
        return zone


    def analyze_zones(self,zones,dijkstra):
        ZonesToZones = []
        for i in range(len(zones)-1):
            for j in range(i+1, len(zones)):
                has_in_common_flag = False
                common_nodes = []
                for z in zones[i]:
                    if z in zones[j]:
                        has_in_common_flag = True
                        common_nodes.append(z)
                if has_in_common_flag:
                    ZoneToZone = [{"hascommon":True},common_nodes]
                else:
                    # calculate the dijkstra between zones
                    try:
                        path = dijkstra._findpath(zones[i][0],zones[j][0])

                        ZoneToZone = [{"hascommon":False},path]
                    except IndexError:
                        print(i,j,zones)
                ZonesToZones += ZoneToZone
        return ZonesToZones




    def get_pos_by_node(self, node):

        for i in range(self.height):
            if node in self.Nodes[i]:
                j = self.Nodes[i].index(node)
                value = [i, j]
                return value

    def get_node_by_id(self, id):
        for i in range(self.height):
            for j in range(self.width):
                if self.Nodes[i][j].id == id:
                    return self.Nodes[i][j]

    def _init_map(self):  # to initiate Map you must use this;now it used in __init__
        for i in range(self.height):
            self.Nodes.append([])
            for j in range(self.width):
                node = Node(i, j, self.width)
                self.Nodes[i].append(node)
                if self.board[i][j] == ECell.LargeBombSite:
                    self.LargeBombSites.append((i, j))
                    self.bombs.append((i, j))
                elif self.board[i][j] == ECell.VastBombSite:
                    self.VastBombSites.append((i, j))
                    self.bombs.append((i, j))
                elif self.board[i][j] == ECell.SmallBombSite:
                    self.SmallBombSites.append((i, j))
                    self.bombs.append((i, j))
                elif self.board[i][j] == ECell.MediumBombSite:
                    self.MediumBombSites.append((i, j))
                    self.bombs.append((i, j))
        # print(self.bombs)

        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == ECell.Empty or (i, j) in self.bombs:
                    self._init_neighbors_graph(self.Nodes[i][j], False)
                else:
                    self._init_neighbors_graph(self.Nodes[i][j], True)

    def bomb_check(self, board):
        count = len(self.bombs)
        self.bombs = []
        for i in range(self.height):
            for j in range(self.width):
                if (board[i][j] == ECell.LargeBombSite) or (board[i][j] == ECell.VastBombSite) or (
                        board[i][j] == ECell.SmallBombSite) or (board[i][j] == ECell.MediumBombSite):
                    self.bombs.append((i, j))
        if count != len(self.bombs):
            return True
        return False

    def _init_neighbors_graph(self, node, iswall):  # this function will be called in _init_map function.s
        j = node.coordinates[0]
        i = node.coordinates[1]

        neighbors = []

        try:
            if not iswall:
                if self.board[i + 1][j] != ECell.Wall:
                    neighbors.append(self.Nodes[i + 1][j])
                if self.board[i - 1][j] != ECell.Wall:
                    neighbors.append(self.Nodes[i - 1][j])
                if self.board[i][j + 1] != ECell.Wall:
                    neighbors.append(self.Nodes[i][j + 1])
                if self.board[i][j - 1] != ECell.Wall:
                    neighbors.append(self.Nodes[i][j - 1])
            self.graph[self.Nodes[i][j]] = neighbors

        except:
            pass

    def GetNodeByPosition(self, position):

        return self.Nodes[position[0]][position[1]]


# class BFS:
#     def DoBfs(self, root, map, goal):
#
#         goal_found = False
#
#         graph = map.graph
#
#         parent = {root: root}
#
#         queue = collections.deque([root])
#         while queue:
#             vertex = queue.popleft()
#             i = 0
#
#             try:
#                 for neighbour in graph[vertex]:
#                     i += 1
#
#                     if neighbour == goal:
#                         parent[neighbour] = vertex
#
#                         path = self.print_path(parent, neighbour, root)
#                         goal_found = True
#                         break
#
#                     if neighbour not in parent:
#                         # print("hi")
#                         parent[neighbour] = vertex
#                         queue.append(neighbour)
#             except KeyError:
#                 print(vertex.coordinates)
#         if (goal_found):
#             path_pos_list = []
#             for i in range(len(path)):
#                 path_pos_list.append(map.get_pos_by_node(path[i]))
#             return path_pos_list
#         return []
#
#     def print_path(self, parent, goal, start):
#         path = [goal]
#         # trace the path back till we reach start
#         while goal != start:
#             goal = parent[goal]
#             path.insert(0, goal)
#         return path


class _dijkstra:

    def __init__(self, map, polices, police_vision, isterror):
        self.isterror = isterror
        if self.isterror:
            self.graph = Graph()
            self.map = map
            self.bombs = [self.map.GetNodeByPosition(buby) for buby in self.map.bombs]
            self.finded_path = None
            self.polices = [self.map.GetNodeByPosition((agent.position.y, agent.position.x)) for agent in polices]
            self.police_vision = police_vision
            self.init_graph_terror()
            self.cost_function = lambda u, v, e, prev_e: e['cost']
        else:
            self.graph = Graph()
            self.map = map
            self.finded_path = None
            self.init_graph_ct()
            self.cost_function = lambda u, v, e, prev_e: e['cost']

    def init_graph_ct(self):

        for i in self.map.graph:
            for j in self.map.graph[i]:
                self.graph.add_edge(i.id, j.id, {'cost': 1})

    def init_graph_terror(self):
        dfz = []
        boobytraps = []
        for i in self.polices:
            dfz += self.danger_zone(i, self.police_vision)
        for i in self.bombs:
            # print("fuck")
            boobytraps += self.danger_zone(i,-1)
            # if (i.coordinates == (30,21)):
            #     print("bubytraps:")
            #     for j in boobytraps:
            #         print(j.coordinates)

        for i in self.map.graph:
            for j in self.map.graph[i]:
                if j in dfz:
                    self.graph.add_edge(i.id, j.id, {'cost': 10000})
                elif j in boobytraps:
                    self.graph.add_edge(i.id, j.id, {'cost': 500})
                else:
                    self.graph.add_edge(i.id, j.id, {'cost': 1})

    def danger_zone(self, node, police_vision):

        i = node.coordinates[0]
        j = node.coordinates[1]
        danger_fucking_zone = []
        for y_vision in range(-police_vision - 1, police_vision + 2):
            for x_vision in range(-police_vision - 1, police_vision + 2):
                if abs(x_vision) + abs(y_vision) < police_vision + 2:
                    try:
                        danger_fucking_zone.append(self.map.Nodes[j + y_vision][i + x_vision])
                    except:
                        # print(j + y_vision,end=" ")
                        # print(i + x_vision)
                        # print("height " +str(self.map.height),end=" ")
                        # print("width "+str(self.map.width))
                        pass
                        
        return danger_fucking_zone

    def _findpath(self, source, destination):
        path_list = find_path(self.graph, source, destination, cost_func=self.cost_function).nodes
        cost = find_path(self.graph, source, destination, cost_func=self.cost_function).costs
        position_path_list = []
        cost = list(map(int, cost))
        cost = sum(cost)

        for i in range(len(path_list)):
            node_coordinates = self.map.get_node_by_id(path_list[i]).coordinates
            position_path_list.append([node_coordinates[1], node_coordinates[0]])
        return position_path_list, cost


class decide_for_agent:
    def __init__(self, agent_id, map):
        self.agent = agent_id
        self.map = map
