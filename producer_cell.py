from general import General

import random

#TODO: add life expectancy
#TODO: create a function for the zone mapping general
#! reproduction is not working

class Producer_Cell():

    producer_cell_list: list["Producer_Cell"] = []

    def __init__(self, general: General):
        self.position_x, self.position_y = 0, 0
        self.general = general

        # attributes which are gene-dependent for each cell 
        #   if a int is assigned, which means it is in test section and does not get inherited from its parent cell

        # 1 = worst, 100 = best
        #   it will be divided by 1000, for example if it is 50 then it is going to be %0.05
        self.food_production_speed: int = random.randint(1, 100)

        # 1 = worst, 5 = best
        self.food_production_zone: int = random.randint(1, 5)

        # 1 = worst, 8 = best
        self.produce_amount: int = 8

        # 1 = worst, 5 = best
        self.shit_sense_zone: int = random.randint(1, 5)

        self.mutation_limits: dict = {
            "food_production_speed" : (1, 10),
            "food_production_zone" : (1, 5),
            "produce_amount" : (1, 4),
            "shit_sense_zone" : (1, 5)
        }

        self.mutation_amount: dict = {
            "food_production_speed" : 1,
            "food_production_zone" : 1,
            "produce_amount" : 1,
            "shit_sense_zone" : 1
        }

    def main_loop_producerCell(self, producer_cell: "Producer_Cell"):

        # first check whether the cell wants to reproduce, (zone_mapping add shit condition, this many available)
        # map the possible zones
        zone_mapping: dict = {
            1: producer_cell.general.one_to_one_zone,
            2: producer_cell.general.zwo_to_zwo_zone,
            3: producer_cell.general.three_to_three_zone,
            4: producer_cell.general.four_to_four_zone,
            5: producer_cell.general.five_to_five_zone
        }
        zone = zone_mapping.get(producer_cell.shit_sense_zone, None)

        # zones that have shits increase the chance of reproduction
        shit_count: int = 0
        for x, y in zone:
            if (0 <= producer_cell.position_x + x <= producer_cell.general.WORLD_WIDTH // 10 - 1) and (0 <= producer_cell.position_y + y <= producer_cell.general.WORLD_HEIGHT // 10 - 1):
                if producer_cell.general.utility_matrix[producer_cell.position_y+y][producer_cell.position_x+x] == "S":
                    shit_count += 1
        reproduction_possibility: int = 0.027 * shit_count

        if random.random() < reproduction_possibility:
            print("bruh")
            producer_cell.reproduce(producer_cell)

        producer_cell.produce_food(producer_cell)


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

        # create the amount of children according to produce_amount
        num_children = producer_cell.produce_amount

        for _ in range(num_children):

            new_cell = Producer_Cell(producer_cell.general)

            zone = producer_cell.general.one_to_one_zone
            random.shuffle(zone)

            # check whether they are available
            for dx, dy in zone:
                
                if producer_cell.is_available(producer_cell.position_x, producer_cell.position_y, dx, dy, producer_cell):
                    new_cell.position_x += dx
                    new_cell.position_y += dy
                    new_cell.food_production_speed = producer_cell.food_production_speed
                    new_cell.food_production_zone = producer_cell.food_production_zone
                    new_cell.produce_amount = producer_cell.produce_amount
                    new_cell.shit_sense_zone = producer_cell.shit_sense_zone


                    for attr in ["food_production_speed", "food_production_zone", "produce_amount", "shit_sense_zone"]:
                        setattr(new_cell, attr, producer_cell.mutate(new_cell, attr))

                    producer_cell.general.all_cells.append(new_cell)
                    producer_cell.producer_cell_list.append(new_cell)
                    producer_cell.general.cell_matrix[new_cell.position_y][new_cell.position_x] = "P"
                    print("new_born")
                    break
        
        # map the possible zones
        zone_mapping: dict = {
            1: producer_cell.general.one_to_one_zone,
            2: producer_cell.general.zwo_to_zwo_zone,
            3: producer_cell.general.three_to_three_zone,
            4: producer_cell.general.four_to_four_zone,
            5: producer_cell.general.five_to_five_zone
        }
        zone = zone_mapping.get(producer_cell.shit_sense_zone, None)

        # zones that have shits(necessary for the reproduction) are gone, so kinda used
        for x, y in zone:
            if producer_cell.general.utility_matrix[producer_cell.position_y+y][producer_cell.position_x+x] == "S":
                producer_cell.general.utility_matrix[producer_cell.position_y+y][producer_cell.position_x+x] = ""

        print("REPRODUCED")

    def is_available(self, starting_x: int, starting_y: int, dx: int, dy: int, producer_cell: "Producer_Cell") -> bool:

        # check if the new position is not out of bounds
        #   is not occupied
        #   is suitable for producer cells(aka water or plains)
        if (0 <= starting_x + dx <= producer_cell.general.WORLD_WIDTH // 10 - 1) and (0 <= starting_y + dy <= producer_cell.general.WORLD_HEIGHT // 10 - 1) and \
            not(producer_cell.general.cell_matrix[starting_y + dy][starting_x + dx]) and \
            (producer_cell.general.map_matrix[starting_y + dy][starting_x + dx] == 8 or producer_cell.general.map_matrix[starting_y + dy][starting_x + dx] == 6):
            
            return True
        
        return False

    def mutate(self, producer_cell: "Producer_Cell", attribute: str) -> int:
        # Get the current value of the attribute
        current_value = getattr(producer_cell, attribute)
        
        # Get the minimum and maximum limits for the attribute
        minimum, maximum = producer_cell.mutation_limits[attribute]
        
        # Mutation probability and magnitude
        mutation_chance = 1  # 1% chance of mutation
        mutation_magnitude = producer_cell.mutation_amount[attribute]
        
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







