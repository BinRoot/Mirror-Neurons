import board
import primate
import egg
import stick


def kill_primate(main_board, primate, primates):
    primate_cell = main_board.get_objects_cell(primate)
    main_board.remove_object(primate_cell[0], primate_cell[1], primate)
    primates.remove(primate)


def run_simulation(main_board, primates, sticks, eggs):
    main_board.plot()
    main_board.time_step += 1
    while len(primates) > 0:
        # print "inspecting primates list"
        for primate in primates:
            # print "doing primate by primate work"
            objects_near_primate = primate.sense_objects(main_board)
            for obj, cell in objects_near_primate.iteritems():
                if primate.pickup_object(main_board, cell[0], cell[1], obj):
                    print "Picked up object: {}".format(obj)
            primate.break_egg()
            if primate.consume_egg():
                continue
            if not primate.is_alive():
                kill_primate(main_board, primate, primates)
            else:
                primate.decrement_hp()
                main_board.move_object_randomly(primate)
            # print main_board
            main_board.plot()
            # print "=============================================="
        main_board.time_step += 1


def main():
    main_board = board.Board(25, 25)

    # Random Initialization
    primates = [primate.Primate() for idx in range(3)]
    eggs = [egg.Egg() for idx in range(2)]
    sticks = [stick.Stick() for idx in range(1)]

    # primates = [primate.Primate()]

    objects = []
    objects.extend(primates)
    objects.extend(eggs)
    objects.extend(sticks)

    # random init
    main_board.rand_init(objects)

    # Specific Initialization
    # main_board = board.Board(3, 3)

    # Add the objects
    # main_board.add_object(1, 2, eggs[0])
    # main_board.add_object(1, 1, primates[0])
    # main_board.add_object(2, 3, primates[1])
    # main_board.add_object(3, 2, sticks[0])

    print "=============================================="
    print main_board
    main_board.plot()
    print "=============================================="


    rv = run_simulation(main_board, primates, sticks, eggs)


if __name__ == "__main__":
    main()
