import random

from general import General


#TODO shitting mechanic is broken, it shits when it eats
#TODO cell can get stuck when there are occupying cells in the distance and it senses a food after those occupying cells (blocking)

class Predator_Cell():

    predator_cell_list: list = []

    def __init__(self, general: General):
        self.position_x, self.position_y = 0, 0
        self.age = 0 
        self.general = general
        self.random_movement: bool = True

        # attributes which are not gene-dependent
        self.food_supply: int = 50  # 1 = hungry, 100 = full

        # attributes which are gene-dependent for each cell 
        self.food_sense_zone: int = random.randint(1, 5)  # 1 = smalles, 5 = biggest
        self.life_expectancy: int = random.randint(500, 25000) # 500 = shortest, 25000 = longest
        self.produce_amount: int = random.randint(1, 8) # 1 = worst, 8 = best
    
        self.mutation_limits: dict = {
            "food_sense_zone" : (1, 5),
            "life_expectancy" : (500, 25000),
            "produce_amount" : (1, 8)
        }

    def random_move_cells(self, predator_cell: "Predator_Cell") -> None:
        # Clear old position
        predator_cell.general.cell_matrix[predator_cell.position_y][predator_cell.position_x] = ""

        # get old and check whether the cell is RIP
        #   chance of its dying increase when the cell's age pasts its life expectancy
        if predator_cell.age >= predator_cell.life_expectancy and \
            random.randint(1, 25000) < (predator_cell.age - predator_cell.life_expectancy):

            # set the dead position as a shit
            predator_cell.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] = "S"

            # remove the cell from existence :(
            predator_cell.general.all_cells.remove(predator_cell)
            predator_cell.predator_cell_list.remove(predator_cell)

            return
        else:
            predator_cell.get_old(predator_cell)

        # check whether the cell wants to reproduce
        if predator_cell.food_supply > 90:
            predator_cell.reproduce(predator_cell)

        # Only look for food if not full
        if predator_cell.food_supply < 100:  # Changed from 100 to more reasonable value
            # Get appropriate zone based on sense level
            zone_mapping = {
                1: predator_cell.general.one_to_one_zone,
                2: predator_cell.general.zwo_to_zwo_zone,
                3: predator_cell.general.three_to_three_zone,
                4: predator_cell.general.four_to_four_zone,
                5: predator_cell.general.five_to_five_zone
            }
            zone = zone_mapping.get(predator_cell.food_sense_zone, predator_cell.general.three_to_three_zone)

            # Filter valid coordinates
            valid_zone = [coord for coord in zone if 
                         predator_cell.is_movement_possible_predatorCell(
                             predator_cell.position_x + coord[1],  # Swapped to match matrix coordinates
                             predator_cell.position_y + coord[0],
                             0, 0,
                             predator_cell)]  # Check if position is valid, not movement

            # Look for food in valid coordinates
            found_food_coordinates = predator_cell.sense_food(valid_zone, predator_cell)
            
            if found_food_coordinates:
                # Find closest food
                closest_food = min(found_food_coordinates,
                                 key=lambda pos: (pos[0] - predator_cell.position_x)**2 + 
                                               (pos[1] - predator_cell.position_y)**2)
                
                # Calculate direction to move (one step at a time)
                dx = closest_food[0] - predator_cell.position_x
                dy = closest_food[1] - predator_cell.position_y
                
                # Normalize movement to single step
                dx = max(min(dx, 1), -1)
                dy = max(min(dy, 1), -1)

                # Check if movement is possible
                if predator_cell.is_movement_possible_predatorCell(
                    predator_cell.position_x, predator_cell.position_y, dx, dy, predator_cell):
                    predator_cell.position_x += dx
                    predator_cell.position_y += dy
                    predator_cell.random_movement = False

        # Random movement if no food found or movement not possible
        if predator_cell.random_movement:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(directions)  # Shuffle for more random behavior
            
            for dx, dy in directions:
                if predator_cell.is_movement_possible_predatorCell(
                    predator_cell.position_x, predator_cell.position_y, dx, dy, predator_cell):
                    predator_cell.position_x += dx
                    predator_cell.position_y += dy
                    break

        # Reset random movement flag
        predator_cell.random_movement = True

        # Check for food at new position and eat if found
        if (predator_cell.food_supply < 100 and  # Changed from 100
            predator_cell.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] == "F"):
            predator_cell.eat_food(predator_cell)
            print(predator_cell.food_supply)
            predator_cell.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] = ""

        # check if the cell wants to shit
        if predator_cell.food_supply > 50 and (random.randint(1, 100000) < 10**(predator_cell.food_supply-50)):
            predator_cell.shit(predator_cell)


        # Mark new position
        predator_cell.general.cell_matrix[predator_cell.position_y][predator_cell.position_x] = "C"

    def generate_predatorCells(self) -> None:
        for _ in range(self.general.starting_generation_predator_cell_count):
            x_position, y_position = self.random_position_predatorCell()
            new_cell = Predator_Cell(self.general)
            new_cell.position_x, new_cell.position_y = x_position, y_position

            self.general.all_cells.append(new_cell)
            self.general.cell_matrix[y_position][x_position] = "C"
            self.predator_cell_list.append(new_cell)

    def eat_food(self, predator_cell: "Predator_Cell") -> None:
        if predator_cell.food_supply < 100:  # Changed from 100
            predator_cell.food_supply += 5

    def sense_food(self, coordinates: list[tuple[int, int]], predator_cell: "Predator_Cell") -> list[tuple[int, int]]:
        found_food_coordinates = []
        
        for dy, dx in coordinates:  # Note: coordinates are (y, x) in the zone definitions
            check_x = predator_cell.position_x + dx
            check_y = predator_cell.position_y + dy
            
            # Check if position is within bounds
            if (0 <= check_y < len(predator_cell.general.utility_matrix) and
                0 <= check_x < len(predator_cell.general.utility_matrix[0])):
                # Check if food exists at this position
                if predator_cell.general.utility_matrix[check_y][check_x] == "F":
                    found_food_coordinates.append((check_x, check_y))
        
        return found_food_coordinates
    
    def shit(self, predator_cell: "Predator_Cell") -> None:

        # empty the stomach
        predator_cell.food_supply -= 5

        # mark the shitted positions as "S"
        predator_cell.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] = "S"

    def random_position_predatorCell(self) -> tuple[int, int]:

        # loop continues until an unoccupied coordinates are generated
        while True:

            ###print( self.WORLD_WIDTH//10-1, self.WORLD_HEIGHT//10-1)
            x_position: int = random.randint(0, self.general.WORLD_WIDTH//10-1)
            y_position: int = random.randint(0, self.general.WORLD_HEIGHT//10-1)

            if not(self.general.cell_matrix[y_position][x_position]) and \
                not(self.general.map_matrix[y_position][x_position] == 8 or self.general.map_matrix[y_position][x_position] == 9):
                break

        return (x_position, y_position)
    
    def is_movement_possible_predatorCell(self, starting_x: int, starting_y: int, dx: int, dy: int, predator_cell: "Predator_Cell") -> bool:

        # check if the new position is not out of bounds
        #   is not occupied
        #   if the biome is walkable(aka not water)
        if (0 <= starting_x + dx <= predator_cell.general.WORLD_WIDTH // 10 - 1) and (0 <= starting_y + dy <= predator_cell.general.WORLD_HEIGHT // 10 - 1) and \
            not(predator_cell.general.cell_matrix[starting_y + dy][starting_x + dx]) and \
            not(predator_cell.general.map_matrix[starting_y + dy][starting_x + dx] == 8 or predator_cell.general.map_matrix[starting_y + dy][starting_x + dx] == 9):
            return True
        return False

    def get_old(self, predator_cell: "Predator_Cell") -> None:

        predator_cell.age += 1

    def reproduce(self, predator_cell: "Predator_Cell") -> None:

        # transfer the one_to_one_zone to neighboring_cells and shuffle it
        neighboring_cells: list[tuple[int, int]] = predator_cell.general.one_to_one_zone
        random.shuffle(neighboring_cells)

        # go over all the possible locations, until one works then return
        for _ in range(len(predator_cell.general.one_to_one_zone)):

            # check the first element of the shuffled list
            dx, dy = neighboring_cells[0]
            

            if predator_cell.is_movement_possible_predatorCell(predator_cell.position_x, predator_cell.position_y, dx, dy, predator_cell):

                # if the dx and dy valid move delete it from the temporary list
                del neighboring_cells[0]

                # create a child with the tested positions
                child_cell = Predator_Cell(self.general)
                child_cell.position_x, child_cell.position_y = predator_cell.position_x+dx, predator_cell.position_y+dy

                # inheriting the attributes from the parent cell

                # add them to matrixes and cells
                predator_cell.general.all_cells.append(child_cell)
                predator_cell.general.cell_matrix[predator_cell.position_y+dy][predator_cell.position_x+dx] = "C"
                predator_cell.predator_cell_list.append(child_cell)
            
            # check whether the produce_amount is reached
            if predator_cell.produce_amount == (len(predator_cell.general.one_to_one_zone)-len(neighboring_cells)):
                return

    def mutate(self, predator_cell: "Predator_Cell", attribute: str) -> int:

        minimum, maximum = predator_cell.mutation_limits[attribute]

        pass
            










