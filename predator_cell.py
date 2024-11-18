import random

#! Add the food sense logic, if movement not possible due to another blocking cell
#!  eaten foods do not dissapear

from general import General

class Predator_Cell():
    def __init__(self, general: General):
        self.position_x, self.position_y = 0, 0
        self.general = general

        self.predator_cell_list: list[Predator_Cell] = []

        self.random_movement: bool = True

        # attributes which are gene-dependent for each cell 
        #   if a int is assigned, which means it is in test section and does not get inherited from its parent cell

        # 1 = hungry, 10 = full
        self.food_supply: int = 5

        # 1 = worst, 5 = best
        self.food_sense_zone: int = 3
    
    def random_move_cells(self) -> None:

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)] 
        for predator_cell in self.predator_cell_list:

            # old position of the cell must be cleared
            self.general.cell_matrix[predator_cell.position_y][predator_cell.position_x] = ""

            # check if has hunger
            #   and has food in the food zone
            """if self.food_supply != 10:
                food_position: tuple[int, int] = self.sense_food()
                #print(food_position)
                if food_position:
                    dx, dy = self.position_x-food_position[0], self.position_y-food_position[1]
                    predator_cell.position_x += dx
                    predator_cell.position_y += dy

                    # mark the random movement False since, it is not needed
                    self.random_movement = False"""

            # choose the random movement as long as it fulfills the conditions in is_movement_possible
            while self.random_movement:
                dx, dy = random.choice(directions)
                if self.general.is_movement_possible(predator_cell.position_x, predator_cell.position_y, dx, dy):
                    predator_cell.position_x += dx
                    predator_cell.position_y += dy
                    break

            # re-set the self.random_movement to True for future movements
            self.random_movement = True

            # check if the cell is on a food
            if self.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] == "F":
                self.eat_food()
                # mark the food as eaten
                self.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] == ""

            # new position must be marked
            self.general.cell_matrix[predator_cell.position_y][predator_cell.position_x] = "C"

    def generate_predatorCells(self) -> None:

        for _ in range(self.general.starting_generation_predator_cell_count):
            x_position, y_position = self.general.random_position()
            new_cell: Predator_Cell = Predator_Cell(self.general)
            new_cell.position_x, new_cell.position_y = x_position, y_position

            self.general.all_cells.append(new_cell)
            self.general.cell_matrix[y_position][x_position] = "C"

            self.predator_cell_list.append(new_cell)

            self.general.cell_occupied_positions.append((x_position, y_position))

    def sense_food(self) -> tuple[int, int] | None:

        for predator_cell in self.predator_cell_list:

            # Create the sense zone for food according to self.food_sense_zone
            possible_food_locations: list[tuple[int, int]] = predator_cell.create_sense_zone(predator_cell.food_sense_zone)
            
            # find actual food locations within the sense zone
            found_food_locations: list[tuple[int, int]] = []
            for location in possible_food_locations:
                #print(predator_cell.position_y//10, predator_cell.position_x//10)
                #print([predator_cell.position_y//10+location[1]],[predator_cell.position_x//10+location[0]])
                if predator_cell.general.utility_matrix[predator_cell.position_y//10+location[1]][predator_cell.position_x//10+location[0]] == "F":
                    found_food_locations.append(location)


        
        # DEBUGGING: print possible and found food locations 
        #print(f"Possible locations: {possible_food_locations}")
        #print(f"Found food locations: {found_food_locations}")
        
        # If no food is found, return None
        if not found_food_locations:
            return None
        
        # Find the closest food location
        target: tuple[int, int] = min(
            found_food_locations,
            key=lambda target: (self.position_x - target[0])**2 + (self.position_y - target[1])**2
        )
        
        return target


    def eat_food(self) -> None:

            # add the eaten food to its supply
            self.food_supply += 1

            #DEBUGGING
            print(self.food_supply)


    def create_sense_zone(self, radius: int) -> list[tuple[int, int]]:

        # create all the possible coordinates in the radius
        coordinates: list[tuple[int, int]] = [(self.position_x + dx, self.position_y + dy) 
                    for dx in range(-radius, radius + 1) 
                    for dy in range(-radius, radius + 1)]

        return coordinates

