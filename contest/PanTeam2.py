# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for 
# educational purposes provided that (1) you do not distribute or publish 
# solutions, (2) you retain this notice, and (3) you provide clear 
# attribution to UC Berkeley, including a link to 
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero 
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and 
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
from game import Actions
from util import PriorityQueue
import game
import capture
import traceback
import sys
from baselineTeam import DefensiveReflexAgent

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AwesomeAgent', second = 'AwesomeAgent'):
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

class DummyAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    return random.choice(actions)

class AwesomeAgent(CaptureAgent):
  
  trackingTime = True
  powerful = 0

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.food = 0
    self.weight = {}
    self.weight['nearestFood'] = 2.0
    self.weight['opponent'] = 1.0
    self.weight['score'] = 800.0
    self.weight['ally'] = -0.4
    self.weight['nearestPellet'] = 2.0
    self.weight['immediateOpponent'] = -100000.0
    self.weight['atePellet'] = 1000.0
    self.weight['deadend'] = -100.0
    # self.weight['hasFood'] = -0.01
    self.weight['dropFood'] = 1000.0
    self.weight['isStop'] = -100
    self.weight['eatenFood'] = 100
    self.weight['eatGhost'] = 1000000
    self.weight['goBack'] = 1000000000

    

    if self.trackingTime:
      self.trackingTime = True
      AwesomeAgent.trackingTime = False


    # CaptureAgent.registerInitialState(self, gameState)
    opponentIndexes = self.getOpponents(gameState)
    self.mod = {}
    for i in opponentIndexes:
      self.mod[i] = InferenceModule(self.index, i, gameState)
    if not gameState.isOnRedTeam(self.index):
      self.weight['score'] = (-1) * self.weight['score']

  def chooseAction(self, gameState):
    width = gameState.data.layout.width
    currentPosition = gameState.getAgentPosition(self.index)
    allPossible = []
    for act in gameState.getLegalActions(self.index):
      # state = gameState.generateSuccessor(self.index, act)
      allPossible.append((self.evaluate(gameState,act), act))
    action = max(allPossible)[1]


    foods = self.getFood(gameState).asList()
    if gameState.generateSuccessor(self.index,action).getAgentPosition(self.index) in foods:
      self.food += 1
    if self.trackingTime and AwesomeAgent.powerful > 0:
      AwesomeAgent.powerful -= 2
    if gameState.generateSuccessor(self.index,action).getAgentPosition(self.index) in self.getCapsules(gameState):
      AwesomeAgent.powerful = capture.SCARED_TIME * 2

    if self.index%2 == 1:
      if currentPosition[0] > width/2:
        self.food = 0
    else:
      if (currentPosition[0] < width/2) - 1:
        self.food = 0
    return action
      

  def evaluate(self, gameState, action):
    width = gameState.data.layout.width
    height = gameState.data.layout.height
    features = {}
    nextState = gameState.generateSuccessor(self.index, action)
    nextStatePosition = nextState.getAgentPosition(self.index)
    currentPosition = gameState.getAgentPosition(self.index)

    foodDist = []
    
    foods = self.getFood(gameState).asList()
    # print foods
    for pos in foods:
      foodDist.append(self.getMazeDistance(pos, nextStatePosition))
    features['nearestFood'] = 100.0/min(foodDist) if min(foodDist)!=0 else 100

    if nextStatePosition in foods:
      features['eatenFood'] = 1.0
    else:
      features['eatenFood'] = 0

    capsule = self.getCapsules(gameState)
    capDist = []
    if capsule:
      for pos in capsule:
        capDist.append(self.getMazeDistance(pos, currentPosition))
      features['nearestPellet'] = 1.0/min(capDist)
    else:
      features['nearestPellet'] = 100.0


    features['score'] = gameState.getScore()
    
    mostBeliefLocation = [self.mod[i].belief.argMax() for i in self.mod]
    shortestDistanceOppo = min(mostBeliefLocation,key=lambda x:self.getMazeDistance(nextStatePosition,x))

    if self.index%2==1:
      if shortestDistanceOppo[0]<width/(2):
        inDanger = -1.0
        eatGhost = 0.0
      else:
        inDanger = 1.0
        eatGhost = 1.0
    else:
      if shortestDistanceOppo[0]>width/2:
        inDanger = -1.0
        eatGhost = 0.0
      else:
        inDanger = 1.0
        eatGhost = 1.0

    if eatGhost == 1:
      if self.getMazeDistance(nextStatePosition, shortestDistanceOppo) == 0:
        features['eatGhost'] = 1.0
      else:
        features['eatGhost'] = 1/(self.getMazeDistance(nextStatePosition, shortestDistanceOppo))
    else:
      features['eatGhost'] = 0

    if self.powerful > 0:
      features['immediateOpponent'] = 0
      features['atePellet'] = 1.0
      opponentfeature = 1.0/(10.0*self.powerful)
    else:
      features['atePellet'] = 0
      opponentfeature = 1.0
      if (3>=util.manhattanDistance(shortestDistanceOppo, nextStatePosition)) and inDanger==-1:
        features['immediateOpponent']= 1
      else:
        features['immediateOpponent']= 0 



    minMazeDist = min([self.getMazeDistance(nextStatePosition,self.mod[i].belief.argMax()) for i in self.mod])
    features['opponent'] = opponentfeature * inDanger * 1.0/(1+minMazeDist)

    allyPos = nextState.getAgentPosition([i for i in self.getTeam(gameState) if i != self.index][0])
    if self.index%2==1:
      if allyPos[0]<width/(2):
        umm = -1.0
      else:
        umm = 1.0
    else:
      if allyPos[0]>width/2:
        umm = -1.0
      else:
        umm = 1.0
    features['ally'] = (1.0-umm) * (1.0/1+self.getMazeDistance(allyPos, nextStatePosition))

    if (len(nextState.getLegalActions(self.index)) <= 2) and (features['immediateOpponent']==1): 
      features['deadend'] = 1.0
    else:
      features['deadend'] = 0.0


    if self.index%2 == 1:
      if nextStatePosition[0] < width/2:
        uh = 1.0
      else:
        uh = 0
    else:
      if (nextStatePosition[0] > width/2) - 1:
        uh = 1.0
      else:
        uh = 0
    features['dropFood'] = self.food * (1-uh)

    threshold = []
    for i in range(1, height):
      if not gameState.hasWall(width/2, i):
        threshold.append((width/2,i))

    backtoSafely = []
    for pos in threshold:
      backtoSafely.append(self.getMazeDistance(pos, nextStatePosition))

    if uh == 1:
      if self.food > 0:
        features['goBack'] = 100.0/min(backtoSafely) if min(backtoSafely)!=0 else 100
      else:
        features['goBack'] = 0
    else:
      features['goBack'] = 0   


    # allFood = []
    # uhh = []
    # if not gameState.hasWall(width/2,i):
    #   uhh.append((width/2,i))
    # for p in uhh:
    #   allFood.append(self.distancer.getDistance(nextStatePosition,p))
    # features['hasFood'] = self.food * min(allFood) * uh

    for i in self.mod:
      self.mod[i].observe(gameState)
    if action == Directions.STOP:
      features['isStop'] = 1.0
    else:
      features['isStop'] = 0

    x=[]
    for i in features:
      x.append([i,features[i]])
    # print (action, sum(self.weight[i] * features[i] for i in self.weight), self.index, x)

    return sum(self.weight[i] * features[i] for i in self.weight)

  # def 

class InferenceModule:
  def __init__(self, index, opponentIndex, gameState):
    self.index = index
    self.opponentIndex = opponentIndex

    self.belief = util.Counter()
    for i in range(gameState.data.layout.width):
      for j in range(gameState.data.layout.height):
        if gameState.hasWall(i,j):
          self.belief[(i,j)] = 0
        else:
          self.belief[(i,j)] = 1.0
    self.belief.normalize()

  def initializeUniformaly(self, gameState):
    for i in range(gameState.data.layout.width):
      for j in range(gameState.data.layout.height):
        if gameState.hasWall(i,j):
          self.belief[(i,j)] = 0
        else:
          self.belief[(i,j)] = 1.0
    self.belief.normalize()

  def observe(self, gameState):
    opponentPos = gameState.getAgentPosition(self.opponentIndex)
    myPos = gameState.getAgentPosition(self.index)
 
    noisyDist = gameState.getAgentDistances()[self.opponentIndex]

    if opponentPos:
      for pos in self.belief:
        self.belief[pos] = 0
      self.belief[opponentPos] = 1.0
    else:
      for pos in self.belief:
        dist = util.manhattanDistance(myPos, pos)
        self.belief[pos] *= gameState.getDistanceProb(dist, noisyDist)
      
      self.belief.normalize()

    update = util.Counter()
    for pos in self.belief:
      if self.belief[pos] > 0:
        successors = []
        x,y = pos
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST, Directions.STOP]: 
          dx, dy = Actions.directionToVector(action)
          nextx, nexty = int(x + dx), int(y + dy)
          if (nextx, nexty) not in gameState.getWalls():
              successors.append((nextx,nexty))
        posProb = 1.0/len(successors)

        for poss in successors:
          update[poss] += posProb * self.belief[pos]

    for i in range(gameState.data.layout.width):
      for j in range(gameState.data.layout.height):
        if gameState.hasWall(i,j):
          update[(i,j)] = 0
    
    update.normalize()
    self.belief = update

    if self.belief.totalCount() <= 0:
      self.initializeUniformaly(gameState)