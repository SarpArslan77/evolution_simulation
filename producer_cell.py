from general import General

import random

class Producer_Cell():
    def __init__(self, general: General):
        self.position_x, self.position_y = 0, 0
        self.general = general

        self.producer_cell_list: list[Producer_Cell] = []

        # attributes which are gene-dependent for each cell 
        #   if a int is assigned, which means it is in test section and does not get inherited from its parent cell

        # 1 = worst, 100 = best
        #   it will be divided by 1000, for example if it is 50 then it is going to be %0.05
        self.food_production_speed: int = 1000

        # 1 = worst, 5 = best
        self.food_production_zone: int = 3

    def generate_producerCells(self) -> None:
        for _ in range(self.general.starting_generation_producer_cell_count):
            x_position, y_position = self.general.random_position()
            new_cell: Producer_Cell = Producer_Cell(self.general)
            new_cell.position_x, new_cell.position_y = x_position, y_position

            # all created cells must be added into the general cell list and general cell matrix
            self.general.all_cells.append(new_cell)
            self.general.cell_matrix[y_position][x_position] = "P"

            # all created cells must be added into its local list for its types
            self.producer_cell_list.append(new_cell)

            # occupied positions must be added to the list
            self.general.cell_occupied_positions.append((x_position, y_position))

    def produce_food(self) -> None:
        for cell in self.producer_cell_list:
            # all the possible coordinates in a 5x5 area
            directions: list[tuple[int, int]] = [
                (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), 
                (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), 
                (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), 
                (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), 
                (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)
                ]
            
            # %0.0(self.food_production_speed)
            if random.randint(0, 100000) < cell.food_production_speed:
                dx, dy = random.choice(directions)
                if self.general.is_movement_possible(cell.position_x, cell.position_y, dx, dy):
                    #print("from the function" + str(dx) + " " + str(dy))
                    self.general.utility_matrix[cell.position_y+dy][cell.position_x+dx] = "F"
                    self.general.utility_occupied_positions.append((cell.position_x+dx, cell.position_y+dy))
                