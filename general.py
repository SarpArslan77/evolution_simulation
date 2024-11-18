import random

class General():

    # starting cell matrix of the game 100 x 200
    cell_matrix: list[list[str]] = []
    # starting utility (z.B food) matrix of the game
    utility_matrix: list[list[str]] = []

    # cell list for created cells
    all_cells: list = []
    cell_occupied_positions: list[tuple[int, int]] = []
    utility_occupied_positions: list[tuple[int, int]] = []

    def __init__(self):
        # general settings
        self.WORLD_WIDTH = 2000
        self.WORLD_HEIGHT = 1000

        # colors
        self.colors = {
            "WHITE" : (255, 255, 255), #0
            "BLACK" : (0, 0, 0), #1
            "GRAY" : (125, 125, 125), #2
            "ARCTIC_GRAY" : (100, 125, 125), #3
            "RED" : (255, 0, 0), #4
            "DARK_RED" : (150, 30, 30), #5
            "GREEN" : (0, 255, 0), #7
            "DARK_GREEN" : (40, 150, 50), #6
            "DARK_BLUE" : (0, 0, 255), #8
            "BRIGHT_BLUE" : (0, 255, 255), #9
            "PURPLE" : (120, 60, 125), #10
            "YELLOW" : (220, 230, 80), #11
            "BROWN" : (120, 95, 60), #12
            "BRIGHT_BROWN" : (200, 160, 50) # 13
        }

        for y in range(self.WORLD_HEIGHT//10):
            General.cell_matrix.append([])
            General.utility_matrix.append([])
            for _ in range(self.WORLD_WIDTH//10):
                General.cell_matrix[y].append("")
                General.utility_matrix[y].append("")


        self.starting_generation_producer_cell_count: int = 500
        self.starting_generation_predator_cell_count: int = 1

    def random_position(self) -> tuple[int, int]:

        # loop continues until an unoccupied coordinates are generated
        while True:

            x_position: int = random.randint(0, self.WORLD_WIDTH//10-1)
            y_position: int = random.randint(0, self.WORLD_HEIGHT//10-1)

            if not(self.cell_matrix[y_position][x_position]):
                break

        return (x_position, y_position)
    
    def is_movement_possible(self, starting_x: int, starting_y: int, dx: int, dy: int) -> bool:

        # check if the new position is not out of bounds
        #   is not occupied
        if (0 <= starting_x + dx <= self.WORLD_WIDTH // 10 - 1) and (0 <= starting_y + dy <= self.WORLD_HEIGHT // 10 - 1) and \
            (starting_x + dx, starting_y + dy) not in self.cell_occupied_positions:
            return True
        return False