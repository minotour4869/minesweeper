import random, pygame, os

SPRITE_SIZE = (25, 25)

class Piece():
    def __init__(self, state=0):
        self.state = state
        self.revealed = False
        self.flagged = False
            
class Board():
    def __init__(self, size, mine, seed=None):
        self.size = size
        self.mine = mine
        self.curmine = 0
        self.seed = seed
        self.remainPiece = (size[0]*size[1]) - self.mine
        
        self.board = []
        for i in range(size[0]):
            tmp = []
            for j in range(size[1]):
                tmp.append(Piece())
            self.board.append(tmp)
            
    def printBoard(self):
        for i in self.board:
            for j in i:
                # if j.revealed: print(j.state, end=' ')
                # else: print('-', end=' ')
                print(j.state, end=' ')
            print()
    
    # def printReveal(self):
        # for i in self.board:
            # for j in i:
                # print(int(j.revealed), end=' ')
            # print()
            
    def genBoard(self):
        random.seed(self.seed)
        looped = 0
        while self.curmine != self.mine:
            state = -int(self.curmine > self.mine)
            target = self.curmine - self.mine
            for i in self.board:
                for j in i:
                    if j.state == state:
                        j.state = -random.randrange(2)
                        self.curmine -= (j.state - state)
                        target -= (j.state - state)
                        if looped > self.mine and not target: return 
            looped += 1
            # print(self.curmine)
            
    def mineCounter(self, pos):
        dirs = [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1]]
        tpiece = 0; tmine = 0
        for i in dirs:
            # print((pos[0] + i[0], pos[1] + i[1]))
            if pos[0] + i[0] >= 0 and pos[0] + i[0] < self.size[0] and pos[1] + i[1] >= 0 and pos[1] + i[1] < self.size[1]:
                tpiece += 1
                if self.board[pos[0] + i[0]][pos[1] + i[1]].state == -1: tmine += 1
        # print((tpiece, tmine))
        return (tpiece, tmine)
        
            
    def swapBomb(self, pos): 
        for i in range(pos[0]):
            for j in range(pos[1]):
                if self.board[i][j].state != -1:
                    self.board[i][j].state = -1
                    self.board[pos[0]][pos[1]].state = 0
                    # print(f"Swapped {(i, j)} and {pos}")
                    return
                        
    def firstMove(self, pos):
        if self.dig(pos) == -1: 
            self.swapBomb(pos)
            # print(f"{pos} had bomb")
        for i in range(self.size[0]): 
            for j in range(self.size[1]):
                # print(self.board[i][j].state)
                if self.board[i][j].state != -1: self.board[i][j].state = self.mineCounter((i, j))[1]
                # print(self.board[i][j].state, end=' ')
            # print()
            
    def flag(self, pos):
        self.board[pos[0]][pos[1]].flagged = not self.board[pos[0]][pos[1]].flagged
            
    def dig(self, pos, first=True):
        # print(f"Digging {pos}...")
        if pos[0] < 0 or pos[0] >= self.size[0] or pos[1] < 0 or pos[1] >= self.size[1]: return 0
        # print(f"{pos}")
        
        if self.board[pos[0]][pos[1]].revealed or self.board[pos[0]][pos[1]].flagged: return 0
        if self.board[pos[0]][pos[1]].state == -1: return (-1 if first else 0)
        self.board[pos[0]][pos[1]].revealed = True; self.remainPiece -= 1
        # print(pos)
        
        tdig = 1
        if (self.dig((pos[0], pos[1] - 1), False) > 0): tdig += self.dig((pos[0], pos[1] - 1), False)
        if (self.dig((pos[0], pos[1] + 1), False) > 0): tdig += self.dig((pos[0], pos[1] + 1), False)
        if (self.dig((pos[0] - 1, pos[1]), False) > 0): tdig += self.dig((pos[0] - 1, pos[1]), False)
        if (self.dig((pos[0] + 1, pos[1]), False) > 0): tdig += self.dig((pos[0] + 1, pos[1]), False)
        # print(f"{pos} {tdig}")
        return tdig
                
class Game():
    def __init__(self, diff):
        if diff == 1: # ez
            self.size = (9, 9)
            self.mine = 10
        elif diff == 2: # med
            self.size = (16, 16)
            self.mine = 40
        elif diff == 3: # hard
            self.size = (16, 30)
            self.mine = 99
        else: # custom
            self.size = (9, 9)
            self.mine = 10
        
        self.board = Board(self.size, self.mine)
        self.board.genBoard()
        self.gameState = 0 # -1 for lost, 1 for won, 0 for others
        self.client = pygame.display.set_mode((SPRITE_SIZE[0]*self.size[0], SPRITE_SIZE[1]*self.size[1]))
        pygame.display.set_caption("Minesweeper")
        
        self.sprite = []
        tmp = []
        for i in range(-2, 9):
            tmp.append(pygame.image.load(os.path.join("assets/piece", f"{i}.png")))
        self.sprite.append(tmp)
        tmp = []
        for i in range(-2, 1):
            tmp.append(pygame.image.load(os.path.join("assets/piece", f"{i}_1.png")))
        self.sprite.append(tmp)
        
    def on(self):
        firstmove = True
        running = True
        lpos = (0, 0)
        while running:
            self.draw(lpos)
            
            if self.gameState:
                input("Press ENTER to continue...")
                running = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.gameState:
                        running = False
                        break
                    cur_pos = pygame.mouse.get_pos()
                    if event.button == 3:
                        self.board.flag((int(cur_pos[0]/SPRITE_SIZE[0]), int(cur_pos[1]/SPRITE_SIZE[1])))
                    elif firstmove:
                        firstmove = False
                        self.board.firstMove((int(cur_pos[0]/SPRITE_SIZE[0]), int(cur_pos[1]/SPRITE_SIZE[1])))
                    elif self.board.dig((int(cur_pos[0]/SPRITE_SIZE[0]), int(cur_pos[1]/SPRITE_SIZE[1]))) == -1:
                        lpos = (int(cur_pos[0]/SPRITE_SIZE[0]), int(cur_pos[1]/SPRITE_SIZE[1]))
                        self.gameState = -1
            if not self.board.remainPiece:
                self.gameState = 1
            if self.gameState and running:
                if self.gameState == 1: print("Won")
                else: print("Lost")
        pygame.quit()
        
                    
    def draw(self, lpos):
        self.client.fill((255, 255, 255))
        pos = (0, 0)
        for i in range(len(self.board.board)):
            for j in range(len(self.board.board[0])):
                if not self.board.board[i][j].revealed:
                    if self.board.board[i][j].flagged: sprite = (self.sprite[0][0] if (self.board.board[i][j].state == -1 or not self.gameState) else self.sprite[1][0])
                    elif (self.board.board[i][j].state == -1 and self.gameState == -1): sprite = self.sprite[1][1] if i == lpos[0] and j == lpos[1] else self.sprite[0][1]
                    else: sprite = self.sprite[1][2]
                else: sprite = self.sprite[0][self.board.board[i][j].state + 2]
                sprite = pygame.transform.scale(sprite, SPRITE_SIZE)
                rect = sprite.get_rect(); rect.topleft = pos
                self.client.blit(sprite, rect)
                pos = (pos[0], pos[1] + SPRITE_SIZE[1])
            pos = (pos[0] + SPRITE_SIZE[0], 0)
        pygame.display.update()