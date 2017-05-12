# search.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
In search.py, you will implement generic search algorithms which are called
by Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other
    maze, the sequence of moves will be incorrect, so only use this for tinyMaze
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s,s,w,s,w,w,s,w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first
    [2nd Edition: p 75, 3rd Edition: p 87]

    Your search algorithm needs to return a list of actions that reaches
    the goal.  Make sure to implement a graph search algorithm
    [2nd Edition: Fig. 3.18, 3rd Edition: Fig 3.7].

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"

    state_stack = util.Stack()
    current_state = problem.getStartState()
    state_stack.push(current_state)
    isVisited = set()
    action = []
    new_action = {current_state:[]}
    while True:
        if state_stack.isEmpty():
            return action
        current_state = state_stack.pop()
        if problem.isGoalState(current_state):
            return new_action[current_state]
        else:
            if not current_state in isVisited:
                isVisited.add(current_state)
                for child_node in problem.getSuccessors(current_state):
                    state_stack.push(child_node[0])
                    action = list(new_action[current_state])
                    action.append(child_node[1])
                    new_action[child_node[0]] = action

    return []


def breadthFirstSearch(problem):
    """
    Search the shallowest nodes in the search tree first.
    [2nd Edition: p 73, 3rd Edition: p 82]
    """
    "*** YOUR CODE HERE ***"
    state_queue = util.Queue()
    current_state = problem.getStartState()
    state_queue.push(current_state)
    isVisited = set()
    action = []
    new_action = {current_state:[]}
    while True:
        if state_queue.isEmpty():
            return action
        current_state = state_queue.pop()
        if problem.isGoalState(current_state):
            return new_action[current_state]
        else:
            if not current_state in isVisited:
                isVisited.add(current_state)
                for child_node in problem.getSuccessors(current_state):
                    state_queue.push(child_node[0])
                    action = list(new_action[current_state])
                    action.append(child_node[1])
                    new_action[child_node[0]] = action

    return []

def uniformCostSearch(problem):
    "Search the node of least total cost first. "
    "*** YOUR CODE HERE ***"
    state_pq = util.PriorityQueue()
    current_state = problem.getStartState()
    state_pq.push(current_state, 0)
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
                state_pq.push(child_node[0],problem.getCostOfActions(action))
                frontier.add(child_node[0])
            if child_node[0] in frontier:
                action = list(new_action[current_state])
                action.append(child_node[1])
                if problem.getCostOfActions(new_action[child_node[0]]) > problem.getCostOfActions(action):
                    state_pq.push(child_node[0], problem.getCostOfActions(action))
                    new_action[child_node[0]] = action               
    return []

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    "Search the node that has the lowest combined cost and heuristic first."
    "*** YOUR CODE HERE ***"
    state_pq = util.PriorityQueue()
    current_state = problem.getStartState()
    state_pq.push(current_state, 0)
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

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
