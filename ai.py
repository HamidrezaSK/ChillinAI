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
        self.map = Classes.Map(self.world.board, self.world.width, self.world.height)
<<<<<<< HEAD
        self.dijkstra = Classes._dijkstra(self.map,self.world.polices,self.world.constants.police_vision_distance)
        self.marked_bombs = [None for i in range(len(self.world.terrorists))]
        self.recent_bombs = [None for i in range(len(self.world.terrorists))]

=======
        self.dijkstra = Classes._dijkstra(self.map, self.world.polices, self.world.constants.police_vision_distance,
                                          True)
        self.dijkstra_ct = Classes._dijkstra(self.map, None, None, False)
        self.marked_bombs = [None for i in range(len(self.world.terrorists))]
        self.recent_bombs = [None for i in range(len(self.world.terrorists))]
>>>>>>> 2d130c4f3c66ef156af0d6ebf0c417e3018a1953

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

<<<<<<< HEAD
        if self.my_side == 'Terrorist':
            #defining the dijkstra instance
            if (self.world.polices):
                # refresh map
                self.map = Classes.Map(self.world.board, self.world.width, self.world.height)
                self.dijkstra = Classes._dijkstra(self.map,self.world.polices,self.world.constants.police_vision_distance)
            if (self.map.bomb_check(self.world.board)):
                # refresh map
                self.map = Classes.Map(self.world.board, self.world.width, self.world.height)
                self.dijkstra = Classes._dijkstra(self.map,self.world.polices,self.world.constants.police_vision_distance)

            my_agents = self.world.polices if self.my_side == 'Police' else self.world.terrorists
            for agent in my_agents:
                if agent.status == EAgentStatus.Dead:
                    continue
                AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))  # find root node
                pathes = []
                for i in self.map.bombs:
                    try:
                        path ,cost=self.dijkstra._findpath(AgentNode.id,self.map.GetNodeByPosition(i).id)
                        pathes.append([path,cost,i])
                    except:
                        print(str(i) + " :out of reach")
                planted_bombs = []
                for i in self.world.bombs:
                    planted_bombs.append((i.position.y,i.position.x))

                pathes = sorted(pathes,key = lambda k : k[1])
                for i in range (len(pathes)):
                    if (pathes[i][2] not in self.marked_bombs or pathes[i][2] == self.marked_bombs[agent.id]) and pathes[i][2] not in planted_bombs:
                        path = pathes[i][0]
                        self.marked_bombs[agent.id] = pathes[i][2]
                        break
                doing_bomb_operation = agent.defusion_remaining_time != -1 if self.my_side == 'Police' else agent.planting_remaining_time != -1

                if doing_bomb_operation:
                    self._agent_print(agent.id, 'Continue Bomb Operation')
                    continue
                bombsite_direction = self._find_bombsite_direction(agent)
                if bombsite_direction == None:
                    self.move_by_path_list(agent, path)
                else:
                    self._agent_print(agent.id, 'Start Bomb Operation')
                    if self.my_side == 'Police':
                        self.defuse(agent.id, bombsite_direction)
                    else:
                        self.plant(agent.id, bombsite_direction)
        else:

            # print(map.graph[map.GetNodeByPosition((22,35))])

            print('decide')
            # dijkstra = Classes._dijkstra(map,)

            my_agents = self.world.polices if self.my_side == 'Police' else self.world.terrorists
            for agent in my_agents:
                if agent.status == EAgentStatus.Dead:
                    continue


                AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))  # find root node

                bomb  = self.map.GetNodeByPosition(self.map.MediumBombSites[0])

                testnode1 = self.map.GetNodeByPosition((3, 2))

                testnode2 = self.map.GetNodeByPosition((16, 10))



                





                doing_bomb_operation = agent.defusion_remaining_time != -1 if self.my_side == 'Police' else agent.planting_remaining_time != -1

                if doing_bomb_operation:
                    self._agent_print(agent.id, 'Continue Bomb Operation')
                    continue

                # print(self.world.board[22][35])

                path,cost = self.dijkstra._findpath(AgentNode.id, testnode2.id)

                if (agent.id == 0):

                    self.move_by_path_list(agent, path)

                bombsite_direction = self._find_bombsite_direction(agent)
                # if bombsite_direction == None:
                #     self._agent_print(agent.id, 'Random Move')
                #     self.move(agent.id, random.choice(self._empty_directions(agent.position)))
                # else:
                #     self._agent_print(agent.id, 'Start Bomb Operation')
                #     if self.my_side == 'Police':
                #         self.defuse(agent.id, bombsite_direction)
                #     else:
                #         self.plant(agent.id, bombsite_direction)
=======
        if self.my_side == 'Police':
            self.ct_decide()
        else:
            self.terror_decide()
>>>>>>> 2d130c4f3c66ef156af0d6ebf0c417e3018a1953

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
                    print(str(i) + " :out of reach")
            planted_bombs = []
            for i in self.world.bombs:
                planted_bombs.append((i.position.y, i.position.x))

            pathes = sorted(pathes, key=lambda k: k[1])
            for i in range(len(pathes)):
                if (pathes[i][2] not in self.marked_bombs or pathes[i][2] == self.marked_bombs[agent.id]) and pathes[i][
                    2] not in planted_bombs:
                    path = pathes[i][0]
                    self.marked_bombs[agent.id] = pathes[i][2]
                    break
            doing_bomb_operation = agent.defusion_remaining_time != -1 if self.my_side == 'Police' else agent.planting_remaining_time != -1

            if doing_bomb_operation:
                self._agent_print(agent.id, 'Continue Bomb Operation')
                continue
            bombsite_direction = self._find_bombsite_direction(agent)
            if bombsite_direction == None:
                self.move_by_path_list(agent, path)
            else:
                self._agent_print(agent.id, 'Start Bomb Operation')
                if self.my_side == 'Police':
                    self.defuse(agent.id, bombsite_direction)
                else:
                    self.plant(agent.id, bombsite_direction)

    def ct_decide(self):
        my_agents = self.world.polices if self.my_side == 'Police' else self.world.terrorists

        bomb1 = self.map.GetNodeByPosition((self.map.VastBombSites[0][0], self.map.VastBombSites[0][1]))

        bomb2 = self.map.GetNodeByPosition((self.map.VastBombSites[2][0], self.map.VastBombSites[2][1]))

        all_zones = []

        for bomb in self.map.VastBombSites:
            bomb_node = self.map.GetNodeByPosition((bomb[0], bomb[1]))

            paths = self.map.all_paths_from_source_node(self.map.graph, bomb_node, 8)

            zone = self.map.final_zone(paths)

            all_zones.append(zone)
        ZoneToZone_analises = self.map.analyze_zones(all_zones,self.dijkstra_ct)

        print(ZoneToZone_analises)

        for agent in my_agents:
            if agent.status == EAgentStatus.Dead:
                continue

            AgentNode = self.map.GetNodeByPosition((agent.position.y, agent.position.x))  # find root node

            testnode1 = self.map.GetNodeByPosition((3, 2))

            testnode2 = self.map.GetNodeByPosition((16, 10))

            doing_bomb_operation = agent.defusion_remaining_time != -1 if self.my_side == 'Police' else agent.planting_remaining_time != -1

            if doing_bomb_operation:
                self._agent_print(agent.id, 'Continue Bomb Operation')
                continue

            # # print(self.world.board[22][35])

            # path = dijkstra._findpath(AgentNode.id, testnode2.id)

            # if (agent.id == 0):

            #     self.move_by_path_list(agent, path)

            bombsite_direction = self._find_bombsite_direction(agent)
            if bombsite_direction is None:
                if agent.id == 1:
                    path = self.dijkstra_ct._findpath(AgentNode.id, bomb1.id)[0]
                    self.move_by_path_list(agent, path)
                elif agent.id == 0:
                    path = self.dijkstra_ct._findpath(AgentNode.id, bomb2.id)[0]
                    self.move_by_path_list(agent, path)
            else:
                self._agent_print(agent.id, 'Start Bomb Operation')
                if self.my_side == 'Police':
                    self.defuse(agent.id, bombsite_direction)
                else:
                    self.plant(agent.id, bombsite_direction)

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

    def _sum_pos_tuples(self, t1, t2):
        return (t1[0] + t2[0], t1[1] + t2[1])

    def _agent_print(self, agent_id, text):
        print('Agent[{}]: {}'.format(agent_id, text))