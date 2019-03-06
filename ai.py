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
                except:
                    pass
            planted_bombs = []
            for i in self.world.bombs:
                planted_bombs.append((i.position.y, i.position.x))
            # (len(pathes))
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
                        path[1] = (path[0][0], path[0][1] + 1)
                        break
                    elif (path[0][0] == path[1][0]) and (path[0][1] < path[1][1]):
                        path[1] = (path[0][0], path[0][1] - 1)
                        break
                    elif (path[0][0] > path[1][0]) and (path[0][1] == path[1][1]):
                        path[1] = (path[0][0] - 1, path[0][1])
                        break
                    elif (path[0][0] < path[1][0]) and (path[0][1] == path[1][1]):
                        path[1] = (path[0][0] + 1, path[0][1] + 1)
                        break

            if path[1] in planted_bombs:
                while len(path) != 1:
                    if (path[0][0] == path[1][0]) and (path[0][1] > path[1][1]):
                        path[1] = (path[0][0], path[0][1] + 1)
                        break
                    elif (path[0][0] == path[1][0]) and (path[0][1] < path[1][1]):
                        path[1] = (path[0][0], path[0][1] - 1)
                        break
                    elif (path[0][0] > path[1][0]) and (path[0][1] == path[1][1]):
                        path[1] = (path[0][0] - 1, path[0][1])
                        break
                    elif (path[0][0] < path[1][0]) and (path[0][1] == path[1][1]):
                        path[1] = (path[0][0] + 1, path[0][1] + 1)
                        break

            if doing_bomb_operation:
                self._agent_print(agent.id, 'Continue Bomb Operation')
                continue
            bombsite_direction = self._find_bombsite_direction(agent)
            if bombsite_direction == None and cost < 30000:
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
        # (self.world.bomb)





        print("cycle", self.current_cycle)

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

    def available_bombside(self, path):
        for i in self.primitive:
            if path[2] in i:
                return False
        return True

    def agent_aside_detector(self):
        self.agent_nodes = []
        my_agents = self.world.polices
        for agent in my_agents:
            self.agent_nodes.append((agent.position.y, agent.position.x))
        # print(self.agent_nodes)
        adjacent_agents = []
        for i in range(len(self.agent_nodes) - 1):
            for j in range(i + 1, len(self.agent_nodes)):
                if (self.agent_nodes[i][0] == self.agent_nodes[j][0] and abs(
                            self.agent_nodes[i][1] - self.agent_nodes[j][1]) == 1) or (
                        self.agent_nodes[i][1] == self.agent_nodes[j][1] and abs(
                            self.agent_nodes[i][0] - self.agent_nodes[j][0]) == 1):
                    adjacent_agents.append((self.agent_nodes[i], self.agent_nodes[j]))
        for i in adjacent_agents:
            self.dijkstra_ct.graph.add_edge(self.map.GetNodeByPosition(i[0]).id, self.map.GetNodeByPosition(i[1]).id,
                                            {'cost': 15})
            # return adjacent_agent

    def init_ct(self):

        self.agent_nodes = []

        my_agents = self.world.polices
        self.ct_heard_marked_bombs = [None for i in my_agents]



        # pathes=[[] for i in my_agents]

        self.primitive = [[] for i in my_agents]

        self.map = Classes.Map(self.world.board, self.world.width, self.world.height)
        self.dijkstra_ct = Classes._dijkstra(self.map, None, None, False)
        for agent in my_agents:
            pathes = []
            AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))
            for bomb in self.map.bombs:
                path, cost = self.dijkstra_ct._findpath(AgentNode.id, self.map.GetNodeByPosition((bomb[0], bomb[1])).id)

                pathes.append([path, cost, bomb])

            far_bombs = []
            for i in range(len(pathes)):
                if (pathes[i][1] > 1000):
                    far_bombs.append(pathes[i])
            for i in far_bombs:
                pathes.remove(i)
            pathes = sorted(pathes, key=lambda k: k[1])
            # bomb_count = round(len(pathes)/len(my_agents))
            # for i in pathes:
            #     if self.available_bombside(i):
            #         if len(self.primitive[agent.id])<bomb_count:
            #             self.primitive[agent.id].append(i[2])
            #         elif agent.id == len(my_agents)-1:
            #             self.primitive[agent.id].append(i[2])
            #         else:
            #             break
            for i in pathes:
                if self.available_bombside(i):
                    self.primitive[agent.id].append(i[2])
                    break
            pathes = []
            for bomb in self.map.bombs:
                if (bomb != self.primitive[agent.id][0]):
                    path, cost = self.dijkstra_ct._findpath(
                        self.map.GetNodeByPosition((self.primitive[agent.id][0][0], self.primitive[agent.id][0][1])).id,
                        self.map.GetNodeByPosition((bomb[0], bomb[1])).id)
                    pathes.append([path, cost, bomb])
            # far_bombs = []
            # for i in range(len(pathes)):
            #     if(pathes[i][1]>1000):
            #         far_bombs.append(pathes[i])
            for i in far_bombs:
                for j in pathes:
                    if j[2] == i[2]:
                        pathes.remove(j)
                        break
            pathes = sorted(pathes, key=lambda k: k[1])
            bomb_count = round((len(pathes) + 1) / len(my_agents))
            for i in pathes:
                if self.available_bombside(i):
                    if len(self.primitive[agent.id]) < bomb_count:
                        self.primitive[agent.id].append(i[2])
                    elif agent.id == len(my_agents) - 1:
                        self.primitive[agent.id].append(i[2])
                    else:
                        break
        self.sort_primitive()

        self.current_headed_bomb_ct_list = [None for i in my_agents]

        self.primitive_dict_lists = [{} for i in my_agents]
        for agent in my_agents:
            for bomb in self.primitive[agent.id]:
                index_bomb = self.primitive[agent.id].index(bomb)
                if index_bomb == 0:
                    self.primitive_dict_lists[agent.id][bomb] = True
                else:
                    self.primitive_dict_lists[agent.id][bomb] = False

        self.got_time_to_defuse = [{} for i in my_agents]
        self.strong_bomb_check = [{} for i in my_agents]
        # for agent in my_agents:
        #     for bomb in self.primitive[agent.id]:
        #         self.got_time_to_defuse[agent.id][bomb] = True
                # self.strong_bomb_check[agent.id][bomb] = False
        self.reset_checked_bombs = [int(0) for i in my_agents]

        self.agents_are_checking = [False for i in my_agents]


                    # self.primitive.reverse()

    def sort_primitive(self):
        for primitive in self.primitive:
            index_primitive = self.primitive.index(primitive)

            for i in range(len(primitive) - 1):

                costs_primitive = {}
                costs = []

                for j in range(i + 1, len(primitive)):
                    path, cost = self.dijkstra_ct._findpath(
                        self.map.GetNodeByPosition((primitive[i][0], primitive[i][1])).id,
                        self.map.GetNodeByPosition((primitive[j][0], primitive[j][1])).id)
                    costs.append(cost)
                    costs_primitive[cost] = primitive[j]
                costs.sort()
                least_cost_next_bomb = costs_primitive[costs[0]]
                index = primitive.index(least_cost_next_bomb)
                x = primitive[i + 1]
                primitive[i + 1] = least_cost_next_bomb
                primitive[index] = x

            self.primitive[index_primitive] = primitive


    def move_ct(self):

        my_agents = self.world.polices
        self.agent_aside_detector()
        for agent in my_agents:

            AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))

            doing_bomb_operation = agent.defusion_remaining_time != -1 if self.my_side == 'Police' else agent.planting_remaining_time != -1

            if doing_bomb_operation:
                self._agent_print(agent.id, 'Continue Bomb Operation')
                continue

            bombsite_direction = self._find_bombsite_direction(agent)
            if bombsite_direction is None:

                if(ESoundIntensity.Strong in agent.bomb_sounds) or self.agents_are_checking[agent.id]:
                    # print("i hear sound",agent.id)
                    self.agents_are_checking[agent.id] = True
                    if self.reset_checked_bombs[agent.id] == len(self.primitive[agent.id]):
                        for agent in my_agents:
                            for bomb in self.strong_bomb_check[agent.id]:
                                self.strong_bomb_check[agent.id][bomb] = False
                        self.reset_checked_bombs[agent.id] = 0
                        self.agents_are_checking[agent.id] = False

                    self.strong_sound_reaction(agent,AgentNode)
                    # print(path, agent.id)
                else:


                    self.move_by_primitive(agent, AgentNode)

                    path, cost = self.dijkstra_ct._findpath(AgentNode.id, self.current_headed_bomb_ct_list[agent.id].id)

                    self.move_by_path_list(agent, path)


                self.move_by_primitive(agent, AgentNode)

            else:
                self._agent_print(agent.id, 'Start Bomb Operation')
                if self.my_side == 'Police':
                    self.defuse(agent.id, bombsite_direction)
                else:
                    self.plant(agent.id, bombsite_direction)

    def move_by_primitive(self, agent, agent_node):
        primitive = self.primitive[agent.id]

        try:

            for bomb in self.primitive_dict_lists[agent.id]:

                if self.primitive_dict_lists[agent.id][bomb] == True: #and self.got_time_to_defuse[agent.id][bomb]:
                    self.current_headed_bomb_ct_list[agent.id] = self.map.GetNodeByPosition((bomb[0], bomb[1]))
                    if self.ct_is_arrived(agent, bomb):
                        index_current_bomb = primitive.index(bomb)

                        if index_current_bomb == len(primitive) - 1:
                            self.primitive_dict_lists[agent.id][bomb] = False
                            self.primitive[agent.id].reverse()
                            self.primitive_dict_lists[agent.id][self.primitive[agent.id][1]] = True
                        else:
                            next_bomb = primitive[index_current_bomb + 1]
                            self.primitive_dict_lists[agent.id][bomb] = False
                            self.primitive_dict_lists[agent.id][next_bomb] = True
                elif self.primitive_dict_lists[agent.id][bomb] == True:# and not self.got_time_to_defuse[agent.id][bomb]:
                    self.primitive_dict_lists[agent.id][bomb] = False
                    index_current_bomb = primitive.index(bomb)
                    if(index_current_bomb == len(primitive)-1):
                        self.primitive[agent.id].reverse()
                        self.primitive_dict_lists[agent.id][self.primitive[agent.id][1]] = True
                    else:
                        next_bomb = primitive[index_current_bomb + 1]
                        self.primitive_dict_lists[agent.id][bomb] = False
                        self.primitive_dict_lists[agent.id][next_bomb] = True

        except:
            print(self.primitive_dict_lists)

    def ct_is_arrived(self, agent, bomb):
        agent_coordinates = (agent.position.y, agent.position.x)

        if agent_coordinates[0] == bomb[0] and abs(agent_coordinates[1] - bomb[1]) <= 2:
            return True
        elif agent_coordinates[1] == bomb[1] and abs(agent_coordinates[0] - bomb[0]) <= 2:
            return True
        else:
            return False


    def strong_sound_reaction(self,agent,AgentNode):




        pathes = []
        agent_primitives = self.primitive[agent.id]
        checkList = []
        for i in self.primitive:
            for j in i:
                checkList.append(j)

        for bomb in checkList:
            path, cost = self.dijkstra_ct._findpath(AgentNode.id, self.map.GetNodeByPosition(bomb).id)
            pathes.append([path, cost, bomb])

        pathes = sorted(pathes, key=lambda k: k[1])

        suspicious_nodes = [pathes[0][2],pathes[1][2],pathes[2][2]]

        for node in suspicious_nodes:
            if node not in self.strong_bomb_check[agent.id].keys():
                self.strong_bomb_check[agent.id][node] = False
                self.got_time_to_defuse[agent.id][node]=True

        # print("suspicious nodes are: ",agent.id ,suspicious_nodes)

        for i in range(len(pathes)):
            try:
                if self.strong_bomb_check[agent.id][pathes[i][2]] == False:
                    chosen_path = pathes[i][0]
                    chosen_bomb = pathes[i][2]
                    current_bomb_index = i


                    # print(chosen_bomb,agent.id)
                    break
            except:
                print(agent.id,self.primitive[agent.id],pathes[i][2])

        agent_y = agent.position.y
        agent_x = agent.position.x

        if (agent_y == chosen_bomb[0] and abs(agent_x-chosen_bomb[1]) == 1) or (agent_x == chosen_bomb[1] and abs(agent_y-chosen_bomb[0]) == 1):

            # print("in bomb neighbor")

            self.strong_bomb_check[agent.id][chosen_bomb] = True

            self.reset_checked_bombs[agent.id] += 1

            if current_bomb_index==len(pathes)-1:
                pathes.reverse()
                chosen_path = pathes[1][0]
                chosen_bomb = pathes[1][2]
            else:
                chosen_path = pathes[current_bomb_index+1][0]
                chosen_bomb = pathes[current_bomb_index+1][2]

            self.move_by_path_list(agent, chosen_path)

        else:
            if len(chosen_path) <= self.world.constants.police_vision_distance + 1:
                for bomb in self.world.bombs:
                    y = bomb.position.y
                    x = bomb.position.x
                    if chosen_bomb == (y, x):
                        remaining_time = bomb.explosion_remaining_time
                        if remaining_time < self.world.constants.bomb_defusion_time + self.world.constants.police_vision_distance:
                            self.got_time_to_defuse[agent.id][chosen_bomb] = False
                            # print("remaining time: " + str(remaining_time) + "defusion time : " + str(
                            #     self.world.constants.bomb_defusion_time))
            if self.got_time_to_defuse[agent.id][chosen_bomb]:
                self.move_by_path_list(agent, chosen_path)
                # print(chosen_path,agent.id)

            else:
                # print("no time to defuse. continue cycling")



                self.move_by_primitive(agent, AgentNode)
                self.move_by_primitive(agent, AgentNode)

                path, cost = self.dijkstra_ct._findpath(AgentNode.id, self.current_headed_bomb_ct_list[agent.id].id)

                self.move_by_path_list(agent, path)


    def _sum_pos_tuples(self, t1, t2):
        return (t1[0] + t2[0], t1[1] + t2[1])

    def _agent_print(self, agent_id, text):
        print('Agent[{}]: {}'.format(agent_id, text))
