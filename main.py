import random
from collections import deque
from tkinter import *

root = Tk()

# Create a black frame
frame = Frame(root, bg="black")
frame.pack()

d = 20 # diametre d'un element du serpent (= taille d'une cellule)
n_w = 35 # nombre de cellules sur la largeur
n_h = 35 # nombre de cellules sur la hauteur
canvas_w = n_w*d
canvas_h = n_h*d

canvas = Canvas(frame, width=canvas_w, height=canvas_h, bg="black")

coords = [[(i*d, j*d) for j in range(n_h)] for i in range(n_w)]  # matrice i, j -> x, y (coordonnees en pixels du coin haut gauche de la cellule)


def draw_img(img, x, y, width, color_map):
    h = len(img)
    w = len(img[0])

    for i in range(h):
        for j in range(w):
            val = img[i][j]
            canvas.create_rectangle(x + j*width, y + i*width, x + (j+1)*width, y + (i+1)*width, fill=color_map[val], outline=color_map[val])

skull = [
'0000000000000',
'0011111111100',
'0111111111110',
'0111111111110',
'1111001001111',
'1100001000011',
'1100011100011',
'0111111111110',
'0111110111110',
'0001111111000',
'0001101011000',
]
class Head:
    def __init__(self, i, j, body):
        self.body = body
        self.prev_coord = (i, j)
        self.coord = (i, j)
        x, y = coords[i][j]
        self.shape = canvas.create_oval(x, y, x+d, y+d, fill="green")
        self.direction = []  # queue
        self.curr_direction = (1, 0)

        self.path = [(i, j)]

    def move(self):
        dx_, dy_ = self.curr_direction
        dx, dy = self.direction.pop(0) if self.direction else self.curr_direction

        if len(self.body.body_parts) > 1 and ((dx_ == -dx and (dx_ == 1 or dx_ == -1)) or (dy_ == -dy and (dy_ == 1 or dy_ == -1))):  # prevent 180 degrees turn
            dx, dy = dx_, dy_

        self.curr_direction = (dx, dy)
        i, j = self.coord
        new_i, new_j = i+dx, j+dy
        if new_i >= n_w:
            new_i = 0
        if new_i < 0:
            new_i = n_w - 1
        if new_j >= n_h:
            new_j = 0
        if new_j < 0:
            new_j = n_h - 1

        if (new_i, new_j) in self.path:
            return True

        if self.body.apple_coord and (new_i, new_j) == self.body.apple_coord:
            self.body.forbidden.append(self.body.apple_coord)
            bp = self.body.body_parts[-1]
            i_, j_ = bp.prev_coord
            # add body part
            body.body_parts.append(BodyPart(i=i_, j=j_, prev_body_part=bp))
            # remove apple
            canvas.delete(self.body.apple)
            # generate new apple
            self.body.new_apple()
            self.body.inc_score()


        x, y = coords[new_i][new_j]
        canvas.coords(self.shape, x, y, x+d, y+d)

        self.prev_coord = self.coord
        self.coord = (new_i, new_j)

        if len(self.path) == len(self.body.body_parts):
            self.path.pop(0)
        self.path.append(self.coord)

        return False


class BodyPart:
    def __init__(self, i, j, prev_body_part):
        x, y = coords[i][j]
        self.shape = canvas.create_oval(x, y, x+d, y+d, fill="white")

        self.prev_coord = (i, j)
        self.coord = (i, j)
        self.prev_body_part = prev_body_part

    def move(self):
        i, j = self.prev_body_part.prev_coord
        x, y = coords[i][j]
        canvas.coords(self.shape, x, y, x+d, y+d)
        self.prev_coord = self.coord
        self.coord = (i, j)


class Body:
    def __init__(self):
        i, j = n_w//2, n_h//2
        self.head = Head(i=i, j=j, body=self)
        self.body_parts = []
        self.speed = (5, 1)  # x cells/sec + y*score cells/sec
        self.refresh_period = 50 # 100 ms

        prev = self.head
        for k in range(5):
            bp = BodyPart(i-k, j, prev_body_part=prev)
            self.body_parts.append(bp)
            prev = bp

        self.forbidden = [(i-k, j) for k in range(len(self.body_parts))]
        self.apple = None
        self.score = -1
        self.score_obj = None
        self.new_apple()
        self.inc_score()
        self.nmoves = 0

    def inc_score(self):
        if self.score_obj:
            canvas.delete(self.score_obj)
        self.score += 1
        self.score_obj = canvas.create_text(10, 10, text="SCORE: %s" % self.score, fill="white", font=('Helvetica 15 bold'), anchor=NW)

    def new_apple(self):
        forbidden = [*self.forbidden, *self.head.path]
        idx = random.choice([i for i in range(n_w*n_h) if i not in [(j_*n_h) + i_ for i_, j_ in forbidden]])
        j = idx//n_h
        i = idx % n_h
        x, y = coords[i][j]
        self.apple = canvas.create_oval(x, y, x+d, y+d, fill="red")
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

    def new_frame(self):
        self.nmoves += self.refresh_period/1000*(self.speed[0] + self.speed[1]*self.score)  # 50 ms/1000 * (5 + 5*0) cells/sec = 0.25 cells / update
        for _ in range(int(round(self.nmoves, 0))):
            destroy = self.head.move()
            if destroy:
                print(f"SCORE: {self.score}")
                canvas.configure(bg="#8b0000")
                canvas.delete(self.head.shape)
                for bp in self.body_parts:
                    canvas.delete(bp.shape)
                if self.apple:
                    canvas.delete(self.apple)
                draw_img(skull, (canvas_w-len(skull[0])*20)//2, (canvas_h-len(skull)*20)//2, 20, color_map={"0": "#8b0000", "1": "black"})
                #root.destroy()
                return

            for bp in self.body_parts:
                bp.move()
            self.nmoves -= 1
        root.after(self.refresh_period, body.new_frame)


body = Body()
canvas.pack()
# Bind the "move_circle" function to keyboard events
root.bind("<Key>", body.change_direction)
body.new_frame()
root.mainloop()
