import pygame
from random import randint
import game_configs

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

BLUE = (0, 100, 255)
WHITE = (255, 255, 255) 
RED = (200, 0, 0)
GRAY = (100, 100, 100)

class FlappyBirdGame:
    def __init__(
            self,
            w=game_configs.screen_width,
            h=game_configs.screen_height,
            speed=game_configs.AI_game_speed
        ):
        self.w = w
        self.h = h
        self.speed = speed

        self.display = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()

        self.score = 0
        self.bird = Bird()
        self.pipes = []

        self.pipes.append(PipesMiddleSpace())
        self.pipes.append(PipesMiddleSpace(x=self.w + game_configs.pipes_distance))
    
    def reset(self):
        self.bird.reset()
        self.pipes = []
        self.pipes.append(PipesMiddleSpace())
        self.pipes.append(PipesMiddleSpace(x=self.w + game_configs.pipes_distance))
        self.score = 0
    
    def play_step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.bird.move(action)

        reward = 0
        game_over = False

        if self.bird.y < 0:
            reward = -20
        
        if self.bird.y > self.pipes[0].y and self.bird.y < self.pipes[0].y + self.pipes[0].h:
            reward = 5

        for pipe in self.pipes:
            pipe.move()

            if pipe.x + pipe.w < self.bird.x:
                self.pipes.remove(pipe)
                self.pipes.append(PipesMiddleSpace())
            
            if not pipe.done and self.bird.x > pipe.x + pipe.w:
                self.score += 1
                reward = 20
                pipe.done = True

            if self.bird.y + self.bird.h > self.h:
                reward = -20
                game_over = True
                break

            if self.bird.x + self.bird.w > pipe.x and self.bird.x < pipe.x + pipe.w:
                if self.bird.y < pipe.y or self.bird.y + self.bird.h > pipe.y + pipe.h:
                    reward = -20
                    game_over = True
                    break
                else:
                    reward = 10

        # if action == [0, 1]:
        #     reward = 100

        self._update_ui()

        return reward, game_over, self.score

    def _update_ui(self):
        self.display.fill(BLUE)

        self.bird.draw(self.display)

        for pipe in self.pipes:
            pipe.draw(self.display)

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])

        pygame.display.update()
        self.clock.tick(self.speed)


class Bird:
    def __init__(
            self,
            x = game_configs.bird_start_x,
            y = game_configs.bird_start_y,
            h = game_configs.bird_height,
            w = game_configs.bird_width,
            g = game_configs.bird_g,
            jump_power = game_configs.bird_jump_power
        ):
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.g = g
        self.jump_power = jump_power

        self.y_vel = 0
    
    def reset(self):
        self.x = game_configs.bird_start_x
        self.y = game_configs.bird_start_y

        self.y_vel = 0

    def jump(self):
        self.y_vel = -self.jump_power

    def move(self, action):
        if action == [0, 1]:
            self.jump()
        
        self.y += self.y_vel
        self.y_vel += self.g
    
    def draw(self, display):
        pygame.draw.rect(display, WHITE, (self.x, self.y, self.w, self.h))


class PipesMiddleSpace:
    def __init__(
            self,
            x = game_configs.pipe_start_x,
            y_min = game_configs.pipe_start_y_min,
            y_max = game_configs.pipe_start_y_max,
            h_min = game_configs.pipe_height_min,
            h_max = game_configs.pipe_height_max,
            w_min = game_configs.pipe_width_min,
            w_max = game_configs.pipe_width_max,
            speed = game_configs.pipe_speed
        ):
        self.x = x
        self.speed = speed

        self.h = randint(h_min, h_max)
        self.w = randint(w_min, w_max)
        self.y = randint(y_min, y_max - self.h)

        self.done = False

    def move(self):
        self.x -= self.speed

    def draw(self, display):
        pygame.draw.rect(display, GRAY, (self.x, 0, self.w, self.y))
        pygame.draw.rect(display, GRAY, (self.x, self.y + self.h, self.w, display.get_height() - self.y - self.h))