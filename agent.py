import torch
import random
import numpy as np
from collections import deque
from game import FlappyBirdGame
from model import Linear_QNet, QTrainer
import game_configs
from helper import plot
import os
from datetime import datetime

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(12, 128, 2)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
    
    def get_state(self, game):
        state = [
            game.bird.x,
            game.bird.y,
            game.bird.y_vel,
            game_configs.bird_width,
            game_configs.bird_g,

            game.pipes[0].x,
            game.pipes[0].y,
            game.pipes[0].h,
            
            game.pipes[1].x,
            game.pipes[1].y,
            game.pipes[1].h,

            game_configs.pipe_width_max,
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0, 0]

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(1, 10)
            if move > 1:
                move = 0
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            
        return final_move

def train():
    # Create a unique folder for this training run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_folder = f'./models/run_{timestamp}'
    os.makedirs(model_folder, exist_ok=True)
    
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0

    agent = Agent()
    game = FlappyBirdGame()

    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            # Save last model
            agent.model.save(file_name=os.path.join(model_folder, 'last_model.pth'))

            # Save best model if new record
            if score > record:
                record = score
                agent.model.save(file_name=os.path.join(model_folder, 'best_model.pth'))

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()