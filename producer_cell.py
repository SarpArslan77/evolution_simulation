from general import General

import random

#! finish the reproduce logic, copy the predator_cell one and adapt

class Producer_Cell():

    producer_cell_list: list = []

    def __init__(self, general: General):
        self.position_x, self.position_y = 0, 0
        self.general = general

        self.producer_cell_list: list[Producer_Cell] = []

        # attributes which are gene-dependent for each cell 
        #   if a int is assigned, which means it is in test section and does not get inherited from its parent cell

        # 1 = worst, 100 = best
        #   it will be divided by 1000, for example if it is 50 then it is going to be %0.05
        self.food_production_speed: int = random.randint(1, 100)

        # 1 = worst, 5 = best
        self.food_production_zone: int = random.randint(1, 5)

        # 1 = worst, 8 = best
        self.produce_amount: int = random.randint(1, 8)

    def generate_producerCells(self) -> None:
        for _ in range(self.general.starting_generation_producer_cell_count):

            x_position, y_position = self.random_position_producerCells()
            new_cell: Producer_Cell = Producer_Cell(self.general)
            new_cell.position_x, new_cell.position_y = x_position, y_position

            # all created cells must be added into the general cell list and general cell matrix
            self.general.all_cells.append(new_cell)
            self.general.cell_matrix[y_position][x_position] = "P"

            # all created cells must be added into its local list for its types
            self.producer_cell_list.append(new_cell)

    def random_position_producerCells(self) -> tuple[int, int]:

        # loop continues until:
        #   an unoccupied coordinates are generated
        #   it can generate on a suitable biom
        while True:

            x_position: int = random.randint(0, self.general.WORLD_WIDTH//10-1)
            y_position: int = random.randint(0, self.general.WORLD_HEIGHT//10-1)

            if (not(self.general.cell_matrix[y_position][x_position]) and \
                ((self.general.map_matrix[y_position][x_position] == 6) or (self.general.map_matrix[y_position][x_position] == 8))):
                break

        return (x_position, y_position)

    def produce_food(self, producer_cell: "Producer_Cell") -> None:
        # all the possible coordinates in a 5x5 area
        directions: list[tuple[int, int]] = [
            (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), 
            (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), 
            (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), 
            (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), 
            (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)
            ]
        
        # %0.0(self.food_production_speed)
        if random.randint(0, 100000) < producer_cell.food_production_speed:
            dx, dy = random.choice(directions)
            if producer_cell.general.is_movement_possible(producer_cell.position_x, producer_cell.position_y, dx, dy):
                producer_cell.general.utility_matrix[producer_cell.position_y+dy][producer_cell.position_x+dx] = "F"

    def reproduce(self, producer_cell: "Producer_Cell") -> None:

        num_children = producer_cell.produce_amount

        for _ in range(num_children):

            new_cell = Producer_Cell(producer_cell.general)

            possible_positions: list[tuple[int, int]] = [
                (producer_cell.position_x + dx, producer_cell.position_y + dy)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
            ]

            random.shuffle(possible_positions)


    def is_available(self, starting_x: int, starting_y: int, dx: int, dy: int, producer_cell: "Producer_Cell") -> bool:

        # check if the new position is not out of bounds
        #   is not occupied
        #   is suitable for producer cells(aka water or plains)
        if (0 <= starting_x + dx <= producer_cell.general.WORLD_WIDTH // 10 - 1) and (0 <= starting_y + dy <= producer_cell.general.WORLD_HEIGHT // 10 - 1) and \
            not(producer_cell.general.cell_matrix[starting_y + dy][starting_x + dx]) and \
            (producer_cell.general.map_matrix[starting_y + dy][starting_x + dx] == 8 or producer_cell.general.map_matrix[starting_y + dy][starting_x + dx] == 9):
            
            return True
        
        return False

        







