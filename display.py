
import pygame
import sys
import random

from depot import map_matrix
from general import General

from predator_cell import Predator_Cell
from producer_cell import Producer_Cell
from herbivore import Herbivore

from saprophyte import Saprophyte

from utility import Shit, Food



#? correct the type hints for each function/variable, everything should be yellow
#TODO saprophytes sometimes go through producer_cells
#TODO   i suppose because the shit is for a very brief of time in the producer cells and therefore overrides the occupied condition, to move towards the food
#! list already does not ahave the cell, when it should be deleted according to old age
#!  -> most probably, when they got eaten, sth occurs, idk man


class Display():
    def __init__(self, general: General, predator_cell: Predator_Cell, producer_cell: Producer_Cell, saprophyte: Saprophyte, herbivore: Herbivore):

        self.general = general
        self.predator_cell = predator_cell
        self.producer_cell = producer_cell
        self.saprophyte = saprophyte
        self.herbivore = herbivore

        # Initialize pygame
        pygame.init()
        
        # Get the screen info for fullscreen
        screen_info = pygame.display.Info()
        self.max_screen_width = screen_info.current_w
        self.max_screen_height = screen_info.current_h
        
        # Initial window setup
        self.SCREEN_WIDTH = 500
        self.SCREEN_HEIGHT = 500
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        self.display_caption = pygame.display.set_caption("Evolution Simulation")
        self.clock = pygame.time.Clock()

        # Create a larger surface for the entire map
        self.world = pygame.Surface((self.general.WORLD_WIDTH, self.general.WORLD_HEIGHT))
        
        # Camera and zoom settings
        self.camera_x = 0
        self.camera_y = 0
        self.scroll_speed = 5
        self.zoom_level = 1.0
        self.min_zoom = 0.2  # Show up to 5x more area
        self.max_zoom = 2.0  # Show 2x less area (more detailed)
        self.zoom_speed = 0.1
        
        # starting map matrix of the game 100 x 200
        self.biom_map_matrix = map_matrix
        
        self.running = True

        # use it to stop the simulation
        self.run_speed: int = 200
        self.stop_speed: int = 1

        # input the background map from the user, default is the 0 (=grid map)
        self.choosen_map = 0
        # input the utility map from the user, default is the 0 (=no utility)
        self.choosen_utility_map = 0

        # draw the starting map
        self.draw_grid_map()

        # produce the starting generations
        self.producer_cell.generate_producerCells()
        self.predator_cell.generate_predatorCells()
        self.herbivore.generate_herbivore()


    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        
        # Camera movement
        if keys[pygame.K_LEFT]:
            self.camera_x -= self.scroll_speed / self.zoom_level
        if keys[pygame.K_RIGHT]:
            self.camera_x += self.scroll_speed / self.zoom_level
        if keys[pygame.K_UP]:
            self.camera_y -= self.scroll_speed / self.zoom_level
        if keys[pygame.K_DOWN]:
            self.camera_y += self.scroll_speed / self.zoom_level
            
        # Zoom controls (Z and X keys)
        if keys[pygame.K_z]:  # Zoom in
            self.zoom_level = min(self.zoom_level + self.zoom_speed, self.max_zoom)
        if self.zoom_level > 1.0:
            if keys[pygame.K_x]:  # Zoom out
                self.zoom_level = max(self.zoom_level - self.zoom_speed, self.min_zoom)
    
        # Keep camera within bounds considering zoom
        max_camera_x = self.general.WORLD_WIDTH - (self.SCREEN_WIDTH / self.zoom_level)
        max_camera_y = self.general.WORLD_HEIGHT - (self.SCREEN_HEIGHT / self.zoom_level)
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def handle_resize(self, event) -> None:
        if not self.is_fullscreen:
            self.SCREEN_WIDTH = event.w
            self.SCREEN_HEIGHT = event.h
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 
                                                pygame.RESIZABLE)

    def set_camera(self) -> None:
        self.screen.fill(self.general.colors["WHITE"])  # Fill background with black
        
        # Calculate the portion of the world to show based on zoom
        view_width = int(self.SCREEN_WIDTH / self.zoom_level)
        view_height = int(self.SCREEN_HEIGHT / self.zoom_level)
        
        # Create a subsurface of the visible area
        visible_area = pygame.Surface((view_width, view_height))
        visible_area.blit(self.world, (0, 0), 
                         (self.camera_x, self.camera_y, view_width, view_height))
        
        # Scale the visible area to fit the screen
        scaled_surface = pygame.transform.scale(visible_area, 
                                             (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        
        # Draw debug information
        font = pygame.font.Font(None, 24)
        debug_info = [
            f"Camera: ({int(self.camera_x)}, {int(self.camera_y)})",
            f"Zoom: {self.zoom_level:.2f}x",
            f"Screen: {self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}",
            "Arrows: Move camera",
            "Z/X: Zoom in/out",
            "0: Grid Map(Default)",
            "1: Biom Map",
            "NUM0: Without Utilities",
            "NUM1: Food",
            "NUM9: Producer Cell Attributes",
            "ESC: Exit"
        ]
        
        for i, text in enumerate(debug_info):
            text_surface = font.render(text, True, self.general.colors["RED"])
            self.screen.blit(text_surface, (10, 10 + i * 25))
    
    def draw_biom_map(self) -> None:
        self.world.set_alpha(25)
        # Draw the grid on the world surface
        self.world.fill(self.general.colors["WHITE"])
        for i in range(self.general.WORLD_WIDTH // 10):
            pygame.draw.line(self.world, self.general.colors["GRAY"], (i*10, 0), (i*10, self.general.WORLD_HEIGHT))
            pygame.draw.line(self.world, self.general.colors["GRAY"], (0, i*10), (self.general.WORLD_WIDTH, i*10))
        
        for y in range(0, self.general.WORLD_HEIGHT, 10):
            for x in range(0, self.general.WORLD_WIDTH, 10):

                if self.biom_map_matrix[y//10][x//10] == 0:
                    color = "WHITE"
                elif self.biom_map_matrix[y//10][x//10] == 1:
                    color = "BLACK"
                elif self.biom_map_matrix[y//10][x//10] == 2:
                    color = "GRAY"
                elif self.biom_map_matrix[y//10][x//10] == 3:
                    color = "ARCTIC_GRAY"
                elif self.biom_map_matrix[y//10][x//10] == 4:
                    color = "RED"
                elif self.biom_map_matrix[y//10][x//10] == 5:
                    color = "DARK_RED"
                elif self.biom_map_matrix[y//10][x//10] == 6:
                    color = "DARK_GREEN"
                elif self.biom_map_matrix[y//10][x//10] == 7:
                    color = "GREEN"
                elif self.biom_map_matrix[y//10][x//10] == 8:
                    color = "DARK_BLUE"
                elif self.biom_map_matrix[y//10][x//10] == 9:
                    color = "BRIGHT_BLUE"
                elif self.biom_map_matrix[y//10][x//10] == 10:
                    color = "PURPLE"
                elif self.biom_map_matrix[y//10][x//10] == 11:
                    color = "YELLOW"
                elif self.biom_map_matrix[y//10][x//10] == 12:
                    color = "BROWN"
                pygame.draw.rect(self.world, self.general.colors[color], (x+1, y+1, 8, 8))
        self.world.set_alpha(255)

    def draw_grid_map(self) -> None:
        # Draw the grid on the world surface
        self.world.fill(self.general.colors["WHITE"])
        for i in range(self.general.WORLD_WIDTH // 10):
            pygame.draw.line(self.world, self.general.colors["GRAY"], (i*10, 0), (i*10, self.general.WORLD_HEIGHT))
            pygame.draw.line(self.world, self.general.colors["GRAY"], (0, i*10), (self.general.WORLD_WIDTH, i*10))

    def draw_cells(self) -> None:
        color : tuple[int, int, int] = ()
        for cell in self.general.all_cells:
            if type(cell) == Predator_Cell:
                color = self.general.colors["RED"]
            elif type(cell) == Producer_Cell:
                if self.biom_map_matrix[cell.position_y][cell.position_x] == 6:
                    color = self.general.colors["GREEN"]
                elif self.biom_map_matrix[cell.position_y][cell.position_x] == 8:
                    color = self.general.colors["ALGEA_BLUE"]
                elif self.biom_map_matrix[cell.position_y][cell.position_x] == 9:
                    color = self.general.colors["ALGEA_BLUE"]
                elif self.biom_map_matrix[cell.position_y][cell.position_x] == 10:
                    color = self.general.colors["BRIGHT_PURPLE"]
                elif self.biom_map_matrix[cell.position_y][cell.position_x] == 4:
                    color = self.general.colors["ORANGE"]
                else:
                    print("yarra")
            elif type(cell) == Saprophyte:
                color = self.general.colors["PINK"]
            elif type(cell) == Herbivore:
                color = self.general.colors["ORANGE"]
            if not(color):
                color = self.general.colors["PINK"] ### DEBUGGING
            pygame.draw.rect(self.world, color, (cell.position_x*10+2, cell.position_y*10+2, 6, 6))

    def draw_utilities(self) -> None:
        # draw the food
        if self.choosen_utility_map == 1:
            color: tuple[int, int, int] = ()
            for y in range(0, self.general.WORLD_HEIGHT, 10):
                for x in range(0, self.general.WORLD_WIDTH, 10):
                    if self.general.utility_matrix[y//10][x//10] == "F":
                        color = self.general.colors["BRIGHT_BROWN"]
                    elif self.general.utility_matrix[y//10][x//10] == "S":
                        color = self.general.colors["BLACK"]
                    elif self.general.utility_matrix[y//10][x//10] == "G":
                        color = self.general.colors["GOLD"]
                    if color:
                        pygame.draw.rect(self.world, color, (x+2, y+2, 6, 6))
                        color = ()

    def run(self):

        speed = self.run_speed     
        
        while self.running:

            # event handling part
            for event in pygame.event.get():
                # quit the session
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # quit the session
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    # choose map
                    elif event.key == pygame.K_0:
                        self.choosen_map = 0
                    elif event.key == pygame.K_1:
                        self.choosen_map = 1
                    # choose utility map
                    if event.key == pygame.K_KP0:
                        self.choosen_utility_map = 0
                    elif event.key == pygame.K_KP1:
                        self.choosen_utility_map = 1
                    if event.key == pygame.K_SPACE:
                        if speed == self.run_speed:
                            speed = self.stop_speed
                        else:
                            speed = self.run_speed

                # mouse keys
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    ###print(x, y)
                    ###self.general.utility_matrix[y//10][x//10] = "S"

                elif event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                    self.handle_resize(event)


            # real loop
            self.handle_input()
            self.set_camera()

            # draw the map according to choice
            if self.choosen_map == 0:
                self.draw_grid_map()
            elif self.choosen_map == 1:
                self.draw_biom_map()
            
            # draw the utility map according to choice
            if self.choosen_utility_map == 0:
                pass
            elif self.choosen_utility_map == 1:
                self.draw_utilities()

            # draw the cells
            self.draw_cells()
            
            # main loop for predator_cel
            for predator_cell in Predator_Cell.predator_cell_list:
                predator_cell.main_loop_predatorCell(predator_cell)
                
            # main loop for producer_cell
            for producer_cell in Producer_Cell.producer_cell_list:
                producer_cell.main_loop_producerCell(producer_cell)

            # main loop for herbivores
            for herbivore in Herbivore.herbivore_list:
                herbivore.main_loop_herbivore(herbivore)

            # create saprophytes according to conditions
            for shit in Shit.all_shit_list:
                born_chance, shit_positions = Saprophyte.shit_born_chance(self.general, shit.position_x, shit.position_y)
                if random.randint(2, 250) < pow(2, born_chance):
                    Saprophyte.generate_saprophyte(shit_positions, self.general)

            # main loop for saprophyte
            for saprophyte in Saprophyte.saprophyte_cell_list:
                saprophyte.main_loop_saprophyte(saprophyte)

            pygame.display.update()
            self.clock.tick(speed)

        pygame.quit()



if __name__ == "__main__":
    general = General()
    shit_ins = Shit((0, 0, 0), "S")
    predator_cell = Predator_Cell(general, shit_ins)
    producer_cell = Producer_Cell(general, shit_ins)
    saprophyte = Saprophyte(general)
    herbivore = Herbivore(general, shit_ins)
    map = Display(general, predator_cell, producer_cell, saprophyte, herbivore)
    map.run()
