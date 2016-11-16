class Primate:
    def __init__(self, name='', maximum_health=20, health_decay_per_move=1, health_recovered_from_food=5):
        self.directions = ['N', 'E', 'S', 'W']
        self.direction_idx = 0
        self.direction = self.directions[self.direction_idx]
        self.egg = None
        self.stick = None
        self.name = name
        self.max_hp = maximum_health
        self.hp = maximum_health
        self.health_decay_per_move = health_decay_per_move
        self.health_recovered_from_food = health_recovered_from_food

    def __str__(self):
        return "\'{}: HP: {}/{}, EGG: {}, STICK: {}\'".format(repr(self), self.hp, self.max_hp, self.stick, self.egg)

    def rotate_right(self):
        self.direction_idx = (self.direction_idx + 1) % len(self.directions)
        self.direction = self.directions[self.direction_idx]

    def rotate_left(self):
        self.direction_idx = (self.direction_idx - 1) % len(self.directions)
        self.direction = self.directions[self.direction_idx]

    def sense_objects(self, board):
        current_position = board.get_objects_cell(self)
        objects_found = {}
        for i_offset in [-1, 0, 1]:
            for j_offset in [-1, 0, 1]:

                i_idx = current_position[0] + i_offset
                j_idx = current_position[1] + j_offset

                if ( board.is_valid_cell(i_idx, j_idx)
                    and board.is_cell_occupied(i_idx, j_idx)
                    and board.board[i_idx][j_idx].__class__.__name__ != self.__class__.__name__
                    ):
                    objects_found.setdefault(board.board[i_idx][j_idx], (i_idx, j_idx))

        return objects_found

    def pickup_object(self, board, i, j, obj):
        # check if the primate is already holding a stick or an egg
        if self.egg != None and obj.__class__.__name__ == "Egg":
            return False
        if self.stick != None and obj.__class__.__name__ == "Stick":
            return False

        # "pickup" the object by giving it to the primate
        if obj.__class__.__name__ == "Egg":
            self.egg = obj
        else:
            self.stick = obj

        # remove the object from the board
        board.remove_object(i, j, obj)

        # indicate that the function performed correctly
        return True

    def break_egg(self):
        if "Egg" in repr(self.egg):
            self.egg.break_egg(self.stick)
        return True

    def consume_egg(self):
        if "Egg" in repr(self.egg) and self.egg.is_broken():
            print "consuming egg: {}".format(self.egg)
            self.hp = min(self.max_hp, self.hp + self.health_recovered_from_food)
            self.egg = None
            return True
        print "could not consume egg: {}".format(self.egg)
        return False

    def decrement_hp(self):
        self.hp = self.hp - 1

    def is_alive(self):
        if self.hp > 0:
            return True
        print "Primate {} is dead.".format(repr(self))
        return False


def main():
    p = Primate()
    print p
    for idx in range(0, 4):
        p.rotate_right()
        print p
    for idx in range(0, 4):
        p.rotate_left()
        print p

if __name__ == "__main__":
    main()