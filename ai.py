# -*- coding: utf-8 -*-

# python imports
import random

# chillin imports
from chillin_client import RealtimeAI

# project imports
from ks.models import (World, Police, Terrorist, Bomb, Position, Constants,
                       ESoundIntensity, ECell, EAgentStatus)
from ks.commands import DefuseBomb, PlantBomb, Move, ECommandDirection

# ai imports
import Classes


class AI(RealtimeAI):
    def __init__(self, world):
        super(AI, self).__init__(world)
        self.done = False

    def initialize(self):
        print('initialize')

        if self.my_side == "Police":
            self.init_ct()
        else:
            self.map = Classes.Map(self.world.board, self.world.width, self.world.height)
            self.dijkstra = Classes._dijkstra(self.map, self.world.polices, self.world.constants.police_vision_distance,
                                              True)
            self.marked_bombs = [None for i in range(len(self.world.terrorists))]
            self.recent_bombs = [None for i in range(len(self.world.terrorists))]

        self.DIRECTIONS = [
            ECommandDirection.Up,
            ECommandDirection.Right,
            ECommandDirection.Down,
            ECommandDirection.Left,
        ]

        self.DIR_TO_POS = {
            ECommandDirection.Up: (+0, -1),
            ECommandDirection.Right: (+1, +0),
            ECommandDirection.Down: (+0, +1),
            ECommandDirection.Left: (-1, +0),
        }

        self.BOMBSITES_ECELL = [
            ECell.SmallBombSite,
            ECell.MediumBombSite,
            ECell.LargeBombSite,
            ECell.VastBombSite,
        ]

    def decide(self):

        if self.my_side == 'Police':
            self.ct_decide()
        else:
            self.terror_decide()

    def plant(self, agent_id, bombsite_direction):
        self.send_command(PlantBomb(id=agent_id, direction=bombsite_direction))

    def defuse(self, agent_id, bombsite_direction):
        self.send_command(DefuseBomb(id=agent_id, direction=bombsite_direction))

    def move(self, agent_id, move_direction):
        self.send_command(Move(id=agent_id, direction=move_direction))

    def move_by_path_list(self, agent, list):
        try:
            path = list
            agent_id = agent.id
            while len(path) != 1:
                if (path[0][0] == path[1][0]) and (path[0][1] > path[1][1]):
                    self.move(agent_id, ECommandDirection.Left)
                    return
                elif (path[0][0] == path[1][0]) and (path[0][1] < path[1][1]):
                    self.move(agent_id, ECommandDirection.Right)
                    return
                elif (path[0][0] > path[1][0]) and (path[0][1] == path[1][1]):
                    self.move(agent_id, ECommandDirection.Up)
                    return
                elif (path[0][0] < path[1][0]) and (path[0][1] == path[1][1]):
                    self.move(agent_id, ECommandDirection.Down)
                    return
        except Exception:
            raise Exception

    def _empty_directions(self, position):
        empty_directions = []

        for direction in self.DIRECTIONS:
            pos = self._sum_pos_tuples((position.x, position.y), self.DIR_TO_POS[direction])
            if self.world.board[pos[1]][pos[0]] == ECell.Empty:
                empty_directions.append(direction)
        return empty_directions

    def terror_decide(self):
        # defining the dijkstra instance
        if (self.world.polices):
            # refresh map
            self.map = Classes.Map(self.world.board, self.world.width, self.world.height)
            self.dijkstra = Classes._dijkstra(self.map, self.world.polices, self.world.constants.police_vision_distance,
                                              True)
        if (self.map.bomb_check(self.world.board)):
            # refresh map
            self.map = Classes.Map(self.world.board, self.world.width, self.world.height)
            self.dijkstra = Classes._dijkstra(self.map, self.world.polices, self.world.constants.police_vision_distance,
                                              True)

        my_agents = self.world.polices if self.my_side == 'Police' else self.world.terrorists
        for agent in my_agents:
            if agent.status == EAgentStatus.Dead:
                continue
            AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))  # find root node
            pathes = []
            for i in self.map.bombs:
                try:
                    path, cost = self.dijkstra._findpath(AgentNode.id, self.map.GetNodeByPosition(i).id)
                    pathes.append([path, cost, i])
                    # print(cost," ",i)
                except:
                    # print(str(i) + " :out of reach")
                    pass
            planted_bombs = []
            for i in self.world.bombs:
                planted_bombs.append((i.position.y, i.position.x))
            # print (len(pathes))
            pathes = sorted(pathes, key=lambda k: k[1])
            path = []
            for i in range(len(pathes)):
                if (pathes[i][2] not in self.marked_bombs or pathes[i][2] == self.marked_bombs[agent.id]) and pathes[i][
                    2] not in planted_bombs:
                    path = pathes[i][0]
                    cost = pathes[i][1]
                    dest = pathes[i][2]
                    self.marked_bombs[agent.id] = pathes[i][2]
                    break
            doing_bomb_operation = agent.defusion_remaining_time != -1 if self.my_side == 'Police' else agent.planting_remaining_time != -1
            try:
                if path[2] in planted_bombs:
                    path = []
            except:
                while len(path) != 1:
                    if (path[0][0] == path[1][0]) and (path[0][1] > path[1][1]):
                        path[1] = (path[0][0],path[0][1]+1)
                        break
                    elif (path[0][0] == path[1][0]) and (path[0][1] < path[1][1]):
                        path[1] = (path[0][0],path[0][1]-1)
                        break
                    elif (path[0][0] > path[1][0]) and (path[0][1] == path[1][1]):
                        path[1] = (path[0][0]-1,path[0][1])
                        break
                    elif (path[0][0] < path[1][0]) and (path[0][1] == path[1][1]):
                        path[1] = (path[0][0]+1,path[0][1]+1)
                        break

            if path[1] in planted_bombs:
                print("damn it move")
                while len(path) != 1:
                    if (path[0][0] == path[1][0]) and (path[0][1] > path[1][1]):
                        path[1] = (path[0][0],path[0][1]+1)
                        break
                    elif (path[0][0] == path[1][0]) and (path[0][1] < path[1][1]):
                        path[1] = (path[0][0],path[0][1]-1)
                        break
                    elif (path[0][0] > path[1][0]) and (path[0][1] == path[1][1]):
                        path[1] = (path[0][0]-1,path[0][1])
                        break
                    elif (path[0][0] < path[1][0]) and (path[0][1] == path[1][1]):
                        path[1] = (path[0][0]+1,path[0][1]+1)
                        break 
            # try:
            #     print("agent: " ,agent.id , " cost: ",cost , " destination: ",dest)
            # except:
            #     pass
            # print()
            if doing_bomb_operation:
                self._agent_print(agent.id, 'Continue Bomb Operation')
                continue
            bombsite_direction = self._find_bombsite_direction(agent)
            if bombsite_direction == None and cost<30000:
                self.move_by_path_list(agent, path)
            else:
                self._agent_print(agent.id, 'Start Bomb Operation')
                if self.my_side == 'Police':
                    self.defuse(agent.id, bombsite_direction)
                else:
                    self.plant(agent.id, bombsite_direction)

    def ct_decide(self):
        my_agents = self.world.polices if self.my_side == 'Police' else self.world.terrorists

        if self.map.bomb_check(self.world.board):
            self.init_ct()

        self.move_ct()
        # print(self.map.LargeBombSites)

        # bomb1 = self.map.GetNodeByPosition((self.map.LargeBombSites[0][0], self.map.LargeBombSites[0][1]))
        # bomb1 = self.map.GetNodeByPosition((23, 35))



        # bomb2 = self.map.GetNodeByPosition((self.map.LargeBombSites[2][0], self.map.LargeBombSites[2][1]))

        # all_zones = []
        #
        # for bomb in self.map.VastBombSites:
        #     bomb_node = self.map.GetNodeByPosition((bomb[0], bomb[1]))
        #
        #     paths = self.map.all_paths_from_source_node(self.map.graph, bomb_node, 8)
        #
        #     zone = self.map.final_zone(paths)
        #
        #     all_zones.append(zone)
        # ZoneToZone_analises = self.map.analyze_zones(all_zones,self.dijkstra_ct)
        #
        # print(ZoneToZone_analises)

        # for agent in my_agents:
        #     if agent.status == EAgentStatus.Dead:
        #         continue

            # AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))  # find root node
            # AgentNodeCoordinates = (agent.position.y, agent.position.x)





            # testnode1 = self.map.GetNodeByPosition((3, 2))
            #
            # testnode2 = self.map.GetNodeByPosition((16, 10))

            # doing_bomb_operation = agent.defusion_remaining_time != -1 if self.my_side == 'Police' else agent.planting_remaining_time != -1

            # if doing_bomb_operation:
            #     self._agent_print(agent.id, 'Continue Bomb Operation')
            #     continue

            # bombsite_direction = self._find_bombsite_direction(agent)
            # if bombsite_direction is None:
            #     pass
                # if agent.id == 1:
                    # path = self.dijkstra_ct._findpath(AgentNode.id, bomb2.id)[0]
                    # self.move_by_path_list(agent, path)


                # elif agent.id == 0:
                #     path = self.dijkstra_ct._findpath(AgentNode.id, bomb1.id)[0]
                #     self.move_by_path_list(agent, path)
                # x = self.map.bombs[::-1]
                # for bomb in x:
                #     bombb = self.map.GetNodeByPosition((bomb[0], bomb[1]))
                #     path_cost = self.dijkstra_ct._findpath(AgentNode.id, bombb.id)
                #     cost = path_cost[1]
                #
                #     bombs_headed = []
                #
                #     for i in self.map.bombs_dic_ct:
                #         if self.map.bombs_dic_ct[bombb] == True:
                #             bombs_headed.append(True)
                #
                #     if cost > 1000 and self.map.bombs_dic_ct[bombb] == False and len(bombs_headed)<3:
                #         self.map.bombs_dic_ct[bombb] = True
                #         self.map.bombs_to_go.append(bombb)
                        # print(path)
                # print(self.map.bombs_to_go[0])
                # print(self.map.bombs_to_go[1])
                # print(self.map.bombs_to_go[2])
                # print(self.map.bombs_to_go)
                        # if agent.id == 0:
                        #     pathh = self.dijkstra_ct._findpath(AgentNode.id, self.map.bombs_to_go[0].id)
                        #     path = pathh[0]
                        #     # cost = pathh[1]
                        #     self.move_by_path_list(agent, path)
                        #     # print(0,cost,path)
                        # elif agent.id == 2:
                        #     pathh = self.dijkstra_ct._findpath(AgentNode.id, self.map.bombs_to_go[1].id)
                        #     path = pathh[0]
                        #     # cost = pathh[1]
                        #     self.move_by_path_list(agent, path)
                        #     # print(1,cost,path)
                        # elif agent.id == 1:
                        #     pathh = self.dijkstra_ct._findpath(AgentNode.id, self.map.bombs_to_go[2].id)
                        #     path = pathh[0]
                        #     # cost = pathh[1]
                        #     self.move_by_path_list(agent, path)
                    # print(2,cost,path)

            # else:
            #     self._agent_print(agent.id, 'Start Bomb Operation')
            #     if self.my_side == 'Police':
            #         self.defuse(agent.id, bombsite_direction)
            #     else:
            #         self.plant(agent.id, bombsite_direction)
        print("hi",self.current_cycle)
    def _find_bombsite_direction(self, agent):
        for direction in self.DIRECTIONS:
            pos = self._sum_pos_tuples((agent.position.x, agent.position.y), self.DIR_TO_POS[direction])
            if self.world.board[pos[1]][pos[0]] in self.BOMBSITES_ECELL:
                has_bomb = self._has_bomb(pos)
                if (self.my_side == 'Police' and has_bomb) or (self.my_side == 'Terrorist' and not has_bomb):
                    return direction
        return None

    def _has_bomb(self, position):
        for bomb in self.world.bombs:
            if position[0] == bomb.position.x and position[1] == bomb.position.y:
                return True
        return False
    def available_bombside(self,path):
        for i in self.primitive:
            if path[2] in i:
                return False
        return True

    def init_ct(self):
        my_agents = self.world.polices
        # pathes=[[] for i in my_agents]

        self.primitive = [[] for i in my_agents]
        
        self.map = Classes.Map(self.world.board, self.world.width, self.world.height)
        self.dijkstra_ct = Classes._dijkstra(self.map, None, None, False)
        for agent in my_agents:
            pathes = []
            AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))
            for bomb in self.map.bombs:
                path,cost = self.dijkstra_ct._findpath(AgentNode.id, self.map.GetNodeByPosition((bomb[0], bomb[1])).id)

                pathes.append([path,cost,bomb])

            far_bombs = []
            for i in range(len(pathes)):
                if(pathes[i][1]>1000):
                    far_bombs.append(pathes[i])
            for i in far_bombs:
                pathes.remove(i)
            pathes = sorted(pathes,key = lambda k : k[1])
            bomb_count = round(len(pathes)/len(my_agents))
            for i in pathes:
                if self.available_bombside(i):
                    if len(self.primitive[agent.id])<bomb_count:
                        self.primitive[agent.id].append(i[2])
                    elif agent.id == len(my_agents)-1:
                        self.primitive[agent.id].append(i[2])
                    else:
                        break
        

        self.sort_primitive()

        self.map.current_headed_bomb_ct_list = [None for i in self.primitive]

        self.map.primitive_dict_lists = [{} for i in self.primitive]
        for agent in my_agents:
            for bomb in self.primitive[agent.id]:
                index_bomb = self.primitive[agent.id].index(bomb)
                if index_bomb == 0:
                    self.map.primitive_dict_lists[agent.id][bomb] = True
                else:
                    self.map.primitive_dict_lists[agent.id][bomb] = False

        print(self.primitive)

        # self.primitive.reverse()


    def sort_primitive(self):
        for primitive in self.primitive:
            index_primitive = self.primitive.index(primitive)

            for i in range(len(primitive)-1):

                costs_primitive = {}
                costs = []

                for j in range(i+1, len(primitive)):
                    path, cost = self.dijkstra_ct._findpath(self.map.GetNodeByPosition((primitive[i][0], primitive[i][1])).id, self.map.GetNodeByPosition((primitive[j][0], primitive[j][1])).id)
                    costs.append(cost)
                    costs_primitive[cost] = primitive[j]
                costs.sort()
                least_cost_next_bomb = costs_primitive[costs[0]]
                index = primitive.index(least_cost_next_bomb)
                x = primitive[i+1]
                primitive[i+1] = least_cost_next_bomb
                primitive[index] = x

            self.primitive[index_primitive] = primitive

    def move_ct(self):

        my_agents = self.world.polices

        for agent in my_agents:

            AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))

            doing_bomb_operation = agent.defusion_remaining_time != -1 if self.my_side == 'Police' else agent.planting_remaining_time != -1

            if doing_bomb_operation:
                self._agent_print(agent.id, 'Continue Bomb Operation')
                continue

            bombsite_direction = self._find_bombsite_direction(agent)
            if bombsite_direction is None:

                self.move_by_primitive(agent, AgentNode)

                path, cost = self.dijkstra_ct._findpath(AgentNode.id, self.map.current_headed_bomb_ct_list[agent.id].id)
                print(path)
                self.move_by_path_list(agent, path)

            else:
                self._agent_print(agent.id, 'Start Bomb Operation')
                if self.my_side == 'Police':
                    self.defuse(agent.id, bombsite_direction)
                else:
                    self.plant(agent.id, bombsite_direction)


    def move_by_primitive(self,agent,agent_node):
        primitive = self.primitive[agent.id]

        for bomb in self.map.primitive_dict_lists[agent.id]:

            if self.map.primitive_dict_lists[agent.id][bomb] == True:
                self.map.current_headed_bomb_ct_list[agent.id] = self.map.GetNodeByPosition((bomb[0], bomb[1]))
                if self.ct_is_arrived(agent,bomb):
                    index_current_bomb = primitive.index(bomb)

                    if index_current_bomb == len(primitive)-1:
                        self.map.primitive_dict_lists[agent.id][bomb] = False
                        self.primitive[agent.id].reverse()
                        self.map.primitive_dict_lists[agent.id][self.primitive[agent.id][0]] = True
                    else:
                        next_bomb = primitive[index_current_bomb+1]
                        self.map.primitive_dict_lists[agent.id][bomb] = False
                        self.map.primitive_dict_lists[agent.id][next_bomb] = True   

    def ct_is_arrived(self,agent,bomb):
        agent_coordinates = (agent.position.y, agent.position.x)

        if agent_coordinates[0] == bomb[0] and abs(agent_coordinates[1]-bomb[1]) == 1:
            return True
        elif agent_coordinates[1] == bomb[1] and abs(agent_coordinates[0]-bomb[0]) == 1:
            return True
        else:
            return False

    def _sum_pos_tuples(self, t1, t2):
        return (t1[0] + t2[0], t1[1] + t2[1])

    def _agent_print(self, agent_id, text):
        print('Agent[{}]: {}'.format(agent_id, text))
