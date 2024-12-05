import random

from general import General


class Predator_Cell():

    predator_cell_list: list["Predator_Cell"] = []

    def __init__(self, general: General):
        self.position_x, self.position_y = 0, 0
        self.age: int = 0 
        self.general = general
        self.random_movement: bool = True

        # attributes which are not gene-dependent
        self.food_supply: int = 20  # 1 = hungry, 100 = full

        # attributes which are gene-dependent for each cell 
        self.food_sense_zone: int = random.randint(1, 5)  # 1 = smallest, 5 = biggest
        self.life_expectancy: int = random.randint(500, 5000) # 500 = shortest, 25000 = longest
        self.produce_amount: int = random.randint(1, 8) # 1 = worst, 8 = best
    
        self.mutation_limits: dict = {
            "food_sense_zone" : (1, 5),
            "life_expectancy" : (500, 5000),
            "produce_amount" : (1, 8)
        }

        self.mutation_amounts: dict = {
            "food_sense_zone" : 1,
            "life_expectancy" : 500,
            "produce_amount" : 1
        }

        self.short_term_position_memory: list[tuple[int, int]] = []

    def main_loop_predatorCell(self, predator_cell: "Predator_Cell") -> None:

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
            predator_cell.age += 1

        # check whether the cell wants to reproduce
        if predator_cell.food_supply > 90:
            predator_cell.reproduce(predator_cell)

        # Only look for food if not full
        if predator_cell.food_supply < 100:  # Changed from 100 to more reasonable value
            # Get appropriate zone based on sense level
            zone_mapping: dict = {
                1: predator_cell.general.one_to_one_zone,
                2: predator_cell.general.zwo_to_zwo_zone,
                3: predator_cell.general.three_to_three_zone,
                4: predator_cell.general.four_to_four_zone,
                5: predator_cell.general.five_to_five_zone
            }
            zone = zone_mapping.get(predator_cell.food_sense_zone, None)

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

                    # Clear old position
                    predator_cell.general.cell_matrix[predator_cell.position_y][predator_cell.position_x] = ""

                    predator_cell.position_x += dx
                    predator_cell.position_y += dy
                    predator_cell.random_movement = False

        # check whether the cell is stuck in a movement loop, if so clear it
        if found_food_coordinates and (predator_cell.short_term_position_memory.count((predator_cell.position_x, predator_cell.position_y)) == 5):
                    predator_cell.short_term_position_memory.clear()

        # Random movement if no food found or movement not possible
        if predator_cell.random_movement:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(directions)  # Shuffle for more random behavior
            
            for dx, dy in directions:
                if predator_cell.is_movement_possible_predatorCell(
                    predator_cell.position_x, predator_cell.position_y, dx, dy, predator_cell):

                    # Clear old position
                    predator_cell.general.cell_matrix[predator_cell.position_y][predator_cell.position_x] = ""

                    predator_cell.position_x += dx
                    predator_cell.position_y += dy
                    break

        # Reset random movement flag
        predator_cell.random_movement = True

        # Check for food at new position and eat if found
        if (predator_cell.food_supply < 100 and  # Changed from 100
            predator_cell.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] == "F"):
            predator_cell.eat_food(predator_cell)
            ###print(predator_cell.food_supply)
            predator_cell.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] = ""

        # check if the cell wants to shit
        if predator_cell.food_supply > 50 and (random.randint(1, pow(10, 50)) < 10**(predator_cell.food_supply-50)):
            predator_cell.shit(predator_cell)


        # mark new position and add it to its position memory
        predator_cell.general.cell_matrix[predator_cell.position_y][predator_cell.position_x] = "C"
        predator_cell.short_term_position_memory.append((predator_cell.position_x, predator_cell.position_y))

    def generate_predatorCells(self) -> None:
        for _ in range(self.general.starting_generation_predator_cell_count):
            x_position, y_position = self.random_position_predatorCell()
            new_cell = Predator_Cell(self.general)
            new_cell.position_x, new_cell.position_y = x_position, y_position

            self.general.all_cells.append(new_cell)
            self.general.cell_matrix[y_position][x_position] = "C"
            self.predator_cell_list.append(new_cell)
            self.short_term_position_memory.append((x_position, y_position))

    def eat_food(self, predator_cell: "Predator_Cell") -> None:
        if predator_cell.food_supply < 100:  # Changed from 100
            predator_cell.food_supply += 5

    def sense_food(self, coordinates: list[tuple[int, int]], predator_cell: "Predator_Cell") -> list[tuple[int, int]]:
        found_food_coordinates : list[tuple[int, int]] = []
        
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
        predator_cell.food_supply -= 50

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

    def reproduce(self, predator_cell: "Predator_Cell") -> None:
        # Determine number of children based on produce_amount
        num_children = predator_cell.produce_amount

        # Create children
        for _ in range(num_children):
            # Create a new predator cell
            new_cell = Predator_Cell(predator_cell.general)

            # Find a nearby empty position to place the child
            possible_positions = [
                (predator_cell.position_x + dx, predator_cell.position_y + dy)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
            ]

            # Shuffle positions to add randomness
            random.shuffle(possible_positions)

            # Find a valid position for the child
            for x, y in possible_positions:
                if predator_cell.is_movement_possible_predatorCell(x, y, 0, 0, predator_cell):

                    new_cell.position_x, new_cell.position_y = x, y
                    #inhabit the attributes
                    new_cell.food_sense_zone = predator_cell.food_sense_zone
                    new_cell.life_expectancy = predator_cell.life_expectancy
                    new_cell.produce_amount = predator_cell.produce_amount
                    
                    # Add the new cell to relevant lists and matrix
                    predator_cell.general.all_cells.append(new_cell)
                    predator_cell.predator_cell_list.append(new_cell)
                    predator_cell.general.cell_matrix[y][x] = "C"
                    predator_cell.short_term_position_memory.append((x, y))

                    # Potentially mutate the child's attributes
                    for attr in ["food_sense_zone", "life_expectancy", "produce_amount"]:
                        setattr(new_cell, attr, predator_cell.mutate(new_cell, attr))
                        
                    break

        # Reduce food supply after reproduction
        predator_cell.food_supply -= 70

    def mutate(self, predator_cell: "Predator_Cell", attribute: str) -> int:

        # Get the current value of the attribute
        current_value = getattr(predator_cell, attribute)
        
        # Get the minimum and maximum limits for the attribute
        minimum, maximum = predator_cell.mutation_limits[attribute]
        
        # Mutation probability and magnitude
        mutation_chance = 1  # 1% chance of mutation
        mutation_magnitude = predator_cell.mutation_amounts[attribute]
        
        # Randomly decide whether to mutate
        if random.randint(1, 100) < mutation_chance:
            # Randomly choose to increase or decrease
            if random.random() < 0.5:
                # Increase value
                mutated_value = current_value + random.randint(0, mutation_magnitude)
            else:
                # Decrease value
                mutated_value = current_value - random.randint(0, mutation_magnitude)
            
            # Ensure the mutated value stays within the defined limits
            mutated_value = max(minimum, min(maximum, mutated_value))
            
            return mutated_value
        
        # If no mutation occurs, return the original value
        return current_value
            






