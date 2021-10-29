#Encoder logic

class Encoder:
    def __init__(self, pin_left, pin_right):
        self.p_l = pin_left
        self.p_r = pin_right
        self.s1 = 0
        self.s2 = 0

    def rotate(self, channel, left_status, right_status):
        if left_status == right_status:
            return False
        if self.s1 != 0:
            self.s1 = 0
            return False
        else:
            self.s1 = 1
            if channel == self.p_r:
                if self.s2 < 1:
                   self.s2 += 1
            else:
                if self.s2 > -1:
                    self.s2 -= 1

            if channel == self.p_r and self.s2 >= 0:
                return channel
            if channel == self.p_l and self.s2 <= 0:
                return channel
