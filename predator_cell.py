import random

from general import General

class Predator_Cell():

    predator_cell_list: list = []

    def __init__(self, general: General):
        self.position_x, self.position_y = 0, 0
        self.general = general
        self.random_movement: bool = True

        # attributes which are gene-dependent for each cell 
        self.food_supply: int = 5  # 1 = hungry, 10 = full
        self.food_sense_zone: int = 3  # 1 = worst, 5 = best
    
    def random_move_cells(self, predator_cell: "Predator_Cell") -> None:
        # Clear old position
        predator_cell.general.cell_matrix[predator_cell.position_y][predator_cell.position_x] = ""

        # Only look for food if not full
        if predator_cell.food_supply < 10:  # Changed from 100 to more reasonable value
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
                         predator_cell.general.is_movement_possible(
                             predator_cell.position_x + coord[1],  # Swapped to match matrix coordinates
                             predator_cell.position_y + coord[0],
                             0, 0)]  # Check if position is valid, not movement

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
                if predator_cell.general.is_movement_possible(
                    predator_cell.position_x, predator_cell.position_y, dx, dy):
                    predator_cell.position_x += dx
                    predator_cell.position_y += dy
                    predator_cell.random_movement = False

        # Random movement if no food found or movement not possible
        if predator_cell.random_movement:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(directions)  # Shuffle for more random behavior
            
            for dx, dy in directions:
                if predator_cell.general.is_movement_possible(
                    predator_cell.position_x, predator_cell.position_y, dx, dy):
                    predator_cell.position_x += dx
                    predator_cell.position_y += dy
                    break

        # Reset random movement flag
        predator_cell.random_movement = True

        # Check for food at new position and eat if found
        if (predator_cell.food_supply < 10 and  # Changed from 100
            predator_cell.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] == "F"):
            predator_cell.eat_food(predator_cell)
            predator_cell.general.utility_matrix[predator_cell.position_y][predator_cell.position_x] = ""

        # Mark new position
        predator_cell.general.cell_matrix[predator_cell.position_y][predator_cell.position_x] = "C"

    def generate_predatorCells(self) -> None:
        for _ in range(self.general.starting_generation_predator_cell_count):
            x_position, y_position = self.general.random_position()
            new_cell = Predator_Cell(self.general)
            new_cell.position_x, new_cell.position_y = x_position, y_position

            self.general.all_cells.append(new_cell)
            self.general.cell_matrix[y_position][x_position] = "C"
            self.predator_cell_list.append(new_cell)
            self.general.cell_occupied_positions.append((x_position, y_position))

    def eat_food(self, predator_cell: "Predator_Cell") -> None:
        if predator_cell.food_supply < 10:  # Changed from 100
            predator_cell.food_supply += 1

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
