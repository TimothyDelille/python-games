import random
import tkinter
import math

from utils import draw_img, skull

class Head:
    def __init__(self, i, j, game):
        self.game = game
        # init prev_coord and coord variables
        self.prev_coord = (i, j)
        self.coord = (i, j)
        # convert i, j index to pixel coordinates
        x, y = self.game.coords[i][j]
        # init canvas shape
        self.shape = self.game.canvas.create_oval(x, y, x+self.game.d, y+self.game.d, fill="green", outline="green")

        self.direction = []  # queue where we store (dx, dy) direction tuples
        self.curr_direction = (1, 0)
        self.path = [(i, j)]

    def move(self):
        dx_, dy_ = self.curr_direction
        dx, dy = self.direction.pop(0) if self.direction else self.curr_direction

        if len(self.game.body_parts) > 1 and ((dx_ == -dx and (dx_ == 1 or dx_ == -1)) or (dy_ == -dy and (dy_ == 1 or dy_ == -1))):  # prevent 180 degrees turn
            dx, dy = dx_, dy_

        self.curr_direction = (dx, dy)
        i, j = self.coord
        new_i, new_j = i+dx, j+dy
        if new_i >= self.game.n_w:
            new_i = 0
        if new_i < 0:
            new_i = self.game.n_w - 1
        if new_j >= self.game.n_h:
            new_j = 0
        if new_j < 0:
            new_j = self.game.n_h - 1

        if (new_i, new_j) in self.path:
            return True

        if self.game.apple_coord and (new_i, new_j) == self.game.apple_coord:
            self.game.forbidden.append(self.game.apple_coord)
            bp = self.game.body_parts[-1]
            i_, j_ = bp.prev_coord
            # add body part
            self.game.body_parts.append(BodyPart(i=i_, j=j_, game=self.game, prev_body_part=bp))
            # remove apple
            self.game.canvas.delete(self.game.apple)
            # generate new apple
            self.game.new_apple()
            self.game.inc_score()


        x, y = self.game.coords[new_i][new_j]
        self.game.canvas.coords(self.shape, x, y, x+self.game.d, y+self.game.d)

        self.prev_coord = self.coord
        self.coord = (new_i, new_j)

        if len(self.path) == len(self.game.body_parts):
            self.path.pop(0)
        self.path.append(self.coord)

        return False


class BodyPart:
    def __init__(self, i, j, game, prev_body_part):
        self.game = game
        # convert i, j index to pixel coordinates
        x, y = self.game.coords[i][j]
        # init canvas shape
        self.shape = self.game.canvas.create_oval(x, y, x+self.game.d, y+self.game.d, fill="white", outline="white")

        # init variables
        self.prev_coord = (i, j)
        self.coord = (i, j)
        self.prev_body_part = prev_body_part

    def move(self):
        i, j = self.prev_body_part.prev_coord
        x, y = self.game.coords[i][j]
        self.game.canvas.coords(self.shape, x, y, x+self.game.d, y+self.game.d)
        self.prev_coord = self.coord
        self.coord = (i, j)


class Game:
    def __init__(self):
        # init tkinter root and canvas
        self.d = 20 # diametre d'un element du serpent (= taille d'une cellule)
        self.n_w = 35 # nombre de cellules sur la largeur
        self.n_h = 35 # nombre de cellules sur la hauteur
        self.canvas_w = self.n_w*self.d
        self.canvas_h = self.n_h*self.d

        self.root = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.root, width=self.canvas_w, height=self.canvas_h, bg="black")

        # create coordinates map
        self.coords = [[(i*self.d, j*self.d) for j in range(self.n_h)] for i in range(self.n_w)]  # matrice i, j -> x, y (coordonnees en pixels du coin haut gauche de la cellule)

        self.skull = []
        self.init_body()

    def init_body(self):
        # create head at the center
        i, j = self.n_w//2, self.n_h//2
        self.head = Head(i=i, j=j, game=self)
        self.body_parts = []
        self.speed = (5, 1)  # x cells/sec + y*score cells/sec
        self.fps = 60
        self.refresh_period = math.floor(1000/self.fps) # in ms

        prev = self.head
        for k in range(5):
            bp = BodyPart(i-k, j, game=self, prev_body_part=prev)
            self.body_parts.append(bp)
            prev = bp

        self.forbidden = [(i-k, j) for k in range(len(self.body_parts))]
        self.apple = None
        self.score = -1
        self.score_obj = None
        self.new_apple()
        self.inc_score()
        self.nmoves = 0

        self.canvas.pack()
        self.collision = False

    def inc_score(self):
        if self.score_obj:
            self.canvas.delete(self.score_obj)
        self.score += 1
        self.score_obj = self.canvas.create_text(10, 10, text="SCORE: %s" % self.score, fill="white", font=('Helvetica 15 bold'), anchor=tkinter.NW)

    def new_apple(self):
        forbidden = [*self.forbidden, *self.head.path]
        idx = random.choice([i for i in range(self.n_w*self.n_h) if i not in [(j_*self.n_h) + i_ for i_, j_ in forbidden]])
        j = idx//self.n_h
        i = idx % self.n_h
        x, y = self.coords[i][j]
        self.apple = self.canvas.create_oval(x, y, x+self.d, y+self.d, fill="red")
        self.apple_coord = (i, j)

    def change_direction(self, event):
        dx, dy = self.head.direction[-1] if self.head.direction else self.head.curr_direction
        new_dx, new_dy = dx, dy
        if event.keysym == "Up":
            new_dx, new_dy= (0, -1)
        elif event.keysym == "Down":
            new_dx, new_dy = (0, 1)
        elif event.keysym == "Left":
            new_dx, new_dy = (-1, 0)
        elif event.keysym == "Right":
            new_dx, new_dy = (1, 0)

        self.head.direction.append((new_dx, new_dy))

    def restart(self):
        self.button.destroy()
        self.canvas.delete(self.button_window)
        self.canvas.configure(bg="black")
        self.canvas.delete(self.score_obj)
        for obj in self.skull:
            self.canvas.delete(obj)
        self.init_body()
        self.run()

    def game_over_screen(self):
        self.canvas.configure(bg="#8b0000")
        self.canvas.delete(self.head.shape)
        for bp in self.body_parts:
            self.canvas.delete(bp.shape)
        if self.apple:
            self.canvas.delete(self.apple)
        self.skull = draw_img(skull, (self.canvas_w-len(skull[0])*20)//2, (self.canvas_h-len(skull)*20)//2, 20, color_map={"0": "#8b0000", "1": "black"}, canvas=self.canvas)
        self.button = tkinter.Button(self.root, width="10", height="2", text="Restart", command = self.restart)
        self.button_window = self.canvas.create_window(self.canvas_w//2, 4*self.canvas_h//5, anchor=tkinter.CENTER, window=self.button)

    def new_frame(self):
        # number of moves to do
        self.nmoves += self.refresh_period/1000*(self.speed[0] + self.speed[1]*self.score)  # 50 ms/1000 * (5 + 5*0) cells/sec = 0.25 cells / update
        for _ in range(int(round(self.nmoves, 0))):
            collision = self.head.move()
            if collision:
                self.game_over_screen()
                return

            for bp in self.body_parts:
                bp.move()
            self.nmoves -= 1
        self.root.after(self.refresh_period, self.new_frame)

    def run(self):
        self.root.bind("<Key>", self.change_direction)
        self.new_frame()
        self.root.mainloop()

if __name__ == "__main__":
    game = Game()
    game.run()
