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
import random, time, util
from game import Directions
import game
import distanceCalculator

#################
# Team creation #
#################

def createTeam(indexes, num, isRed, names=['MixAgent','MixAgent']):
    """
    This function should return a list of agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.    isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments, which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(name)(index) for name, index in zip(names, indexes)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

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
        
        
        """
    	you can have your own distanceCalculator. (you can even have multiple distanceCalculators, if you need.)
    	reference the registerInitialState function in captureAgents.py and baselineTeam.py to understand more about the distanceCalculator. 
    	"""

        """
        Each agent has two indexes, one for pacman and the other for ghost.
        self.index[0]: pacman
        self.index[1]: ghost
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


    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index[0])

        '''
        You should change this in your own agent.
        '''
        
        return random.choice(actions)
    
    
		
class ReflexCaptureAgent(CaptureAgent):
    """
    A base class for reflex agents that chooses score-maximizing actions
    """
 
    def registerInitialState(self, gameState):
        """
        Each agent has two indexes, one for pacman and the other for ghost.
        self.index[0]: pacman
        self.index[1]: ghost
        """
        CaptureAgent.registerInitialState(self, gameState)   
        
        """
        overwrite distancer
        only calculate distance positions which are reachable for self team
        """
        self.red = gameState.isOnRedTeam(self.index[0])#0 or 1 doesn't mater
        wallChar = 'r' if self.red else 'b'
        
        layout = gameState.data.layout.deepCopy()
        walls = layout.walls
        for x in range(layout.width):
            for y in range(layout.height):
                if walls[x][y] is wallChar:
                    walls[x][y] = False
        
        self.distancer = distanceCalculator.Distancer(layout)
        

        # comment this out to forgo maze distance computation and use manhattan distances
        self.distancer.getMazeDistances()
        
        
        self.start = [gameState.getAgentPosition(index) for index in self.index]
        #print('mii')


    def chooseAction(self, gameState):
        if(isinstance(self, MixAgent)):
            return self.chooseActionImpl(gameState, self.index[0])#pacman
        else:
            return self.chooseActionImpl(gameState, self.index[1])#ghost
    def chooseActionImpl(self, gameState, index):
        """
        Picks among the actions with the highest Q(s,a).
        """
#         isPacman = gameState.getAgentState(index).isPacman
        
        actions = gameState.getLegalActions(index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
        act =  random.choice(bestActions)
        return act
    def getSuccessor(self, gameState, action, index):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        return gameState.generateSuccessor(index, action)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)

        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.    They can be either
        a counter or a dictionary.
        """
        return {'successorScore': 1.0}


class MixAgent(ReflexCaptureAgent):
    def getFeatures(self, gameState, action):
        #pacman
        features = util.Counter()
        successor = self.getSuccessor(gameState, action, self.index[0])
        #successor = self.getSuccessor(successor, action, self.index[1])
        foodList = self.getFood(successor).asListNot()
        features['successorScore'] = -len(foodList)#self.getScore(successor)

        #food
        myPos = successor.getAgentState(self.index[0]).getPosition()
        if len(foodList) > 0:
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
        
        #capsule
        capsulesList = self.getCapsules(successor)
        features['capsule'] = -len(capsulesList)
        
        #ghost
        myState = successor.getAgentState(self.index[1])
        myPos = myState.getPosition()
        initialPos = gameState.getInitialAgentPosition(self.index[1])
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = []
		
        #enemy
        for enemy in enemies:
            if enemy.isPacman and self.getMazeDistance(initialPos, enemy.getPosition())< 25:
                invaders.append(enemy)
        features['numInvaders'] = len(invaders)
		
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
        else:
            features['invaderDistance'] = 0

        #score
        if action == Directions.STOP: features['stop'] = 1
        score = (successor.getScore()-gameState.getScore())
        if(not self.red):
            score=-score;
        features['score'] = score
        return features
		
    def getWeights(self, gameState, action):
        return  {'successorScore': 100, 'distanceToFood': -5, 'capsule':150, 'numInvaders': -100, 'invaderDistance': -5, 'stop': -5, 'score':200}
