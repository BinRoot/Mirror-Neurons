class Egg:
    def __init__(self, max_hits=10, regular_damage=2, stick_damage=5):
        self.max_hits = max_hits
        self.HP = max_hits
        if stick_damage < regular_damage:
            raise ValueError("stick damage ({}) is less than regular damage ({})".format(stick_damage, regular_damage))
        self.stick_damage = stick_damage - regular_damage
        self.regular_damage = regular_damage
        pass

    def break_egg(self, stick):
        if str(stick) == "ST":
            self.HP -= self.stick_damage
        self.HP -= self.regular_damage

    def is_broken(self):
        return self.HP <= 0

    def __str__(self):
        return "{}. HP: {}/{}".format(repr(self), self.HP, self.max_hits)