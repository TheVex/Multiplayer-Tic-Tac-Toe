# Multiplayer-Tic-Tac-Toe
<div align = center><img src="banner.jpg"><br><br></div>
  
Our task was to implement **project 1 of variant A**, which consisted in creating a multiplayer game server with Python sockets. We have implemented a multiplayer game server using **TCP sockets**. The game is a turn-based tic-tac-toe game between two players. The server manages the states of the players and ensures consistent synchronization. 

This project is relevant to us because we love to play tic-tac-toe among ourselves, and so we were able to try to implement our own game and practice the skills we learned in the Distributed network systems (DNP) course. Namely, the creation of **TCP sockets** and **multithreading**

You can find more details about the project in the report.

## Preparing for launch

1. Clone the repository:
```bash
git clone https://github.com/TheVex/Multiplayer-Tic-Tac-Toe.git
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

3. Launching the app.
The application consists of a server and clients. To work, you must:
1. Start the server (in the first terminal):
```bash
python server.py
```
2. Wait for the server startup message in the logs.
3. Launch the first client (in the second terminal):
```bash
python client.py
```
4. Launch the second client (in the third terminal):
```bash
python client.py
```
## How to start the game
1. In the first client, click `Play`. Empty lobby will be opened, where `Create game` button should be clicked.
2. Open lobby in second client. A list of available games should appear in the second client (otherwise click refresh)
3. Select `Game 1` in the second client to connect to the game.
