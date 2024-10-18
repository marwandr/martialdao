# Martial Dao - A Brawler Game using UDP

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Known Issues](#known-issues)
- [Credits](#credits)
- [Contributing](#contributing)
- [License](#license)

## Introduction
Martial Dao is a peer-to-peer brawler game I developed as a project for a Computer Networks course. It utilizes PyGame, pickle, and websocket libraries to create a multiplayer gaming experience over UDP.

## Features
- Multiplayer brawler game
- Local server-client architecture
- Custom sprites and music

## Technologies Used
- **Programming Language:** Python
- **Libraries:** PyGame, pickle, websocket
- **Networking Protocol:** UDP

## Installation
To set up the game locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/marwandr/martialdao.git
   cd martialdao

3. Install the required dependencies:
   ```bash
   pip install pygame websocket-client pyfiglet

## Usage
To start playing, simply run the client. Within the client you can choose whether you want to host the server or join a game.
   ```bash
   python3 client.py
```
Use the game interface to control your character and battle against other players.

## Known Issues
- The game currently only works locally and does not support different IP addresses, due to some bugs while retrieving the IP address.
- Server recovery does not work properly after disconnection.

## Credits
- Music: Filip Lackovic - Drums of the Horde
- Sprites:
     dreamer sprites created by developer
     warrior sprites created by: https://luizmelo.itch.io/fantasy-warrior

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.
