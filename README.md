#Harry Potter Video Load Remover 
Initial program created by jagotu, revised by Cynaschism and TheTedder.
Uses Python 3.8.
##How to Install  
Clone the repository.
Then run the following command.

>`pip install -r requirements.txt`

Run main.py

##How to Use
Select the video to retime.
Then select the game that is running.
Current full support for:
- Harry Potter 1 (PS2, Xbox, Gamecube)
- Harry Potter 2 (PS2, Xbox, Gamecube)  
- Harry Potter 3 (PS2, Xbox, Gamecube)  

Note: Harry Potter 2 PC feature not currently setup for retime use.

Select the start frame, end frame, and the dimensions of the watch box. Make sure the preview image looks correct to the reference image in the bottom left of the window.

###Enter a threshold value
Program currently compares images using Structural Similarity. Value is 0-1, 1 being exact match.
The number next to the input box is the current SSI value on the preview image.
0.9 is found to generally be a good threshold value to use.

After clicking OK, program will process the video.
Note: it will likely be heavily on computer resources, looking to fix that in later updates. Possibly a single process vs multiprocess user option.
After processing, a results box will display:
- real time duration of the selected region.
- total number of load frames
- processing time
- loadless time


