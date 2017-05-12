# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """


  def getAction(self, gameState):
    """
    You do not need to change this method, but you're welcome to.

    getAction chooses among the best options according to the evaluation function.

    Just like in the previous project, getAction takes a GameState and returns
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    "Add more of your code here if you want to"

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design a better evaluation function here.

    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (newFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    # print(newPos)
    newFood = successorGameState.getFood()
    oldFood = currentGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]


    newfoodList = newFood.asList()
    oldFoodList = oldFood.asList()
    sorted(newfoodList, key = lambda food_dis: manhattanDistance(newPos, food_dis))

    if sum(newScaredTimes) == 0:
      for ghost in newGhostStates:
          if manhattanDistance(newPos,ghost.getPosition()) <= 1:
              return -float('Inf')
    
    if len(newfoodList) < len(oldFoodList):
        return float('Inf')
    
    # food_dist = [manhattanDistance(newPos, food) for food in newfoodList]
    shortest_dist = manhattanDistance(newfoodList[0], newPos)
    return 3.5/shortest_dist

    "*** YOUR CODE HERE ***"
    # return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
  """
    Your minimax agent (question 2)
  """

  def MAX_VALUE(self, gameState, depth):
    if depth == 0 or gameState.isWin() or gameState.isLose():
      return [self.evaluationFunction(gameState), "none"]
    value = [-float('Inf'), "none"]
    actionList = []
    succesorList = []
    for action_item in gameState.getLegalActions(0):
      if not action_item == Directions.STOP:
        actionList.append(action_item)
    for successor_item in actionList:
      succesorList.append(gameState.generateSuccessor(0, successor_item))
    index = 0
    if not depth == 0:
      depth -= 1
    # depth -= 1

    for gameState in succesorList:
      temp = self.MIN_VALUE(gameState, depth)
      if value[0] < temp:
        value = [temp, actionList[index]]
    # depth -= 1
    index += 1


    return value

  def MIN_VALUE(self, gameState, depth):
    if gameState.isWin() or gameState.isLose():
      return self.evaluationFunction(gameState)
    value = float('Inf')
    # ghostAction = []
    ghostSuccessor = []
    ghostSuccessor.append(gameState)

    ghost_num = gameState.getNumAgents() - 1
    ghost_max = []

    for ghost_index in range(1, ghost_num + 1):
      temp = []
      for gameState in ghostSuccessor:
        if gameState.isLose() or gameState.isWin():
          ghost_max.append(gameState)
        else:
          ghostAction = [ghost_action for ghost_action in gameState.getLegalActions(ghost_index)]
          # for ghost_action in gameState.getLegalActions(ghost_index):
          #   ghostAction.append(ghost_action)
          temp = temp + [gameState.generateSuccessor(ghost_index, ghost_action) for ghost_action in ghostAction]
      ghostSuccessor = temp[:]


    ghost_max = ghost_max + ghostSuccessor[:]

    for gameState in ghost_max:
      temp_value = self.MAX_VALUE(gameState, depth)
      value = min(value, temp_value[0])

    return value







  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    "*** YOUR CODE HERE ***"
    value = self.MAX_VALUE(gameState, self.depth)
    return value[1] 
    # util.raiseNotDefined()

alpha = -float('Inf')
beta = float('Inf')
class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """


  def MAX_VALUE_AB(self, gameState, depth, alpha, beta):
    if depth == 0 or gameState.isWin() or gameState.isLose():
      return [self.evaluationFunction(gameState), "none"]
    value = [-float('Inf'), "none"]
    actionList = []
    succesorList = []
    for action_item in gameState.getLegalActions(0):
      if not action_item == Directions.STOP:
        actionList.append(action_item)
    for successor_item in actionList:
      succesorList.append(gameState.generateSuccessor(0, successor_item))
    index = 0
    if not depth == 0:
      depth -= 1

    for gameState in succesorList:
      temp = self.MIN_VALUE_AB(gameState, depth, alpha, beta)
      if value[0] < temp:
        value = [temp, actionList[index]]
      index += 1

      if value[0] >= beta:
        return value
      alpha = max(alpha, value[0])


    return value



  def MIN_VALUE_AB(self, gameState, depth, alpha, beta):
    if gameState.isWin() or gameState.isLose():
      return self.evaluationFunction(gameState)
    value = float('Inf')
    # ghostAction = []
    ghostSuccessor = []
    ghostSuccessor.append(gameState)

    ghost_num = gameState.getNumAgents() - 1
    ghost_max = []

    for ghost_index in range(1, ghost_num + 1):
      temp = []
      for gameState in ghostSuccessor:
        if gameState.isLose() or gameState.isWin():
          ghost_max.append(gameState)
        else:
          ghostAction = [ghost_action for ghost_action in gameState.getLegalActions(ghost_index)]
          # for ghost_action in gameState.getLegalActions(ghost_index):
          #   ghostAction.append(ghost_action)
          temp = temp + [gameState.generateSuccessor(ghost_index, ghost_action) for ghost_action in ghostAction]
      ghostSuccessor = temp[:]


    ghost_max = ghost_max + ghostSuccessor[:]

    for gameState in ghost_max:
      temp_value = self.MAX_VALUE_AB(gameState, depth, alpha, beta)
      value = min(value, temp_value[0])
      if value <= alpha:
        return value
      beta = min(beta, value)
    return value

  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    value = self.MAX_VALUE_AB(gameState, self.depth, alpha, beta)
    return value[1]
    # util.raiseNotDefined()


class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Your expectimax agent (question 4)
  """
  def MAX_VALUE_EXP(self, gameState, depth):
    if depth == 0 or gameState.isWin() or gameState.isLose():
      return [self.evaluationFunction(gameState), "none"]
    value = [-float('Inf'), "none"]
    actionList = []
    succesorList = []
    for action_item in gameState.getLegalActions(0):
      if not action_item == Directions.STOP:
        actionList.append(action_item)
    for successor_item in actionList:
      succesorList.append(gameState.generateSuccessor(0, successor_item))
    index = 0
    if not depth == 0:
      depth -= 1
    # depth -= 1

    for gameState in succesorList:
      temp = self.MIN_VALUE_EXP(gameState, depth)
      if value[0] < temp:
        value = [temp, actionList[index]]
    # depth -= 1
      index += 1


    return value

  def MIN_VALUE_EXP(self, gameState, depth):
    if gameState.isWin() or gameState.isLose():
      return self.evaluationFunction(gameState)
    value = 0
    # ghostAction = []
    ghostSuccessor = []
    ghostSuccessor.append(gameState)

    ghost_num = gameState.getNumAgents() - 1
    ghost_max = []

    for ghost_index in range(1, ghost_num + 1):
      temp = []
      for gameState in ghostSuccessor:
        if gameState.isLose() or gameState.isWin():
          ghost_max.append(gameState)
        else:
          ghostAction = [ghost_action for ghost_action in gameState.getLegalActions(ghost_index)]
          # for ghost_action in gameState.getLegalActions(ghost_index):
          #   ghostAction.append(ghost_action)
          temp = temp + [gameState.generateSuccessor(ghost_index, ghost_action) for ghost_action in ghostAction]
      ghostSuccessor = temp[:]


    ghost_max = ghost_max + ghostSuccessor[:]

    for gameState in ghost_max:
      temp_value = self.MAX_VALUE_EXP(gameState, depth)
      value = value + temp_value[0]
    value = value / len(ghost_max)
    return value

  def getAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    "*** YOUR CODE HERE ***"
    value = self.MAX_VALUE_EXP(gameState, self.depth)
    return value[1]
    # util.raiseNotDefined()

def minDistToOther(position_pac, foodList):
  if len(foodList) == 0:
    return 0.0
  sorted(foodList, key = lambda food_dist: manhattanDistance(food_dist, position_pac))

  position_food = foodList[0]
  distance_food = manhattanDistance(position_pac, position_food)
  foodList.remove(position_food)

  while len(foodList) > 0:
    sorted(foodList, key = lambda food_dist: manhattanDistance(food_dist, position_food))
    distance_food = distance_food + manhattanDistance(position_food, foodList[0])
    position_food = foodList[0]
    foodList.remove(position_food)

  return distance_food


def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
  """
  "*** YOUR CODE HERE ***"
  
  ghostStates = [gameState for gameState in currentGameState.getGhostStates()]
  ghostPositionList = [ gameState.getPosition() for gameState in ghostStates]
  currentFood = currentGameState.getFood()
  position_pac = currentGameState.getPacmanPosition()
  newScaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
  foodList = currentFood.asList()


  distToFood = 0.001
  foodWeight = 20
  ghostWeight = -0.5
  currentScore = currentGameState.getScore()
  powerWeight = 0
  food_threshold = 8
  distToGhost = minDistToOther(position_pac, ghostPositionList)
  nearestFood = []
  
  for food in foodList:
     nearestFood.append(manhattanDistance(food, position_pac))
  sorted(nearestFood) 

  if len(foodList) < food_threshold:
    food_threshold = len(foodList)


  for index in range(food_threshold):
    distToFood = distToFood + nearestFood[index]

  

  if newScaredTimes[0] != 0:
      powerWeight = 180 
      ghostWeight = -0.11
  
  return currentScore + (3.5 / distToFood) * foodWeight + distToGhost * ghostWeight + powerWeight

# Abbreviation
better = betterEvaluationFunction








class ContestAgent(MultiAgentSearchAgent):
  """
    Your agent for the mini-contest
  """

  def MAX_VALUE_EXP(self, gameState, depth):
    if depth == 0 or gameState.isWin() or gameState.isLose():
      return [self.evaluationFunction(gameState), "none"]
    value = [-float('Inf'), "none"]
    actionList = []
    succesorList = []
    for action_item in gameState.getLegalActions(0):
      if not action_item == Directions.STOP:
        actionList.append(action_item)
    for successor_item in actionList:
      succesorList.append(gameState.generateSuccessor(0, successor_item))
    index = 0
    if not depth == 0:
      depth -= 1
    # depth -= 1

    for gameState in succesorList:
      temp = self.MIN_VALUE_EXP(gameState, depth)
      if value[0] < temp:
        value = [temp, actionList[index]]
    # depth -= 1
      index += 1


    return value

  def MIN_VALUE_EXP(self, gameState, depth):
    if gameState.isWin() or gameState.isLose():
      return self.evaluationFunction(gameState)
    value = 0
    # ghostAction = []
    ghostSuccessor = []
    ghostSuccessor.append(gameState)

    ghost_num = gameState.getNumAgents() - 1
    ghost_max = []

    for ghost_index in range(1, ghost_num + 1):
      temp = []
      for gameState in ghostSuccessor:
        if gameState.isLose() or gameState.isWin():
          ghost_max.append(gameState)
        else:
          ghostAction = [ghost_action for ghost_action in gameState.getLegalActions(ghost_index)]
          # for ghost_action in gameState.getLegalActions(ghost_index):
          #   ghostAction.append(ghost_action)
          temp = temp + [gameState.generateSuccessor(ghost_index, ghost_action) for ghost_action in ghostAction]
      ghostSuccessor = temp[:]


    ghost_max = ghost_max + ghostSuccessor[:]

    for gameState in ghost_max:
      temp_value = self.MAX_VALUE_EXP(gameState, depth)
      value = value + temp_value[0]
    value = value / len(ghost_max)
    return value

  def getAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    "*** YOUR CODE HERE ***"
    value = self.MAX_VALUE_EXP(gameState, self.depth)
    return value[1]
    # util.raiseNotDefined()

def minDistToOther(position_pac, foodList):
  if len(foodList) == 0:
    return 0.0
  sorted(foodList, key = lambda food_dist: manhattanDistance(food_dist, position_pac))

  position_food = foodList[0]
  distance_food = manhattanDistance(position_pac, position_food)
  foodList.remove(position_food)

  while len(foodList) > 0:
    sorted(foodList, key = lambda food_dist: manhattanDistance(food_dist, position_food))
    distance_food = distance_food + manhattanDistance(position_food, foodList[0])
    position_food = foodList[0]
    foodList.remove(position_food)

  return distance_food


def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
  """
  "*** YOUR CODE HERE ***"
  
  ghostStates = [gameState for gameState in currentGameState.getGhostStates()]
  ghostPositionList = [ gameState.getPosition() for gameState in ghostStates]
  currentFood = currentGameState.getFood()
  position_pac = currentGameState.getPacmanPosition()
  newScaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
  foodList = currentFood.asList()


  distToFood = 0.1
  foodWeight = 20
  ghostWeight = -20
  currentScore = currentGameState.getScore()
  powerWeight = 0
  food_threshold = 4
  distToGhost = 0.9*minDistToOther(position_pac, ghostPositionList)
  nearestFood = []
  
  for food in foodList:
     nearestFood.append(manhattanDistance(food, position_pac))
  sorted(nearestFood) 

  if len(foodList) < food_threshold:
    food_threshold = len(foodList)


  for index in range(food_threshold):
    if newScaredTimes[0] != 0:
      distToFood = distToFood + 1.2*nearestFood[index]
    else:
      distToFood = distToFood + 0.8*nearestFood[index]

  

  if newScaredTimes[0] != 0:
      powerWeight = float('Inf')
      ghostWeight = 0

  return currentScore + (100 / distToFood) * foodWeight + distToGhost * ghostWeight + powerWeight
