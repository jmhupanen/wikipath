# Wikipath
This program implements a distributed system that finds the shortest path between the provided Wikipedia pages. It has six workers 
that fetch links from the found pages. 

To find the path between two Wikipedia pages, you have to type the starting page after the 
"Starting page:" prompt and the destination after the "Destination page:" prompt. After that, the workers parse pages until the 
destination page is found. Finally, the program prints the path from the start to the destination.

## How to run
To build the image use command: ```docker build -t wikipath .```

To run the container use command: ```docker run -ti wikipath```
