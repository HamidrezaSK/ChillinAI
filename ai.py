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

        for agent in my_agents:
            if agent.status == EAgentStatus.Dead:
                continue

            AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))  # find root node
            # AgentNodeCoordinates = (agent.position.y, agent.position.x)





            # testnode1 = self.map.GetNodeByPosition((3, 2))
            #
            # testnode2 = self.map.GetNodeByPosition((16, 10))

            doing_bomb_operation = agent.defusion_remaining_time != -1 if self.my_side == 'Police' else agent.planting_remaining_time != -1

            if doing_bomb_operation:
                self._agent_print(agent.id, 'Continue Bomb Operation')
                continue

            bombsite_direction = self._find_bombsite_direction(agent)
            if bombsite_direction is None:
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
                if agent.id == 0:
                    pathh = self.dijkstra_ct._findpath(AgentNode.id, self.map.bombs_to_go[0].id)
                    path = pathh[0]
                    # cost = pathh[1]
                    self.move_by_path_list(agent, path)
                    # print(0,cost,path)
                elif agent.id == 2:
                    pathh = self.dijkstra_ct._findpath(AgentNode.id, self.map.bombs_to_go[1].id)
                    path = pathh[0]
                    # cost = pathh[1]
                    self.move_by_path_list(agent, path)
                    # print(1,cost,path)
                elif agent.id == 1:
                    pathh = self.dijkstra_ct._findpath(AgentNode.id, self.map.bombs_to_go[2].id)
                    path = pathh[0]
                    # cost = pathh[1]
                    self.move_by_path_list(agent, path)
                    # print(2,cost,path)

            else:
                self._agent_print(agent.id, 'Start Bomb Operation')
                if self.my_side == 'Police':
                    self.defuse(agent.id, bombsite_direction)
                else:
                    self.plant(agent.id, bombsite_direction)
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


    def init_ct(self):
        my_agents = self.world.polices
        try:
            self.map = Classes.Map(self.world.board, self.world.width, self.world.height,self.map.bombs_to_go)
        except:
            self.map = Classes.Map(self.world.board, self.world.width, self.world.height)
        self.dijkstra_ct = Classes._dijkstra(self.map, None, None, False)
        x = self.map.bombs[::-1]
        for agent in my_agents:

            AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))

            for bomb in x:
                bombb = self.map.GetNodeByPosition((bomb[0], bomb[1]))
                path_cost = self.dijkstra_ct._findpath(AgentNode.id, bombb.id)
                cost = path_cost[1]

                bombs_headed = []

                for i in self.map.bombs_dic_ct:
                    if self.map.bombs_dic_ct[bombb] == True:
                        bombs_headed.append(True)

                if cost > 1000 and self.map.bombs_dic_ct[bombb] == False and len(bombs_headed) < 3 and len(self.map.bombs_to_go) < 3:
                    self.map.bombs_dic_ct[bombb] = True
                    self.map.bombs_to_go.append(bombb)
        print("ct init completed")


    def _sum_pos_tuples(self, t1, t2):
        return (t1[0] + t2[0], t1[1] + t2[1])

    def _agent_print(self, agent_id, text):
        print('Agent[{}]: {}'.format(agent_id, text))
