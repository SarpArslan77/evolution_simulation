import random

from general import General
from utility import Shit

class Saprophyte():

    all_saprophytes: list["Saprophyte"] = []

    def __init__(self, general: General):

        self.general = general

        self.position_x, self.position_y = 0, 0
        self.age: int = 0
        self.random_movement: bool = True

        # attributes which are gene dependent
        self.shit_sense_zone: int = random.randint(1, 5)
        self.life_expectancy: int = random.randint(500, 5000)

        # choose what type of saprophyte is it
        self.type: int = 0 

        self.short_term_position_memory: list[tuple[int, int]] = []

    @classmethod
    def generate_saprophyte(cls, shit_positions: list[tuple[int, int]], general: General) -> None: 

        new_cell = Saprophyte(general)
        new_cell.position_x, new_cell.position_y = random.choice(shit_positions)

        # set the type of saprophyte according to its living space(land or water)
        if general.map_matrix[new_cell.position_y][new_cell.position_x] == 6 or \
            general.map_matrix[new_cell.position_y][new_cell.position_x] == 4 or \
            general.map_matrix[new_cell.position_y][new_cell.position_x] == 10:
            new_cell.type = 1
        elif general.map_matrix[new_cell.position_y][new_cell.position_x] == 8 or \
            general.map_matrix[new_cell.position_y][new_cell.position_x] == 9:
            new_cell.type = 2

        new_cell.general.all_cells.append(new_cell)
        new_cell.general.cell_matrix[new_cell.position_y][new_cell.position_x] = "SP"
        new_cell.all_saprophytes.append(new_cell)
        new_cell.short_term_position_memory.append((new_cell.position_x, new_cell.position_y))
        #print((new_cell.position_x, new_cell.position_y))

        # delete the all shits in the zone
        for shit in Shit.all_shits[:]:
            if (shit.position_x, shit.position_y) in shit_positions:
                new_cell.general.utility_matrix[shit.position_y][shit.position_x] = ""
                Shit.all_shits.remove(shit)
        


        return

    @classmethod
    def shit_born_chance(cls, general : General, position_x: int, position_y: int) -> tuple[int, list[tuple[int, int]]]:

        # give the amount of shits in a 3x3 area for a born chance
        possible_zone: list[tuple[int, int]] = [
            (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)
        ]

        shit_count: int = 1
        shit_positions: list[tuple[int, int]] = [(position_x, position_y)]
        for dy, dx in possible_zone:
            if (0 <= position_x+dx <= general.WORLD_WIDTH // 10 - 1) and (0 <= position_y+dy <= general.WORLD_HEIGHT // 10 - 1):
                if general.utility_matrix[position_y+dy][position_x+dx] == "S":
                    shit_positions.append((position_x+dx, position_y+dy))
                    shit_count += 1
        return (shit_count, shit_positions)

    def sense_shit(self, saprophyte: "Saprophyte", coordinates: list[tuple[int, int]]) -> list[tuple[int, int]]:
        found_shit_coordinates: list[tuple[int, int]] = []

        for dx, dy in coordinates:

            if (0 <= dx <= saprophyte.general.WORLD_WIDTH // 10 - 1) and (0 <= dy <= saprophyte.general.WORLD_HEIGHT // 10 - 1):
                if saprophyte.general.utility_matrix[dy][dx] == "S":
                    found_shit_coordinates.append((dx, dy))

        return found_shit_coordinates
    
    def is_movement_possible_saprophyte(self, starting_x: int, starting_y: int, dx: int, dy: int, saprophyte: "Saprophyte") -> bool:

        # check if the new position is not out of bounds
        #   is not occupied
        #   if the biome is walkable for the corresponding type
        if (0 <= starting_x + dx <= saprophyte.general.WORLD_WIDTH // 10 - 1) and (0 <= starting_y + dy <= saprophyte.general.WORLD_HEIGHT // 10 - 1) and \
            not(saprophyte.general.cell_matrix[starting_y + dy][starting_x + dx]):
            if saprophyte.type == 1 and not(saprophyte.general.map_matrix[starting_y + dy][starting_x + dx] == 8 or saprophyte.general.map_matrix[starting_y + dy][starting_x + dx] == 9):
                return True
            elif saprophyte.type == 2 and (saprophyte.general.map_matrix[starting_y + dy][starting_x + dx] == 8 or saprophyte.general.map_matrix[starting_y + dy][starting_x + dx] == 9):
                return True
            
        return False

    def main_loop_saprophyte(self, saprophyte: "Saprophyte") -> None:

        if saprophyte.age >= saprophyte.life_expectancy and \
            random.randint(1, 25000) < (saprophyte.age - saprophyte.life_expectancy):
            
            saprophyte.general.utility_matrix[saprophyte.position_y][saprophyte.position_x] = "G"

            saprophyte.general.cell_matrix[saprophyte.position_y][saprophyte.position_x] = ""

            saprophyte.general.all_cells.remove(saprophyte)
            saprophyte.all_saprophytes.remove(saprophyte)

            return
        else:
            saprophyte.age += 1

        # Get appropriate zone based on sense level
        zone_mapping: dict = {
            1: saprophyte.general.one_to_one_zone,
            2: saprophyte.general.zwo_to_zwo_zone,
            3: saprophyte.general.three_to_three_zone,
            4: saprophyte.general.four_to_four_zone,
            5: saprophyte.general.five_to_five_zone
        }
        zone = zone_mapping.get(saprophyte.shit_sense_zone, None)

        # Filter valid coordinates
        valid_zone: list[tuple[int, int]] = []
        for coord in zone:
            if saprophyte.is_movement_possible_saprophyte(saprophyte.position_x, saprophyte.position_y, coord[1], coord[0], saprophyte):
                valid_zone.append((saprophyte.position_x+coord[1], saprophyte.position_y+coord[0]))

        found_shit_coordinates = saprophyte.sense_shit(saprophyte, valid_zone)
        
        if found_shit_coordinates:
            # Find closest food
            closest_food = min(found_shit_coordinates,
                                key=lambda pos: (pos[0] - saprophyte.position_x)**2 + 
                                            (pos[1] - saprophyte.position_y)**2)
            
            # Calculate direction to move (one step at a time)
            dx = closest_food[0] - saprophyte.position_x
            dy = closest_food[1] - saprophyte.position_y
            
            # Normalize movement to single step
            dx = max(min(dx, 1), -1)
            dy = max(min(dy, 1), -1)

            # Check if movement is possible
            if saprophyte.is_movement_possible_saprophyte(
                saprophyte.position_x, saprophyte.position_y, dx, dy, saprophyte):

                # Clear old position
                saprophyte.general.cell_matrix[saprophyte.position_y][saprophyte.position_x] = ""

                saprophyte.position_x += dx
                saprophyte.position_y += dy
                saprophyte.random_movement = False

        # check whether the cell is stuck in a movement loop, if so clear it
        if found_shit_coordinates and (saprophyte.short_term_position_memory.count((saprophyte.position_x, saprophyte.position_y)) == 5):
                saprophyte.short_term_position_memory.clear()

        # Random movement if no food found or movement not possible
        if saprophyte.random_movement:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(directions)  # Shuffle for more random behavior
            
            for dx, dy in directions:
                if saprophyte.is_movement_possible_saprophyte(
                    saprophyte.position_x, saprophyte.position_y, dx, dy, saprophyte):

                    # Clear old position
                    saprophyte.general.cell_matrix[saprophyte.position_y][saprophyte.position_x] = ""

                    saprophyte.position_x += dx
                    saprophyte.position_y += dy
                    break

        # Reset random movement flag
        saprophyte.random_movement = True

        # check for food
        if saprophyte.general.utility_matrix[saprophyte.position_y][saprophyte.position_x] == "S":
            saprophyte.age -= min(saprophyte.age, 250)
            saprophyte.general.utility_matrix[saprophyte.position_y][saprophyte.position_x] = ""

        saprophyte.general.cell_matrix[saprophyte.position_y][saprophyte.position_x] = "SP"
        saprophyte.short_term_position_memory.append((saprophyte.position_x, saprophyte.position_y))














        
