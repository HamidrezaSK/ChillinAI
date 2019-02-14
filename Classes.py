#from ks.models import (World, Police, Terrorist, Bomb, Position, Constants,
 #                      ESoundIntensity, ECell, EAgentStatus)
from ks.models import ECell
class Node:
	def __init__(self,x,y):                                          # ___x   (x,y) => cordinates
		self.cordinates = (x,y)                                      #|
		self.neighbors = []                                          #|
                                                                     #y
	#def _init_neighbors(self):
class Map:
	def __init__(self,board,width,height): # board , width , height are the game initiate attributes in decide function.
		self.board = board
		self.Nodes = [] #this is the board with nodes.
		self.width = width
		self.height = height
		self.VastBombSites = []
		self.LargeBombSites = []
		self.MediumBombSites = []
		self.SmallBombSites = []
		self._init_map()


	def _init_map(self):              # to initiate Map you must use this;now it used in __init__
		for i in range(self.height):
			self.Nodes.append([])
			for j in range(self.width):
				node = Node(j,i)
				self.Nodes[i].append(node)
				_init_neighbors(node)
				if(self.board[i][j] == LargeBombSite):
					self.LargeBombSites.append((i,j))
				else if(self.board[i][j] == VastBombSite):
					self.VastBombSites.append((i,j))
				else if(self.board[i][j] == SmallBombSite):
					self.SmallBombSites.append((i,j))
	


	def _init_neighbors(self,node):    #this function will be called in _init_map function.s
		i = node.cordinates[1]
		j = node.cordinates[0]		
		try:
			if(self.board[i+1][j] == Empty):
				self.Nodes[i][j].neighbors.append(self.Nodes[i+1][j])
			if(self.board[i-1][j] == Empty):
				self.Nodes[i][j].neighbors.append(self.Nodes[i-1][j])
			if(self.board[i][j+1] == Empty):
				self.Nodes[i][j].neighbors.append(self.Nodes[i][j+1])
			if(self.board[i][j-1] == Empty):
				self.Nodes[i][j].neighbors.append(self.Nodes[i][j-1])
		except:
			pass
