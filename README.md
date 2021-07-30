# Santorini AI

This code seeks to implement the abstract board game Santorini with Python. The interface of the game is implemented with Pygame. There are two AIs: one uses Minimax and one used Monte Carlo Tree Search (MCTS).

## Getting Started

I run this on Pycharm in Python 3.9. Users need pygame installed, and a computer with some graphics inferface. Some virtual environments (like Google Colab) lack the visual capability to show the pygame interface.

To play the game, run "pygame_gui.py" This will import all the relevant classes from other files.

If one is unable to use pygame, run the "ascii_game.py" file. This will alow the player to use keyboard commands to play.

### Prerequisites

The following packages must be installed: pygame, random, math, pandas, numpy, sklearn, joblib

Note: pypy does not support pygame.

## Built With

* [Pycharm](https://www.jetbrains.com/pycharm/) - IDE
* [Pygame](https://www.pygame.org/news) - Game interface

## Versioning

Currently in beta testing. Version control using Git.
In the current version, the Game AI includes lots of blank space one each side. I plan to add further information, such as a turn history and AI decision-making visuals
in this space.


## Authors

* **Marshall Krakauer** - *marshallkrakauer (at) gmail.com* - [Github](https://github.com/MarshallKrakauer)


## License

This project is licensed under Creative Commons.

## Acknowledgments

* [Programming Pixels](https://programmingpixels.com/handling-a-title-screen-game-flow-and-buttons-in-pygame.html) - Used this code to create button
* [My Great Learning](https://www.mygreatlearning.com/blog/alpha-beta-pruning-in-ai/) - Used to build minimax algorithm with alpha-beta pruning
* [Gord](https://boardgamegeek.com/boardgamedesigner/3302/gord) - Creator of Santorini
* [Tech with Tim](https://www.youtube.com/channel/UC4JX40jDee_tINbkjycV4Sg) - Pygame tutorial, pycharm tutorial, github tutorial, checkers AI tutorial, OOP tutorial...
* [Kevin Mess](https://www.csn.edu/directory/kevin-mess) - The best CS lecturer
* [Sam Ragusa](https://github.com/SamRagusa/Checkers-Reinforcement-Learning) - Example of Alpha-Beta Pruning in Python
