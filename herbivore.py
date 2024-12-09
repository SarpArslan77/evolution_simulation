import random

from general import General
from utility import Shit


class Herbivore(): 

    herbivore_list: list["Herbivore"] = []

    def __init__(self, general: General, shit_ins: Shit):
        self.position_x, self.position_y = 0, 0
        self.age: int = 0 
        self.general = general
        self.shit_ins = shit_ins
        self.random_movement: bool = True

        # attributes which are not gene-dependent
        self.food_supply: int = 20  # 1 = hungry, 100 = full

        # attributes which are gene-dependent for each cell 
        self.producer_cell_sense_zone: int = random.randint(1, 5)  # 1 = smallest, 5 = biggest
        self.life_expectancy: int = random.randint(500, 5000) # 500 = shortest, 25000 = longest
        self.produce_amount: int = random.randint(1, 8) # 1 = worst, 8 = best
    
        self.mutation_limits: dict = {
            "producer_cell_sense_zone" : (1, 5),
            "life_expectancy" : (500, 5000),
            "produce_amount" : (1, 8)
        }

        self.mutation_amounts: dict = {
            "producer_cell_sense_zone" : 1,
            "life_expectancy" : 500,
            "produce_amount" : 1
        }

        self.short_term_position_memory: list[tuple[int, int]] = []

    def main_loop_herbivore(self, herbivore: "Herbivore") -> None:

        # get old and check whether the cell is RIP
        #   chance of its dying increase when the cell's age pasts its life expectancy
        if herbivore.age >= herbivore.life_expectancy and \
            random.randint(1, 25000) < (herbivore.age - herbivore.life_expectancy):

            # set the dead position as a shit
            herbivore.general.utility_matrix[herbivore.position_y][herbivore.position_x] = "S"

            # set the new position as dead
            herbivore.general.cell_matrix[herbivore.position_y][herbivore.position_x] = ""

            # remove the cell from existence :(
            herbivore.general.all_cells.remove(herbivore)
            herbivore.herbivore_list.remove(herbivore)

            return
        else:
            herbivore.age += 1

        # check whether the cell wants to reproduce
        if herbivore.food_supply > 90:
            herbivore.reproduce(herbivore)

        # Only look for food if not full
        if herbivore.food_supply < 100:  # Changed from 100 to more reasonable value
            # Get appropriate zone based on sense level
            zone_mapping: dict = {
                1: herbivore.general.one_to_one_zone,
                2: herbivore.general.zwo_to_zwo_zone,
                3: herbivore.general.three_to_three_zone,
                4: herbivore.general.four_to_four_zone,
                5: herbivore.general.five_to_five_zone
            }
            zone = zone_mapping.get(herbivore.producer_cell_sense_zone, None)

            # Filter valid coordinates
            valid_zone = [coord for coord in zone if 
                         herbivore.is_movement_possible_herbivore(
                             herbivore.position_x + coord[1],  # Swapped to match matrix coordinates
                             herbivore.position_y + coord[0],
                             0, 0,
                             herbivore)]  # Check if position is valid, not movement

            # Look for food in valid coordinates
            found_food_coordinates = herbivore.sense_producerCell(valid_zone, herbivore)
            
            if found_food_coordinates:
                # Find closest food
                closest_food = min(found_food_coordinates,
                                 key=lambda pos: (pos[0] - herbivore.position_x)**2 + 
                                               (pos[1] - herbivore.position_y)**2)
                
                # Calculate direction to move (one step at a time)
                dx = closest_food[0] - herbivore.position_x
                dy = closest_food[1] - herbivore.position_y
                
                # Normalize movement to single step
                dx = max(min(dx, 1), -1)
                dy = max(min(dy, 1), -1)

                # Check if movement is possible
                if herbivore.is_movement_possible_herbivore(
                    herbivore.position_x, herbivore.position_y, dx, dy, herbivore):

                    # Clear old position
                    herbivore.general.cell_matrix[herbivore.position_y][herbivore.position_x] = ""

                    herbivore.position_x += dx
                    herbivore.position_y += dy
                    herbivore.random_movement = False

        # check whether the cell is stuck in a movement loop, if so clear it
        if found_food_coordinates and (herbivore.short_term_position_memory.count((herbivore.position_x, herbivore.position_y)) == 5):
                    herbivore.short_term_position_memory.clear()

        # Random movement if no food found or movement not possible
        if herbivore.random_movement:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(directions)  # Shuffle for more random behavior
            
            for dx, dy in directions:
                if herbivore.is_movement_possible_herbivore(
                    herbivore.position_x, herbivore.position_y, dx, dy, herbivore):

                    # Clear old position
                    herbivore.general.cell_matrix[herbivore.position_y][herbivore.position_x] = ""

                    herbivore.position_x += dx
                    herbivore.position_y += dy
                    break

        # Reset random movement flag
        herbivore.random_movement = True

        # Check for food at new position and eat if found
        # Filter valid coordinates
        valid_zone_producer_cell: list[tuple[int, int]] = []
        for coord in [(1, 1), (1, 0), (0, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (-1, 1)]:
            if (0 <= herbivore.position_x + dx <= herbivore.general.WORLD_WIDTH // 10 - 1) and (0 <= herbivore.position_y + dy <= herbivore.general.WORLD_HEIGHT // 10 - 1) and \
                not(herbivore.general.map_matrix[herbivore.position_y + dy][herbivore.position_x + dx] == 8 or herbivore.general.map_matrix[herbivore.position_y + dy][herbivore.position_x + dx] == 9):
                
                valid_zone_producer_cell.append((herbivore.position_x+dx, herbivore.position_y+dy))
        
        random.shuffle(valid_zone_producer_cell)
        if herbivore.food_supply < 10000000000:
            for dx, dy in valid_zone_producer_cell:
                if herbivore.general.cell_matrix[dy][dx] == "P":
                    herbivore.eat_producerCell(herbivore)
                    # Remove the matching cell object from the list
                    herbivore.general.all_cells = [
                        producer_cell for producer_cell in herbivore.general.all_cells
                        if not (producer_cell.position_x == dx and producer_cell.position_y == dy)
                    ]
                    herbivore.general.cell_matrix[herbivore.position_y][herbivore.position_x] = ""

                    # mark new position and add it to its position memory
                    herbivore.general.cell_matrix[herbivore.position_y][herbivore.position_x] = "H"
                    herbivore.short_term_position_memory.append((herbivore.position_x, herbivore.position_y))

                    return

        # check if the cell wants to shit
        if herbivore.food_supply > 50 and (random.randint(1, pow(10, 50)) < 10**(herbivore.food_supply-50)):
            herbivore.shit(herbivore)

        # mark new position and add it to its position memory
        herbivore.general.cell_matrix[herbivore.position_y][herbivore.position_x] = "H"
        herbivore.short_term_position_memory.append((herbivore.position_x, herbivore.position_y))

    def generate_herbivore(self) -> None:
        for _ in range(self.general.starting_generation_herbivore_count):
            x_position, y_position = self.random_position_herbivore()
            new_cell = Herbivore(self.general, self.shit_ins)
            new_cell.position_x, new_cell.position_y = x_position, y_position

            self.general.all_cells.append(new_cell)
            self.general.cell_matrix[y_position][x_position] = "H"
            self.herbivore_list.append(new_cell)
            self.short_term_position_memory.append((x_position, y_position))

    def eat_producerCell(self, herbivore: "Herbivore") -> None:
        if herbivore.food_supply < 100:  # Changed from 100
            herbivore.food_supply += 5

    def sense_producerCell(self, coordinates: list[tuple[int, int]], herbivore: "Herbivore") -> list[tuple[int, int]]:
        found_producerCell_coordinates : list[tuple[int, int]] = []
        
        for dy, dx in coordinates:  # Note: coordinates are (y, x) in the zone definitions
            check_x = herbivore.position_x + dx
            check_y = herbivore.position_y + dy
            
            # Check if position is within bounds
            if (0 <= check_y < len(herbivore.general.utility_matrix) and
                0 <= check_x < len(herbivore.general.utility_matrix[0])):
                # Check if food exists at this position
                if herbivore.general.cell_matrix[check_y][check_x] == "P":
                    found_producerCell_coordinates.append((check_x, check_y))
        print(found_producerCell_coordinates)
        return found_producerCell_coordinates
    
    def shit(self, herbivore: "Herbivore") -> None:

        # empty the stomach
        herbivore.food_supply -= 50

        # create a shit utility
        new_shit = Shit(self.general.colors["BLACK"], "S")
        new_shit.position_x, new_shit.position_y = herbivore.position_x, herbivore.position_y
        herbivore.shit_ins.all_shit_list.append(new_shit)

        # mark the shitted positions as "S"
        herbivore.general.utility_matrix[new_shit.position_y][new_shit.position_x] = new_shit.symbol

    def random_position_herbivore(self) -> tuple[int, int]:

        # loop continues until an unoccupied coordinates are generated
        while True:

            ###print( self.WORLD_WIDTH//10-1, self.WORLD_HEIGHT//10-1)
            x_position: int = random.randint(0, self.general.WORLD_WIDTH//10-1)
            y_position: int = random.randint(0, self.general.WORLD_HEIGHT//10-1)

            if not(self.general.cell_matrix[y_position][x_position]) and \
                not(self.general.map_matrix[y_position][x_position] == 8 or self.general.map_matrix[y_position][x_position] == 9):
                break

        return (x_position, y_position)
    
    def is_movement_possible_herbivore(self, starting_x: int, starting_y: int, dx: int, dy: int, herbivore: "Herbivore") -> bool:

        # check if the new position is not out of bounds
        #   is not occupied
        #   if the biome is walkable(aka not water)
        if (0 <= starting_x + dx <= herbivore.general.WORLD_WIDTH // 10 - 1) and (0 <= starting_y + dy <= herbivore.general.WORLD_HEIGHT // 10 - 1) and \
            not(herbivore.general.cell_matrix[starting_y + dy][starting_x + dx]) and \
            not(herbivore.general.map_matrix[starting_y + dy][starting_x + dx] == 8 or herbivore.general.map_matrix[starting_y + dy][starting_x + dx] == 9):
            return True
        return False

    def reproduce(self, herbivore: "Herbivore") -> None:
        # Determine number of children based on produce_amount
        num_children = herbivore.produce_amount

        # Create children
        for _ in range(num_children):
            # Create a new herbivore
            new_cell = Herbivore(herbivore.general, self.shit_ins)

            # Find a nearby empty position to place the child
            possible_positions = [
                (herbivore.position_x + dx, herbivore.position_y + dy)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
            ]

            # Shuffle positions to add randomness
            random.shuffle(possible_positions)

            # Find a valid position for the child
            for x, y in possible_positions:
                if herbivore.is_movement_possible_herbivore(x, y, 0, 0, herbivore):

                    new_cell.position_x, new_cell.position_y = x, y
                    #inhabit the attributes
                    new_cell.producer_cell_sense_zone = herbivore.producer_cell_sense_zone
                    new_cell.life_expectancy = herbivore.life_expectancy
                    new_cell.produce_amount = herbivore.produce_amount
                    
                    # Add the new cell to relevant lists and matrix
                    herbivore.general.all_cells.append(new_cell)
                    herbivore.herbivore_list.append(new_cell)
                    herbivore.general.cell_matrix[y][x] = "H"
                    herbivore.short_term_position_memory.append((x, y))

                    # Potentially mutate the child's attributes
                    for attr in ["producer_cell_sense_zone", "life_expectancy", "produce_amount"]:
                        setattr(new_cell, attr, herbivore.mutate(new_cell, attr))
                        
                    break

        # Reduce food supply after reproduction
        herbivore.food_supply -= 70

    def mutate(self, herbivore: "Herbivore", attribute: str) -> int:

        # Get the current value of the attribute
        current_value = getattr(herbivore, attribute)
        
        # Get the minimum and maximum limits for the attribute
        minimum, maximum = herbivore.mutation_limits[attribute]
        
        # Mutation probability and magnitude
        mutation_chance = 1  # 1% chance of mutation
        mutation_magnitude = herbivore.mutation_amounts[attribute]
        
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
            






