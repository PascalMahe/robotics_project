## Project for IA712 in Telecom Paris MS IA

### Needs a Tello drone to run (just one at the moment, maybe more later)

Basic idea of the project is search and rescue: have a drone search for someone in a room then have another drone rejoin the first once the target has been found.

To work, first turn on the drone and connect the computer to its Wifi network.

Then use either:
 - test_connect.py to check that the Python can connect to the drone. The drone will not move, only send back its battery level.
 - tello-2.py to take off, do a few basic moves (move up, turn, go down...) and land again
 - drone-ctrl.ipynb to have an interactive notebook to: connect, send commands and disconnect properly.

receive_state.py _should_ receive the state from the drone. Untested.

Need to add commands to get the video streaming.
