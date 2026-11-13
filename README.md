### Project Goal
This project examines limited attention and time pressure in chess. 
In the first stage, we identify important predictors of mistakes made, such as time pressure, specific position characteristics, board advantages,etc. 
With factors that predict difficulty, we can establish a scoring system that tracks the difficulty of each node. 

In the second stage, based on the estimated difficulty of each position, we explore players' risk tolerance and risk seeking level at different stages 
and scenarios of a game. We can also segmentate higher-rated players from lower-rated players and understand how their behavior differ

### Description
We start by randomly selecting games from playes in Lichess with API request.
We use the Python-chess library to extract game, time, and position characteristics for those games.
Our purpose is to create a reduced-form model regressing centipawn loss(CL) on various variables.

### Dependencies

Describe any prerequisites, libraries, OS version, etc., needed before installing program.
ex. Windows 10

### Installing
How/where to download your program
Any modifications needed to be made to files/folders

### Executing program
How to run the program
Step-by-step bullets,
code block for comments


### Help
Any advise for common problems or issues.

 
### Authors
Samuel Cheung

### Version History

0.2
Various bug fixes and optimizations
See commit change or See release history
0.1
Initial Release
License


### Acknowledgments

Inspiration, code snippets, etc.

