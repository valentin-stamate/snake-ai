import random
import threading
import tkinter as tk

from game.snakegame import SnakeGame
from game.json_reader import JsonReader

episodes = 10
window = tk.Tk()

replay_memory = []


def main():
    config = JsonReader.read('configuration.json')

    window.title('Snake')

    canvas = tk.Canvas(window, bg="#202020", width=config['width'], height=config['height'])
    canvas.grid(row=0, column=0, columnspan=1)

    game = SnakeGame(window=window, canvas=canvas, config=config, show_progress=False)

    game.register_callbacks(lambda x: on_refresh(x))

    # Create a new thread to run the game independently
    threading.Thread(target=lambda: start(game)).start()

    window.eval('tk::PlaceWindow . center')
    window.mainloop()


def start(game: SnakeGame):
    for i in range(episodes):
        print(f"Episode {i + 1}")
        game.start()

    # for experience in replay_memory:
    #     print(experience)

    window.destroy()


def on_episode_end(episode):
    print(f'Episode %-3d ended' % episode)


def on_refresh(game: SnakeGame):
    game.make_action(random.sample(game.possible_actions, 1)[0])
    experience = game.refresh_snake()

    replay_memory.append(experience)

if __name__ == '__main__':
    main()


