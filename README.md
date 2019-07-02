# rass
Proof of concept for a voice interface for an object mouse used by a robotic arm.  
_(robotic arm selective search)_

## Instructions to run
To run, this program requires Python 3.x and a few modules (you can use a venv for this) that I've put in pip_requirements.txt. You can install these with `pip -r pip_requirements.txt`

After that, you can just run `ui.py` with Python 3, and the rest should work automatically.

## What it does
The program will take a picture from your default webcam and analyze it to try and recognize objects within the scene.  
Afterwards, it will wait and listen for user input vocally for a select set of keywords after a keypress from the user. _(OpenCV requires that you be focused on the window with the image to have the keypress be registered -- I'm working on changing this)_

Keywords you can use:
* "next": Choose the next object in a set of recognized objects.
* "previous": Choose the previous object.
* "focus": Zoom in and focus on a particular object; this will choose this image to be the new base image, and objects will be searched for within this new frame.
* "refresh": Take a new photo and abandon current object set to reanalyze for objects.
* "select": Select the current object being focused on. _As this is a proof of concept however, what this does is instead display the coordinates of the object within the image to the user, and refresh the frame shown._
* "quit", "exit", "stop": Exit the program.

Once voice input is recorded, it will be translated from speech to text using a Google API within the Python SpeechRecognition module.

Of note:
1. This program uses your default mic and webcam -- I haven't yet added functionality to mess around with this.
2. There are still some kinks in the code, so it's not exactly 100% bug free -- if you find something here or there let me know.
3. This uses a basic selective search algorithm within an extended contribution friendly version of OpenCV. It's not exactly the best for finding and recognizing objects, but I'm working on looking into better methods and tools to do object segmentation within cluttered scenes for a better version of this program.
