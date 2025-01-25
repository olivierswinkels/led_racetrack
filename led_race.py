import pygame
import sys
import numpy as np
from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
from dataclasses import dataclass

@dataclass
class Player:
    controller: pygame.joystick.Joystick
    color: Color
    speed: int
    location: int

COLORS = [Color(255, 0, 255), Color(0, 255, 0), Color(0, 0, 255), Color(255, 0, 0)]


class LedRace():
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.game_speed = 1

        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            print("No game controllers found.")
            sys.exit()

       # Initialize all connected joysticks
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(joystick_count)]
        for joystick in self.joysticks:
            joystick.init()
            
        # Print controller information
        self.players = []
        for i, joystick in enumerate(self.joysticks):
            self.players.append(Player(joystick, COLORS[i], 0, 0))
            print(f"Player {i}: {joystick.get_name()}")
    

        self.leds = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=100)
        self.strip = self.leds.get_strip()
        self.num_pixels = self.strip.num_pixels()
        print(f"LED Strip has {self.num_pixels} leds")



        self.run()
        
    def __del__(self):
        pygame.joystick.quit()
        pygame.quit()
    
    def run(self):
        try:
            while True:
                # Process events
                pygame.event.pump()
                # initialize track
                track = np.zeros((self.num_pixels, 3), dtype=np.uint8)
                track[30:40] = Color(0, 50, 50)
                for player in self.players:
                    num_axes = player.controller.get_numaxes()
                    axis_states = [player.controller.get_axis(j) for j in range(num_axes)]
                    speed = max(axis_states) * self.game_speed
                    
                    player.location = (player.location + speed) % self.num_pixels
                    track[int(player.location)] = player.color
                


                # Add a small delay to avoid flooding the console
                self.leds.write(track)  
                pygame.time.delay(10)
        
        except KeyboardInterrupt:
            print("Exiting...")

if __name__ == "__main__":
    LedRace()
