import pygame
import random
import copy
import heapq
import numpy as np

WIDTH = 800

WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Maze Runner")

#Initializing the font for game text
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 30)

#RGB Colors

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE= (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# HELPER FUNCTIONS FOR ASTAR

def path(previous, s):
    '''
    `previous` is a dictionary chaining together the predecessor state that led to each state
    `s` will be None for the initial state
    otherwise, start from the last state `s` and recursively trace `previous` back to the initial state,
    constructing a list of states visited as we go
    '''
    if s is None:
        return []
    else:
        return path(previous, previous[s])+[s]

def pathcost(path, step_costs):
    '''
    add up the step costs along a path, which is assumed to be a list output from the `path` function above
    '''
    cost = 0
    for s in range(len(path)-1):
        cost += step_costs[path[s]][path[s+1]]
    return cost

# QUEUE FOR ASTAR

class Frontier_PQ:
    ''' frontier class for uniform search, ordered by path cost '''

    def __init__(self, start, cost):
        self.states = {}
        self.q = []
        self.add(start, cost)

    def add(self, state, cost):
        ''' push the new state and cost to get there onto the heap'''
        heapq.heappush(self.q, (cost, state))
        self.states[state] = cost

    def pop(self):
        (cost, state) = heapq.heappop(self.q)  # get cost of getting to explored state
        self.states.pop(state)    # and remove from frontier
        return (cost, state)

    def replace(self, state, cost):
        ''' found a cheaper route to `state`, replacing old cost with new `cost` '''
        self.states[state] = cost
        for i, (oldcost, oldstate) in enumerate(self.q):
            if oldstate==state and oldcost > cost:
                self.q[i] = (cost, state)
                heapq._siftdown(self.q, 0, i) # now i is posisbly out of order; restore
        return

    def contains(self,state):
        return state in self.states.keys()

    def view(self):
        print(self.q)

    def length(self):
        return len(self.q)

# HEURSITIC FOR ASTAR
# we will use the manhatten distance heurisic
def h(state):
    dist = 0
    gLocs = {0 : (0,0), 1 : (0,1), 2 : (0,2),
            3 : (1,0), 4 : (1,1), 5 : (1,2),
            6 : (2,0), 7 : (2,1), 8 : (2,2)}
    for i in range(3):
        for j in range(3):
            x = gLocs[state[i][j]]
            dist += abs(x[0] - i) + abs(x[1] - j)
    return dist

# HELPER FUNCTION TO GENERATE ALL POSSIBLE STATES FROM A GIVEN STATE
def adjacent_states(state):
    '''what are all the successors of this state? depends on location of the 0 (blank tile)'''
    adjacent = []
    loc0 = [int(np.where(state==0)[i]) for i in range(2)]
    if loc0[0] > 0:
        # If row of 0 is > 0, then we can move 0 up
        swap = np.copy(state)
        newloc = [loc0[0]-1, loc0[1]]
        swap[loc0[0], loc0[1]] = state[newloc[0], newloc[1]]
        swap[newloc[0], newloc[1]] = 0
        adjacent.append(swap)
    if loc0[0] < (state.shape[0]-1):
        # If row of 0 is not bottom, then can move 0 down
        swap = np.copy(state)
        newloc = [loc0[0]+1, loc0[1]]
        swap[loc0[0], loc0[1]] = state[newloc[0], newloc[1]]
        swap[newloc[0], newloc[1]] = 0
        adjacent.append(swap)
    if loc0[1] > 0:
        # If column of 0 is > 0, then we can move 0 left
        swap = np.copy(state)
        newloc = [loc0[0], loc0[1]-1]
        swap[loc0[0], loc0[1]] = state[newloc[0], newloc[1]]
        swap[newloc[0], newloc[1]] = 0
        adjacent.append(swap)
    if loc0[1] < (state.shape[1]-1):
        # If column of 0 is not far-right, then we can move 0 right
        swap = np.copy(state)
        newloc = [loc0[0], loc0[1]+1]
        swap[loc0[0], loc0[1]] = state[newloc[0], newloc[1]]
        swap[newloc[0], newloc[1]] = 0
        adjacent.append(swap)
    return adjacent


# This function draws the current state of the game onto the screen
# It takes in the pygame window (win)
# The width of the window in pixels (width)
# And a grid object that represents the puzzle

def draw(win,width,grid):
    win.fill(WHITE)
    gridWidth = grid.get_width()
    gap = width // gridWidth # gap between the lines that draw the gird

    # Draw the lines for the 3x3 grid

    for i in range(gridWidth):
        pygame.draw.line(win,GREY,(0,i * gap), (width,i * gap))

    for j in range(gridWidth):
        pygame.draw.line(win,GREY,(j * gap,0), (j *gap,width ))

    # Fill the grid with the current state of the game

    state = grid.get_state()
    for i in range(1,gridWidth + 1):
        y = (gap * i) - (gap // 2)
        for j in range(1,gridWidth + 1):
            x = (gap * j) - (gap // 2)
            squareNum = str(state[i - 1][j - 1])
            if squareNum != "0":
                text = myfont.render(squareNum,WHITE,BLACK)
                WIN.blit(text,(x,y))
    pygame.display.update()

class grid():
    def __init__(self,s = [[0,1,2],[3,4,5],[6,7,8]]):
        self.width = 3
        self.startState = s
        self.state = s

        # find and store the location of the emptyslot
        for i in range(self.width):
            for j in range(self.width):
                if self.state[i][j] == 0:
                    self.emptyLoc = (i,j)

        self.goalState = [[0,1,2],[3,4,5],[6,7,8]]

    def set_state(self,s):
        self.state = s

        # find and store the location of the emptyslot
        for i in range(self.width):
            for j in range(self.width):
                if self.state[i][j] == 0:
                    self.emptyLoc = (i,j)

    def get_state(self):
        return self.state

    def get_width(self):
        return self.width

    def solved(self):
        return self.state == self.goalState

    def get_empty_loc(self):
        return self.emptyLoc

    def in_grid(self,x,y):
        if x < 0 or x >= self.width:
            return False
        elif y < 0 or y >= self.width:
            return False
        return True

    # reset game to start state
    def reset(self):
        self.state = [self.startState[:3],self.startState[3:6],self.startState[6:]]
        for i in range(self.width):
            for j in range(self.width):
                if self.state[i][j] == 0:
                    self.emptyLoc = (i,j)

    # generate new start game state
    def generate_state(self):
        tileNumbers = [0,1,2,3,4,5,6,7,8]

        validPuzzle = False

        while not validPuzzle:
            # generate a random puzzle state
            randomized = random.sample(tileNumbers,9)

            # check its validity
            invCount = 0
            for i in range(len(randomized)):
                for j in range(i + 1, len(randomized)):
                    if randomized[i] != 0 and randomized[j] != 0:
                        if randomized[i] > randomized[j]:
                            invCount += 1

            if (invCount % 2):
                pass
            else:
                validPuzzle = True
                self.startState = randomized
                self.state = [randomized[:3],randomized[3:6],randomized[6:]]
                for i in range(self.width):
                    for j in range(self.width):
                        if self.state[i][j] == 0:
                            self.emptyLoc = (i,j)



    def set_empty_loc(self,x,y):
        self.emptyLoc = (x,y)


    # handles the execution of sliding a tile
    # 'u' slide piece up into empty spot
    # 'l' slide piece left into empty spot
    # 'r' slide piece right into empty spot
    # 'd' slide piece down into empty spot
    def slide(self, move):
        slideLoc = None
        if move == 'u':
            slideLoc = (self.emptyLoc[0] - 1,self.emptyLoc[1])
        elif move == 'l':
            slideLoc = (self.emptyLoc[0],self.emptyLoc[1] + 1)
        elif move == 'r':
            slideLoc = (self.emptyLoc[0],self.emptyLoc[1] - 1)
        elif move == 'd':
            slideLoc = (self.emptyLoc[0] + 1,self.emptyLoc[1])
        if self.in_grid(slideLoc[0],slideLoc[1]):
                num = self.state[slideLoc[0]][slideLoc[1]]
                self.state[self.emptyLoc[0]][self.emptyLoc[1]] = num
                self.state[slideLoc[0]][slideLoc[1]] = 0
                self.set_empty_loc(slideLoc[0],slideLoc[1])


    # solve the 9 tile puzzle and play its animation out
    def solve(self):
        sTuple = tuple(map(tuple, self.state))
        gTuple = tuple(map(tuple, self.goalState))
        q = Frontier_PQ(sTuple,0 + h(self.state))
        pred = {sTuple:None}
        gScore = {sTuple:0}
        fScores = {sTuple:h(self.state)}
        closed = []
        while(q.length()):
            curr = q.pop()
            currState = curr[1]
            closed.append(currState)
            if currState == gTuple:
                solPath = path(pred,gTuple)
                pathCost = len(solPath) - 1
                return (solPath,pathCost)
            for child in adjacent_states(np.asarray(currState)):
                cTuple = tuple(map(tuple, child))
                if cTuple in closed:
                    continue
                elif q.contains(cTuple):
                    tempG = gScore[currState] + 1
                    fScore = tempG + h(child)
                    if(fScore < fScores[cTuple]):
                        q.replace(cTuple,fScore)
                        fScores[cTuple] = fScore
                        pred[cTuple] = currState
                        gScore[cTuple] = tempG
                else:
                    pred[cTuple] = currState
                    gScore[cTuple] = gScore[currState] + 1
                    fScore = gScore[currState] + h(child)
                    fScores[cTuple] = fScore
                    q.add(cTuple,fScore)

def main():
    active = True
    solved = False
    gameGrid = grid()
    gameGrid.generate_state()
    while active:
        draw(WIN,WIDTH,gameGrid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # user presses x button in the upper right corner
                active = False
            if event.type == pygame.KEYDOWN:
                if not solved:
                    if event.key == pygame.K_UP:
                        gameGrid.slide('d')
                    if event.key == pygame.K_DOWN:
                        gameGrid.slide('u')
                    if event.key == pygame.K_LEFT:
                        gameGrid.slide('l')
                    if event.key == pygame.K_RIGHT:
                        gameGrid.slide('r')
                    if event.key == pygame.K_s:
                        solution = gameGrid.solve()
                        for s in solution[0]:
                            gameGrid.set_state(s)
                            draw(WIN,WIDTH,gameGrid)
                            pygame.time.wait(500)
                        solved = True
                if event.key == pygame.K_r: # reset current state
                    gameGrid.reset()
                    solved = False
                if event.key == pygame.K_n: # generate new state
                    gameGrid.generate_state()
                    solved = False

            if gameGrid.solved():
                solved = True

    pygame.quit()

main()
