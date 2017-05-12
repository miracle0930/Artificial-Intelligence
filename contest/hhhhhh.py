# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util, operator
from util import nearestPoint
from game import Directions
import game


class Node:
  def __init__(self, state, action, cost, parent):
    self.state = state
    self.action = action
    self.cost = cost
    self.parent = parent

  def getPath(self):
    if self.parent == None: return []
    path = self.parent.getPath()
    return path + [self.action] 

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'TopAgent', second = 'BottomAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
  def __init__(self, gameState):
    CaptureAgent.__init__(self, gameState)
    self.mostlikely = [None]*4


  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on). 
    
    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    ''' 
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py. 
    '''
    CaptureAgent.registerInitialState(self, gameState)

    ''' 
    Your initialization code goes here, if you need any.
    '''
    if self.red:
      CaptureAgent.registerTeam(self, gameState.getRedTeamIndices())
    else:
      CaptureAgent.registerTeam(self, gameState.getBlueTeamIndices())



    self.legalPositions = []
    for p in gameState.getWalls().asList(False):
      if p[1] > 1: 
        self.legalPositions.append(p)


    self.x, self.y = gameState.getWalls().asList()[-1] 
    self.walls = list(gameState.getWalls())

    # self.chokes = []

    # if self.red:
    #   xAdd = -3
    # else:
    #   xAdd = 4

    # for i in range(self.y): 
    #   if not self.walls[self.x/2 + xAdd][i]:
    #     self.chokes.append(((self.x/2 + xAdd), i))  

    # if self.index == max(gameState.getRedTeamIndices()) or self.index == max(gameState.getBlueTeamIndices()):
    #   x, y = self.chokes[3*len(self.chokes)/4]

    # else:
    #   x, y = self.chokes[1*len(self.chokes)/4]
    # self.goalTile = (x, y)


    global beliefs
    beliefs = [util.Counter()] * gameState.getNumAgents() 
    
    # All beliefs begin with the agent at its inital position
    for i, val in enumerate(beliefs):
      if i in self.getOpponents(gameState): 
        beliefs[i][gameState.getInitialAgentPosition(i)] = 1.0

    self.goToCenter(gameState)

  def getEnemyPos(self, gameState):
    enemyPos = []
    for enemy in self.getOpponents(gameState):
      pos = gameState.getAgentPosition(enemy)
      if not pos == None:
        enemyPos.append((enemy, pos))
    return enemyPos


  def enemyDist(self, gameState):
    pos = self.getEnemyPos(gameState)
    minDist = 0
    if not len(pos) == 0:
      minDist = float('inf')
      self_position = gameState.getAgentPosition(self.index)
      for enemy, enemy_position in pos:
        dist = self.getMazeDistance(enemy_position, self_position)
        if dist < minDist:
          minDist = dist
    return minDist

##--------------------------------------------------
  def inEnemyTerritory(self, gameState):
    return gameState.getAgentState(self.index).isPacman

  def getMyPos(self, gameState):
    return gameState.getAgentState(self.index).getPosition()

  def partnerDist(self, gameState):
    distanceToPartner = float('inf')
    agent_1 = self.agentsOnTeam[0]
    agent_2 = self.agentsOnTeam[1]
    if self.index == 0:
      agent_1_pos = gameState.getMyPos(agent_1)
      agent_2_pos = gameState.getAgentState(agent_2).getPosition()
    else:
      agent_1_pos = gameState.getMyPos(agent_2)
      agent_2_pos = gameState.getAgentState(agent_1).getPosition()
    distanceToPartner = self.getMazeDistance(agent_1_pos, agent_2_pos)
    if distanceToPartner == 0:
      distanceToPartner = 0.5
    return distanceToPartner

  def getDist(self, p):
    posActions = [(p[0] - 1, p[1]), (p[0] + 1, p[1]), (p[0], p[1] - 1), (p[0], p[1] + 1), (p[0], p[1])]
    actions = []
    for act in posActions:
      if act in self.legalPositions:
        actions.append(act)
        
    dist = util.Counter()
    for act in actions:
      dist[act] = 1
    return dist

  def side(self, gameState):
    width = gameState.data.layout.width
    height = gameState.data.layout.height
    position = gameState.getAgentPosition(self.index)
    if self.red:
      if position[0] < width / 2: return 1
      else:  return 0
    else:
      if position[0] > width / 2 - 1: return 1
      else: return 0 

  def elapseTime(self, gameState):
    newBeliefs = util.Counter()
    for agent, belief in enumerate(beliefs):
      if agent in self.getOpponents(gameState):
        pos = gameState.getAgentPosition(agent)
        if pos != None:
          newBeliefs[pos] = 1.0
        else:
          for p in belief:
            if p in self.legalPositions and belief[p] > 0: 
              newPosDist = self.getDist(p)
              for x, y in newPosDist:
                newBeliefs[x, y] += belief[p] * newPosDist[x, y] 
          if len(newBeliefs) == 0:
            oldState = self.getPreviousObservation()
            if oldState != None and oldState.getAgentPosition(agent) != None:
              newBeliefs[oldState.getInitialAgentPosition(agent)] = 1.0
            else:
              for p in self.legalPositions: newBeliefs[p] = 1.0
        newBeliefs.normalize()
        beliefs[agent] = newBeliefs

  def observe(self, agent, noisyDistance, gameState):
    myPos = gameState.getAgentPosition(self.index)
    allPossible = util.Counter()
    for oldPos in self.legalPositions:
      trurDistance = util.manhattanDistance(oldPos, myPos)
      allPossible[oldPos] += gameState.getDistanceProb(trurDistance, noisyDistance)
    for p in self.legalPositions:
      beliefs[agent][p] *= allPossible[p]
    allPossible.normalize()
    self.beliefs = allPossible

  def aStarSearch(self, problem):
    startNode = Node(problem.getStartState(), None, 0, None)
    current_state = problem.getStartState()
    state_pq = util.PriorityQueue()
    state_pq.push(startNode, 0)
    isVisited = set()
    frontier = set()
    action = []
    new_action = {current_state:[]}

    while True:
      if state_pq.isEmpty():
        return action
      current_state = state_pq.pop()
      if problem.isGoalState(current_state):
        return new_action[current_state]
      isVisited.add(current_state)
      for child_node in problem.getSuccessors(current_state):
        if not (child_node[0] in isVisited or child_node[0] in frontier):
          action = list(new_action[current_state])
          action.append(child_node[1])
          new_action[child_node[0]] = action
          state_pq.push(child_node[0],problem.getCostOfActions(action)+heuristic(child_node[0], problem))
          frontier.add(child_node[0])
        if child_node[0] in frontier:
          action = list(new_action[current_state])
          action.append(child_node[1])
          if problem.getCostOfActions(new_action[child_node[0]]) + heuristic(child_node[0], problem) > problem.getCostOfActions(action) + heuristic(child_node[0], problem):
            state_pq.push(child_node[0], problem.getCostOfActions(action) + heuristic(child_node[0], problem))
            new_action[child_node[0]] = action               
    return []

  def heuristic(self, state, problem):

    position, foodGrid = state
    walls = problem.walls
    food_list = foodGrid.asList()
    food_list.append(position)
    min_food_dist = float('inf')
    total_food_dist = 0
    for food_item in food_list:
      min_food_dist = min(food_manhattan_dist(food_item, state[0], walls), min_food_dist)
    total_food_dist = total_food_dist + min_food_dist
    min_food_dist = 0
    for fromfood in food_list:
      for tofood in food_list:
        if fromfood == tofood:
          continue
        else:
          min_food_dist = max(food_manhattan_dist(fromfood, tofood, walls), min_food_dist)
    if len(food_list) == 0:
      return 0
    else:
      return min_food_dist + total_food_dist

    def food_manhattan_dist(xy1, xy2, walls):
      wallnum1 = 0
      wallnum2 = 0
      wallnum3 = 0
      wallnum4 = 0
      largex = max(xy1[0], xy2[0])
      smallx = min(xy1[0], xy2[0])
      largey = max(xy1[1], xy2[1])
      smally = min(xy1[1], xy2[1])

      for wallx in range (smallx, largex):
        if walls[wallx][smally] == True:
          wallnum1 += 1
        if walls[wallx][largey] == True:
          wallnum3 += 1
      for wally in range (smally, largey):
        if walls[largex][wally] == True:
          wallnum2 += 1
        if walls[smallx][wally] == True:
          wallnum4 += 1

      totalwall1 = wallnum1 + wallnum2
      totalwall2 = wallnum3 + wallnum4
      if (totalwall1 == 0 or totalwall2 == 0):
        return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])
      else:
        return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1]) + 2 * min(totalwall1, totalwall2)
  
  def chooseAction(self, gameState):

    actions = gameState.getLegalActions(self.index)
    opponents = self.getOpponents(gameState)
    noisyD = gameState.getAgentDistances() 
    myPos = gameState.getAgentPosition(self.index)
    
    # for agent in opponents:
    #     self.observe(agent, noisyD[agent], gameState) 
   
    # self.locations = [self.chokes[len(self.chokes)/2]] * gameState.getNumAgents() 
    # for i, belief in enumerate(beliefs):
    #     maxLoc = 0
    #     checkForAllEq = 0
    #     for val in beliefs[i]:
    #         if belief[val] == maxLoc and maxLoc > 0: 
    #             checkForAllEq += 1 
    #         elif belief[val] > maxLoc:
    #             maxLoc = belief[val]
    #             self.locations[i] = val
    #     if checkForAllEq > 5:
    #         self.locations[i] = self.goalTile
   
    # for agent in opponents:
    #     beliefs[agent].normalize()   
    #     self.mostlikely[agent] = max(beliefs[agent].iteritems(), key=operator.itemgetter(1))[0]
    
    # self.elapseTime(gameState)
    agentPos = gameState.getAgentPosition(self.index)


    actionList = ['start', 'attack', 'defend']
    evaluateType = actionList[1]

    if self.atCenter == False:
      evaluateType = actionList[0]

    if agentPos == self.center and self.atCenter == False:
      self.atCenter = True
      evaluateType = actionList[1]

    enemyPos = self.getEnemyPos(gameState)

    if not len(enemyPos) == 0:
      for enemy, pos in enemyPos:
        if self.getMazeDistance(agentPos, pos) < 4 and not self.inEnemyTerritory(gameState):
          evaluateType = actionList[2]
          break

    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a, evaluateType) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if not pos == nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor


  def evaluate(self, gameState, action, evaluateType):
    
    if evaluateType == 'attack':
      features = self.getFeaturesAttack(gameState, action)
      weights = self.getWeightsAttack(gameState, action)

    elif evaluateType == 'defend':
      features = self.getFeaturesDefend(gameState, action)
      weights = self.getWeightsDefend(gameState, action)

    elif evaluateType == 'start':
      features = self.getFeaturesStart(gameState, action)
      weights = self.getWeightsStart(gameState, action)

    return features * weights

  
  def getFeaturesAttack(self, gameState, action):

    width = gameState.data.layout.width
    height = gameState.data.layout.height

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['score_successor'] = self.getScore(successor)


    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: 
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['score_food'] = minDistance
      # features['get_food'] = len(foodList)*(min([self.distancer.getDistance(myPos,p) for p in [(width/2,i) for i in range(1,height) if not gameState.hasWall(width/2,i)]]))*self.side(gameState)

    # features['giveup_food'] = len(foodList) * (self.side(gameState))
    capsules = self.getCapsules(successor)
    if not len(capsules) == 0:
      minCapsuleDist = min([self.getMazeDistance(myPos, capsule) for capsule in capsules])
    else:
      minCapsuleDist = 0.01
    features['score_capsule'] =  1.0 / minCapsuleDist



    distEnemy = self.enemyDist(successor)
    if (distEnemy <= 2):
      if distEnemy == 0: distEnemy = 0.1
      features['score_enemy'] = 4/distEnemy
    elif (distEnemy <= 4):
      features['score_enemy'] = 1
    else:
      features['score_enemy'] = 0 


    if action == Directions.STOP: 
      features['score_stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: 
      features['score_reverse'] = 1

    return features

  def getFeaturesDefend(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    
    features['enemy_num'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['enemy_distance'] = min(dists)

    distEnemy = self.enemyDist(successor)
    if (distEnemy <= 8):
      features['danger'] = 1
      if (distEnemy <= 1):
        features['danger'] = -1
    else:
      features['danger'] = 0 


    if action == Directions.STOP: features['score_stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['score_reverse'] = 1


    return features

  def getFeaturesStart(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    dist = self.getMazeDistance(myPos, self.center)

    features['score_center'] = dist
    if myPos == self.center:
      features['score_atcenter'] = 1
    return features


  def getWeightsAttack(self, gameState, action):
    return {'score_successor': 100, 'score_enemy': -400, 'score_food': -1, 
            'score_stop': -2000, 'score_reverse': -20, 'score_capsule': 3,
            'get_food': 100, 'giveup_food': -1}
  def getWeightsDefend(self, gameState, action):
    return {'enemy_num': -1000, 'enemy_distance': -50, 'score_stop': -2000, 'score_reverse': -20, 'danger': 3000}
  def getWeightsStart(self, gameState, action):
    return {'score_center': -1, 'score_atcenter': 1000}


class TopAgent(ReflexCaptureAgent):

  def goToCenter(self, gameState):
    locations = []
    self.atCenter = False
    x = gameState.getWalls().width / 2
    y = gameState.getWalls().height / 2
    if self.red:
      x = x - 1
    self.center = (x, y)
    maxHeight = gameState.getWalls().height

    for i in xrange(maxHeight - y):
      if not gameState.hasWall(x, y):
        locations.append((x, y))
      y = y + 1

    myPos = gameState.getAgentState(self.index).getPosition()
    minDist = float('inf')
    minPos = None

    for location in locations:
      dist = self.getMazeDistance(myPos, location)
      if dist <= minDist:
        minDist = dist
        minPos = location
    
    self.center = minPos

class BottomAgent(ReflexCaptureAgent):

  def goToCenter(self, gameState):
    locations = []
    self.atCenter = False
    x = gameState.getWalls().width / 2
    y = gameState.getWalls().height / 2
    if self.red:
      x = x - 1
    self.center = (x, y)
    
    for i in xrange(y):
      if not gameState.hasWall(x, y):
        locations.append((x, y))
      y = y - 1

    myPos = gameState.getAgentState(self.index).getPosition()
    minDist = float('inf')
    minPos = None

    for location in locations:
      dist = self.getMazeDistance(myPos, location)
      if dist <= minDist:
        minDist = dist
        minPos = location
    
    self.center = minPos  