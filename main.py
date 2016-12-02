import board
import primate
import egg
import stick
import numpy as np
import random


def kill_primate(main_board, primate, primates):
    primate_cell = main_board.get_objects_cell(primate)
    main_board.remove_object(primate_cell[0], primate_cell[1], primate)
    primates.remove(primate)


def run_simulation(main_board, primates, sticks, eggs, random_strategy):
    train_x = []
    train_y = []
    prev_img = None

    learned_policy = [0, 2, 0, 1, 1, 0, 2, 1, 1, 1]
    policy_idx = 0

    skill_accomplished = False
    main_board.plot()
    main_board.time_step += 1
    while len(primates) > 0:
        # print "inspecting primates list"
        action_type = [0, 0, 0]
        for primate in primates:
            # print "doing primate by primate work"
            objects_near_primate = primate.sense_objects(main_board)
            picked_out_obj = False
            for obj, cell in objects_near_primate.iteritems():
                if primate.pickup_object(main_board, cell[0], cell[1], obj):
                    print "Picked up object: {}".format(obj)
                    picked_out_obj = True
            if picked_out_obj:
                action_type[2] = 1
                continue
            primate.break_egg()
            if primate.consume_egg():
                continue
            if not primate.is_alive():
                kill_primate(main_board, primate, primates)
            else:
                primate.decrement_hp()

                old_stick_dist = main_board.distance_to_closest(primate, stick.Stick.__module__)
                old_egg_dist = main_board.distance_to_closest(primate, egg.Egg.__module__)

                #### Generate exploration data
                # main_board.move_object_randomly(primate)

                #### Generating test data
                # if random_strategy:
                #     main_board.move_object_randomly(primate)
                # else:
                #     if primate.stick is None:
                #         # move to direction of closest stick
                #         direction = main_board.direction_to_closest(primate, stick.Stick.__module__)
                #         if direction is not None:
                #             main_board.move_object_in_direction(primate, direction)
                #     else:
                #         # move to direction of closest egg
                #         try:
                #             direction = main_board.direction_to_closest(primate, egg.Egg.__module__)
                #             if direction is not None:
                #                 main_board.move_object_in_direction(primate, direction)
                #         except TypeError:
                #             primates = []

                #### Evaluating policy
                if policy_idx < len(learned_policy):
                    if learned_policy[policy_idx] == 0:
                        # move to direction of closest egg
                        try:
                            direction = main_board.direction_to_closest(primate, egg.Egg.__module__)
                            if direction is not None:
                                main_board.move_object_in_direction(primate, direction)
                        except TypeError:
                            primates = []
                    elif learned_policy[policy_idx] == 1:
                        # move to direction of closest stick
                        direction = main_board.direction_to_closest(primate, stick.Stick.__module__)
                        if direction is not None:
                            main_board.move_object_in_direction(primate, direction)
                    policy_idx += 1

                if primate.stick is not None and primate.egg is not None:
                    skill_accomplished = True

                new_stick_dist = main_board.distance_to_closest(primate, stick.Stick.__module__)
                new_egg_dist = main_board.distance_to_closest(primate, egg.Egg.__module__)
                if old_stick_dist - new_stick_dist > old_egg_dist - new_egg_dist:
                    action_type[1] = 1
                else:
                    action_type[0] = 1

            # print main_board
            main_board.plot()
        img = main_board.get_img_for_nn()
        if prev_img is not None:
            img_concat = np.hstack((img.flatten(), prev_img.flatten()))
            # print('img_concat', np.shape(img_concat), action_type)
            train_x.append(img_concat)
            train_y.append(action_type)
        prev_img = img
            # print "=============================================="
        main_board.time_step += 1
    np.save('{}/train_x.npy'.format(main_board.plot_dir), train_x)
    np.save('{}/train_y.npy'.format(main_board.plot_dir), train_y)
    return skill_accomplished


def main():
    total_trials = 10.
    num_success = 0.
    for i in range(int(total_trials)):
        if _main():
            num_success += 1
    print('% success: {}'.format(num_success * 100. / total_trials))


def _main():
    main_board = board.Board(12, 12)

    # Random Initialization
    primates = [primate.Primate(name=str(idx)) for idx in range(1)]
    eggs = [egg.Egg() for idx in range(2)]
    sticks = [stick.Stick() for idx in range(2)]

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

    r = random.random()
    return run_simulation(main_board, primates, sticks, eggs, r < 0.9)


if __name__ == "__main__":
    main()
