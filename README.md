# Santorini AI

The goal of this game is to create a powerful Santorin AI player, alongside a GUI where users can play against it. Currently, there are two AI algorithms: Minimax and Monte Carlo Tree Search (MCTS). More work has been put into the latter, so it is a stronger opponent. Other AIs may be added in future versions

## Getting Started

I run this on Pycharm in Python 3.9. Users need pygame installed, and a computer with some graphics inferface. Some virtual environments (like Google Colab) lack the visual capability to show the pygame interface. Run the the following to start the program:

> python pygame_gui.py

This will initate the pygame GUI. From here, players must choose who will play as the white and grey player. The game will continue from there until a player exits the program.

### Requirements

> pygame=2.0.1

Note: pypy does not support pygame.

## Authors

* **Marshall Krakauer** - *marshallkrakauer (at) gmail.com* - [Github](https://github.com/MarshallKrakauer)


## License

This project is licensed under Creative Commons.

## Acknowledgments

* [Programming Pixels](https://programmingpixels.com/handling-a-title-screen-game-flow-and-buttons-in-pygame.html) - Used this code to create button
* [My Great Learning](https://www.mygreatlearning.com/blog/alpha-beta-pruning-in-ai/) - Used to build minimax algorithm with alpha-beta pruning
