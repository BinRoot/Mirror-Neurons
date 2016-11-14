import random

from matplotlib.ticker import MultipleLocator

import egg
import primate
import stick

import matplotlib.pyplot as plt
import time, os

class Board:
    def __init__(self, n=10, m=10, empty_square=None, objects=[]):
        self.empty_square = empty_square
        self.n = n
        self.m = m
        self.board = [[self.empty_square for i in range(n)] for j in range(m)]
        self.objects_position = {}
        self.movement_direction = {}
        self.movement_direction.setdefault("up", (-1, 0))
        self.movement_direction.setdefault("down", (1, 0))
        self.movement_direction.setdefault("right", (0, 1))
        self.movement_direction.setdefault("left", (0, -1))
        self.movement_direction.setdefault("up-left", (-1, -1))
        self.movement_direction.setdefault("up-right", (-1, 1))
        self.movement_direction.setdefault("down-left", (1, -1))
        self.movement_direction.setdefault("down-right", (1, 1))
        self.possible_directions = self.movement_direction.keys()
        self._direction_to_arrow = {'N': '^', 'S': 'v', 'E': '>', 'W': '<'}
        self.plot_dir = 'plots_{}'.format(int(time.time()))
        self._mkdir(self.plot_dir)
        self.time_step = 0

    def _mkdir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def __repr__(self):
        return str(self)

    def __str__(self):
        s = "{}".format(self.objects_position)
        for row in self.board:
            s = "{}\n{}".format(s, row)
        return s

    def plot(self):
        primate_xs, primate_ys = [], []
        primate_labels = []
        stick_xs, stick_ys = [], []
        egg_xs, egg_ys = [], []

        for i in range(self.n):
            for j in range(self.m):
                if isinstance(self.board[j][i], primate.Primate):
                    primate_xs.append(i)
                    primate_ys.append(j)
                    arrow_label = ''
                    if self.board[j][i].egg:
                        arrow_label += 'o'
                    elif self.board[j][i].stick:
                        arrow_label += '/'
                    primate_labels.append(arrow_label)
                elif isinstance(self.board[j][i], egg.Egg):
                    egg_xs.append(i)
                    egg_ys.append(j)
                elif isinstance(self.board[j][i], stick.Stick):
                    stick_xs.append(i)
                    stick_ys.append(j)

        plt.rcParams['axes.facecolor'] = (0, 0.3, 0.1)
        plt.scatter(primate_xs, primate_ys, s=200, color='brown', alpha=1.0)
        for i in range(len(primate_xs)):
            plt.annotate(primate_labels[i], (primate_xs[i], primate_ys[i]))
        plt.scatter(stick_xs, stick_ys, color='red', marker='_', s=100, alpha=1)
        plt.scatter(egg_xs, egg_ys, color='yellow', marker='o', alpha=1)

        axes = plt.gca()

        spacing = 1. # This can be your user specified spacing.
        minorLocator = MultipleLocator(spacing)
        axes.yaxis.set_minor_locator(minorLocator)
        axes.xaxis.set_minor_locator(minorLocator)

        axes.grid(True, which='minor')
        axes.set_xlim([-1, self.n + 1])
        axes.set_ylim([-1, self.m + 1])
        plt.savefig('{}/{}.png'.format(self.plot_dir, self.time_step))
        plt.clf()
        # plt.show()

    def rand_init(self, objects):
        if len(objects) > self.n * self.m:
            raise ValueError("There are more objects that require placing than available spaces on the board.\n")
        placement_table = {}
        for i in range(0, self.m):
            for j in range(0, self.n):
                placement_table.setdefault(random.random(), (i, j))
        for idx, key in enumerate(sorted(placement_table.keys())):
            if idx >= len(objects):
                return
            i_idx = placement_table[key][0]
            j_idx = placement_table[key][1]
            self.add_object(i_idx, j_idx, objects[idx])

    def add_object(self, i, j, obj):
        if self.board[i][j] != self.empty_square:
            raise KeyError("self.board[{}][{}] is not empty.".format(i, j))
        self.board[i][j] = obj
        self.objects_position.setdefault(obj, (i, j))
        return True

    def remove_object(self, i, j, obj):
        if self.board[i][j] != obj:
            raise KeyError("self.board[{}][{}] is not {}".format(i, j, obj))
        self.board[i][j] = self.empty_square
        del self.objects_position[obj]
        return True

    def move_object_to_cell(self, obj, source, destination):
        self.remove_object(source[0], source[1], obj)
        self.add_object(destination[0], destination[1], obj)
        return True

    def move_object_in_direction(self, obj, direction):
        # source cell co-ordinates
        i_s, j_s = self.get_objects_cell(obj)
        if direction not in self.movement_direction.keys():
            raise KeyError("{} is not a defined direction.".format(direction))
        i_offset, j_offset = self.movement_direction[direction]

        # destination cell co-ordinates
        i_d = i_s + i_offset
        j_d = j_s + j_offset

        # check if the destination cell is a valid cell
        if not self.is_valid_cell(i_d, j_d):
            return False

        # ensure the destination cell is empty
        if self.board[i_d][j_d] != self.empty_square:
            return False

        # move the object
        self.move_object_to_cell(obj, (i_s, j_s), (i_d, j_d))
        return True

    def move_object_randomly(self, obj, max_attempts=5):
        attempts = 0
        while attempts < max_attempts:
            direction = random.choice(self.possible_directions)
            if self.move_object_in_direction(obj, direction):
                print "Object {} was moved in direction {}".format(obj, direction)
                return True
        print "Object {} was not able to move after {} attempts".format(primate, max_attempts)
        return False

    def is_valid_cell(self, i, j):
        if i >= len(self.board) or i < 0:
            return False
        if j >= len(self.board[0]) or j < 0:
            return False
        return True

    def is_cell_occupied(self, i, j):
        '''
        returns True if cell is occupied
        returns False if cell is not occupied
        '''
        if not self.is_valid_cell(i, j):
            return False
        if self.board[i][j].__class__.__name__ != self.empty_square.__class__.__name__:
            return True
        return False

    def cell_status(self, i, j):
        '''
        returns the __class__.__name__ attribute of the object present in the cell
        '''
        return self.board[i][j].__class__.__name__

    def get_objects_cell(self, obj):
        if obj in self.objects_position:
            return self.objects_position[obj]
        return None


def main():
    board = Board(n=4, m=5)
    print board
    bird = 'B'
    egg = 'E'
    stick = 'S'
    none = None
    objects = [bird, bird, bird, egg, egg, stick]
    board.rand_init(objects)
    print board.__class__.__name__
    print board

if __name__ == "__main__":
    main()
