from general import General

class Food():
    pass

class Shit():
    
    all_shit_list: list["Shit"] = []

    def __init__(self, color: tuple[int, int, int], symbol: str):
        self.position_x, self.position_y = 0, 0

        self._color = color
        self._symbol = symbol

    @property
    def color(self) -> tuple[int, int, int]:
        return self._color
    
    @property
    def symbol(self) -> str:
        return self._symbol


























