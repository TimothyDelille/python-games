import tkinter
import math
import random

from utils import draw_img, skull

class Game:
    def __init__(self):
        self.root = tkinter.Tk()
        self.h, self.w = 500, 500
        self.bg = "#70C5CE"
        self.canvas = tkinter.Canvas(self.root, width=self.w, height=self.h)
        fps = 60
        self.refresh_period = math.floor(1000/fps)  # FPS in ms


        self.d = 40
        # let's place the y axis at h//5 with y going up
        self.ytop = self.h//5
        self.g = 15*1e-4  # pixels/ms^2
        self.speed = 0.2 # pixels per ms
        self.vimpulse = 0.5 # pixels per ms

        # gap has to be high enough to allow for a jump
        # v = -gt + vimpulse
        # v = 0 => t = vimpulse/g
        # y(t) = -1/2 gt^2 + vimpulse*t + 0
        # pipe gap = 1/2 vimpulse^2/g
        self.pipe_gap = math.ceil(self.vimpulse**2/self.g + self.d)
        self.pipe_width = 50

    def init_game(self):
        self.y = 0 # top of the bird
        self.v = 0
        self.t = 0
        self.y0 = self.y
        self.v0 = 0

        self.canvas.configure(bg=self.bg)
        self.bird = self.canvas.create_oval(self.w//2, self.ytop - self.y, self.w//2 + self.d, self.ytop - self.y + self.d, fill="red", outline="black")
        self.canvas.pack()

        self.counter = 0
        self.pipe_id = 0
        self.pipes = [] # list with tuples (id, bottom canvas obj, top canvas obj)

        self.last_pipe_ts = 0
        self.score_obj = None
        self.score = 0
        self.game_over = False

    def move_bird(self):
        # ma = -mg
            # a = -g
            # v = -gt + A
            # y = -1/2gt^2 + v_0*t + y_0

        _, y, _, _ = self.canvas.coords(self.bird)
        if y >= self.h-self.d and self.v < 0:
            self.t = 0
            # y = ytop-h
            # => h-ytop = -1/2gt^2 + v_0t + y_0
            # => -1/2gt^2 + v_0t + y_0 - y_top + h= 0
            # delta = v_0^2 + 2g(y_0 - y_top + h)
            # t = (v_0 + sqrt(delta))/g
            # vmax = gt + v_0 = -sqrt(delta)

            self.v0 = -self.v #math.sqrt(self.v0**2 + 2*self.g*(self.y0 - self.ytop + self.h))
            self.y0 = self.ytop - self.h + self.d

        self.t += self.refresh_period
        self.v = -self.g*self.t + self.v0
        self.y = -1/2*self.g*self.t**2 + self.v0*self.t + self.y0
        self.canvas.coords(self.bird, self.w//2, self.ytop - self.y, self.w//2 + self.d, self.ytop - self.y + self.d)

    def new_pipe(self):
        # max height has to be attainable in the time it takes for the pipe to reach the bird:
        # t = (w//2) / speed (in ms)
        # assuming you come from the bottom: vimpulse*t - d - margin >= max_h
        # min_h = h - max_h
        # maxh = max(self.h, self.vimpulse*(self.w//2/self.speed) - self.pipe_gap)
        # minh = self.h - maxh
        maxh = self.h - self.pipe_gap - 10
        minh = self.h - maxh
        height = random.randint(minh, maxh)
        bottom = self.canvas.create_rectangle(self.w, self.h - height, self.w+self.pipe_width, self.h, fill="#73BD2E", outline="black")
        top = self.canvas.create_rectangle(self.w, 0, self.w + self.pipe_width, self.h - height - self.pipe_gap, fill="#73BD2E", outline="black")
        self.pipe_id += 1
        self.pipes.append((self.pipe_id, bottom, top))

    def move_pipe(self):
        (pipe_id, bottom, top) = self.pipes.pop(0)
        x1, yb, x2, _ = self.canvas.coords(bottom)
        _, _, _, yt = self.canvas.coords(top)

        if x2 <= 0:
            # don't add them back to the queue
            return

        x = x1 - self.speed*self.refresh_period
        self.canvas.coords(bottom, x, yb, x+self.pipe_width, self.h)
        self.canvas.coords(top, x, 0, x+self.pipe_width, yt)
        self.pipes.append((pipe_id, bottom, top)) # add them back to the queue

    def move_pipes(self):
        l = len(self.pipes)
        for _ in range(l):
            self.move_pipe()

    def check_for_collision(self):
        x1, y1, x2, y2 = self.canvas.coords(self.bird)
        for i in range(len(self.pipes)):
            (_, bottom, top) = self.pipes[i]
            xb1, yb, xb2, _ = self.canvas.coords(bottom)
            _, _, _, yt = self.canvas.coords(top)
            if (x1 > xb2) or (x2 < xb1):
                continue
            if (y1 <= yt) or (y2 >= yb):
                return True

    def update_score(self):
        xbird, _, _, _ = self.canvas.coords(self.bird)
        for i in range(len(self.pipes)):
            (pipe_id, bottom, top) = self.pipes[i]
            _, _, x, _ = self.canvas.coords(bottom)
            if (xbird > x) and pipe_id > self.score:
                self.score = pipe_id

        if self.score_obj:
            self.canvas.delete(self.score_obj)
        self.score_obj = self.canvas.create_text(10, 10, text="SCORE: %s" % self.score, fill="white", font=('Helvetica 15 bold'), anchor=tkinter.NW)

    def new_frame(self):
        self.counter += self.refresh_period
        self.move_bird()
        if self.counter - self.last_pipe_ts >= 2000: # every 2 sec
            self.new_pipe()
            self.last_pipe_ts = self.counter
        self.move_pipes()
        self.update_score()

        if self.check_for_collision():
            self.game_over_screen()
            return
        self.root.after(self.refresh_period, self.new_frame)

    def jump(self, event):
        if (event.keysym == "space") and not self.game_over:
            _, y, _, _ = self.canvas.coords(self.bird)
            # make sure you can't go over ytop with the impulse
            # v = 0 => -gt + v_impulse = 0 => t_top = v_impulse/g
            # y(t_top) = -1/2 g*t_top^2 + v_impulse*t_top + y_0 <= 0 (y_top)
            # => -1/2 v_impulse^2/g + v_impulse^2/g + y_0 <= 0
            # => v_impulse <= sqrt(-y_0*2g) (y_0 < 0)
            self.y0 = self.ytop - y
            #self.v0 =  min(self.vimpulse, math.sqrt(-self.y0*2*self.g)) #abs(self.v)
            self.v0 = self.vimpulse
            self.t = 0

    def run(self):
        self.root.bind("<Key>", self.jump)
        self.init_game()
        self.new_frame()
        self.root.mainloop()
    def restart(self):
        self.button.destroy()
        self.canvas.delete(self.button_window)
        self.canvas.delete(self.score_obj)
        for obj in self.skull:
            self.canvas.delete(obj)
        self.run()

    def game_over_screen(self):
        self.game_over = True
        self.canvas.configure(bg="#8b0000")
        self.canvas.delete(self.bird)
        for (_, b, t) in self.pipes:
            self.canvas.delete(b)
            self.canvas.delete(t)
        self.skull = draw_img(skull, (self.w-len(skull[0])*20)//2, (self.h-len(skull)*20)//2, 20, color_map={"0": "#8b0000", "1": "black"}, canvas=self.canvas)
        self.button = tkinter.Button(self.root, width="10", height="2", text="Restart", command = self.restart)
        self.button_window = self.canvas.create_window(self.w//2, 4*self.h//5, anchor=tkinter.CENTER, window=self.button)

if __name__ == "__main__":
    game = Game()
    game.run()


