from future.moves import tkinter as tk
from future.moves.tkinter import Canvas, Frame


class UICell:
    def __init__(self, root, canvas, x, y, w, h):
        self.canvas = canvas

        c_x = x + w/2
        c_y = y + h/2
        points_t = [x, y, x + w, y, c_x, c_y]
        points_l = [x, y, x, y + h, c_x, c_y]
        points_r = [x + w, y, x + w, y + h, c_x, c_y]
        points_b = [x, y + h, x + w, y + h, c_x, c_y]
        self.up_bg_id = self.canvas.create_polygon(points_t, outline='#000', fill='#ccc', width=1)
        self.left_bg_id = self.canvas.create_polygon(points_l, outline='#000', fill='#ccc', width=1)
        self.right_bg_id = self.canvas.create_polygon(points_r, outline='#000', fill='#ccc', width=1)
        self.down_bg_id = self.canvas.create_polygon(points_b, outline='#000', fill='#ccc', width=1)

        self.up_num = tk.Label(root, width="8", text="0.0")  # top
        self.up_num.place(x=c_x-w/4+6, y=y+5)
        self.left_num = tk.Label(root, width="8", text="0.0")  # left
        self.left_num.place(x=x+7, y=c_y-9)
        self.right_num = tk.Label(root, width="8", text="0.0")  # right
        self.right_num.place(x=c_x+5, y=c_y-9)
        self.down_num = tk.Label(root, width="8", text="0.0")  # bottom
        self.down_num.place(x=c_x-w/4+6, y=y+h-25)

        self.action_id = {
            'left': self.left_num,
            'up': self.up_num,
            'right': self.right_num,
            'down': self.down_num
        }

        r = 4
        self.dot_id = self.canvas.create_oval(c_x - r, c_y - r, c_x + r, c_y + r, outline="#333", fill="#999")

        # self.canvas.itemconfigure(tmp, outline='#f00', fill='#333')

    def set_active(self, flag):
        color = '#49f' if flag else '#999'
        self.canvas.itemconfigure(self.dot_id, outline="#333", fill=color)

    def update(self, action, value, terminal):
        widget = self.action_id[action]
        widget['text'] = value
        bg = ''
        if value[0] == '-':
            bg = '#f00' if terminal else '#f99'
        else:
            bg = '#0c0' if terminal else '#9f9'
        widget['bg'] = bg


class UI(Frame):
    def __init__(self, root, agent):
        super().__init__()
        self.canvas = Canvas(self)
        self.pack(fill=tk.BOTH, expand=1)

        self.root = root

        self.cell_width = 150
        self.cell_height = 100
        self.max_width = 0
        self.max_height = 0
        self.row = -1
        self.col = -1
        self.grid = []

        self.agent = agent

        e = '{:.1f}'.format(self.agent.get_epsilon())
        tk.Label(text="Eps:").place(x=5, y=7)
        self.dec = tk.Button(text="-", width=4, command=self.__decrease_eps)
        self.eps = tk.Label(text=str(e), width=4, bg='#ccc', fg='#00f')
        self.inc = tk.Button(text="+", width=4, command=self.__increase_eps)
        self.dec.place(x=35, y=5)
        self.eps.place(x=80, y=8)
        self.inc.place(x=120, y=5)

    def update(self):
        height, width = self.agent.world.get_size()
        if self.max_width != width and self.max_height != height:
            self.max_width = width
            self.max_height = height
            self.__create_grid()
            self.agent.world.ui_grid = self.grid

        pos = self.agent.world.get_position()
        if pos['row'] >= 0 and pos['col'] >= 0:
            if self.row >= 0 and self.col >= 0:
                if self.row != pos['row'] or self.col != pos['col']:
                    cell = self.grid[self.row][self.col]
                    cell.set_active(False)
            self.row = pos['row']
            self.col = pos['col']
            cell = self.grid[self.row][self.col]
            cell.set_active(True)

        while len(self.agent.update_queue):
            upd = self.agent.update_queue.popleft();
            r = upd['row']
            c = upd['col']
            a = upd['action']
            v = upd['value']
            t = upd['terminal']
            self.grid[r][c].update(a, v, t)

    def __create_grid(self):
        for y in range(self.max_height):
            row = []
            for x in range(self.max_width):
                cell = self.__create_cell(x, y)
                row.append(cell)
            self.grid.append(row)
        self.canvas.pack(fill=tk.BOTH, expand=1)

    def __create_cell(self, x, y):
        x = x * self.cell_width + 5
        y = y * self.cell_height + 50
        return UICell(self.root, self.canvas, x, y, self.cell_width, self.cell_height)

    def __decrease_eps(self):
        e = self.agent.get_epsilon() - 0.1
        if e < 0.0:
            e = 0
        self.eps['text'] = '{:.1f}'.format(e)
        self.agent.set_epsilon(e)

    def __increase_eps(self):
        e = self.agent.get_epsilon() + 0.1
        if e > 1.0:
            e = 1.0
        self.eps['text'] = '{:.1f}'.format(e)
        self.agent.set_epsilon(e)