from pygame_magics.entities.singleton import Singleton


class PlayerStats(metaclass=Singleton):

    def __init__(self):
        self.health = 100
        self.player = None
        self.experience = 0
        self.n = 1

    def check_experience(self):
        """
        it checks if we could go on next leve and if yes it promotes us
        :return:
        """
        if self.experience_growth() <= self.experience:
            self.experience = 0
            self.n += 1

    def experience_growth(self):
        """
        formula that is experience * coef ^ level
        :return:
        """
        return 5 * (1.57 ** (self.n - 1))
