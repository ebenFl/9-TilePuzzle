import pygame
import random
import copy

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

        self.goalState = [[1,2,3],[4,5,6],[7,8,0]]
        self.prev = None
        self.g = 0
        self.f = 0

    def set_state(self,s):
        self.state = s

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

    # generates all the possible gamesteps 1 move away
    # from the current game grid and returns them in an array
    def get_possible_states(self):
        moves = ['u','l','r','d']
        newStates = []
        for move in moves:
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
                    copyState = copy.deepcopy(self.get_state())
                    num = copyState[slideLoc[0]][slideLoc[1]]
                    copyState[self.emptyLoc[0]][self.emptyLoc[1]] = num
                    copyState[slideLoc[0]][slideLoc[1]] = 0
                    newStates.append(grid(copyState))
        return newStates

    #heuristic function for a star search
    def h(self):
        count = 0 # count of numbers not in right location
        for i in range(self.width):
            for j in range(self.width):
                if self.state[i][j] != self.goalState[i][j]:
                    count += 1
        return count

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
                    print(len(gameGrid.get_possible_states()))
                    print(gameGrid.h())
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
