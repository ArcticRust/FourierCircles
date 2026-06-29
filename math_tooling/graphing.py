# i hate graphing >:(

import pygame
from .function_list import *
import time
import random

BLACK = (0, 0, 0)
pygame.init()

class GraphBuilder:
    def __init__(self):
        self.axis_width = 2
        self.width = 1280
        self.height = 720
        self.center = (self.width / 2, self.height / 2)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill("white")
        self.num_x_markers = 10 # in each direction
        px_width_of_x_marker = self.width / (2 * self.num_x_markers)
        self.num_y_markers = self.height / px_width_of_x_marker / 2
        self.marker_width = 2
        self.marker_height = 20
        self.x_scale = 1
        self.y_scale = 1

        self.draw_axis()
        # TODO: add dt shenanigans later, only doing plotting now

    def adjust_y_scale(self, new_val: float):
        self.y_scale = new_val
    
    def adjust_x_scale(self, new_val: float):
        self.x_scale = new_val

    def draw_axis(self, x_scale: float=1, y_scale: float=1):

        # y axis
        top_left_point = (self.width / 2 - self.axis_width / 2, 0)
        width_height = (self.axis_width, self.height) 
        pygame.draw.rect(self.screen, BLACK, pygame.rect.Rect(top_left_point, width_height))

        # x axis
        top_left_point = (0, self.height / 2 - self.axis_width / 2)
        width_height = (self.width, self.axis_width) 
        pygame.draw.rect(self.screen, BLACK, pygame.rect.Rect(top_left_point, width_height))

        # x markers
        dist_between_x_markers = self.width / 2 / self.num_x_markers
        for i in range(1, int(self.num_x_markers) + 1):
            # positive end of axis
            top_left_of_rect = (self.width / 2 + dist_between_x_markers * i - self.marker_width / 2, self.height / 2 - self.marker_height / 2)
            width_height_of_rect = (self.marker_width, self.marker_height)
            pygame.draw.rect(self.screen, BLACK, pygame.rect.Rect(top_left_of_rect, width_height_of_rect))
            
            # negative end of axis
            top_left_of_rect = (self.width / 2 - dist_between_x_markers * i - self.marker_width / 2, self.height / 2 - self.marker_height / 2)
            width_height_of_rect = (self.marker_width, self.marker_height)
            pygame.draw.rect(self.screen, BLACK, pygame.rect.Rect(top_left_of_rect, width_height_of_rect))

        # y markers
        dist_between_y_markers = self.height / 2 / self.num_y_markers
        for i in range(1, int(self.num_y_markers) + 2):
            # positive end of axis
            top_left_of_rect = (self.width / 2 - self.marker_height / 2, self.height / 2 + self.marker_width / 2 - dist_between_y_markers * i)
            width_height_of_rect = (self.marker_height, self.marker_width)
            pygame.draw.rect(self.screen, BLACK, pygame.rect.Rect(top_left_of_rect, width_height_of_rect))

            # positive end of axis
            top_left_of_rect = (self.width / 2 - self.marker_height / 2, self.height / 2 + self.marker_width / 2 + dist_between_y_markers * i)
            width_height_of_rect = (self.marker_height, self.marker_width)
            pygame.draw.rect(self.screen, BLACK, pygame.rect.Rect(top_left_of_rect, width_height_of_rect))
        

    def plot(self, func: Expr, color: tuple[float, float, float]=(266, 0, 0)):
        if color[0] == 266:
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        num_pixels_per_interpolation = 2
        x_per_pixel = self.x_scale * self.num_x_markers * 2 / self.width 
        y_per_pixel = self.y_scale * self.num_y_markers * 2 / self.height
        x_offset = self.num_x_markers * self.x_scale # offset since starting at x = -num_x_markers * x_scale
        temp = func.eval(-x_offset)
        incr = num_pixels_per_interpolation * x_per_pixel
        for i in range(int(self.width / num_pixels_per_interpolation)):
            x_val = incr * (i + 1) - x_offset
            f_of_x1 = temp
            try:
                error_storage = func.eval(x_val)
                f_of_x2 = error_storage
            except:
                pass
            temp = f_of_x2
            
            coord1 = (int(i * num_pixels_per_interpolation), int(-f_of_x1 / y_per_pixel + self.height / 2))
            coord2 = (int((i + 1) * num_pixels_per_interpolation), int(-f_of_x2 / y_per_pixel + self.height / 2))
            pygame.draw.line(self.screen, color, coord1, coord2, 2)
        

    def update(self):
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                
            self.update()
            time.sleep(.1)

    def _coord_convert_cartesian2py(self, x: float, y: float) -> tuple[float, float]:
        x_markers_worth = x / self.x_scale
        y_markers_worth = y / self.y_scale
        return self.center + (x_markers_worth * (self.width / self.num_x_markers), -y_markers_worth * (self.height / self.num_y_markers))

    # implement if necessary
    #def _coord_convert_py2cartesian(self, x: float, y: float):
    #    ...

    def __del__(self):
        pygame.quit()



