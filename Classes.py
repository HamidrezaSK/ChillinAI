class Node:
	def __init__(self,x,y):
		self.cordinates = (x,y)
		self.neighbors = []

	def _init_neighbors(self):
class Map:
	def __init__(self,board,width,height):
		self.board = []
		self.width = width
		self.height = height
		self._init_map()
	def _init_map(self):
		for i in range(self.height):
			self.board.append([])
			for j in range(self.width):
				node = Node(j,i)
				self.board[i].append(node)
				_init_neighbors(node)
	def _init_neighbors(self,node):
		pass