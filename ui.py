#!/usr/bin/env python
'''This is the user-interface for an object detecting robot arm that
  is controlled via voice commands.
'''

import time
import cv2
import speech_recognition as sr
import ssearch

ASCII_BEL = '\007'
ACTIONS = ["next","previous","focus","refresh","select","full"]
SIMILAR_ACTIONS = ["no","last","zoom","new","yes","big"]
SENTINEL_VALUES = ["stop","end","quit","off","exit"]
NEXT = 0
PREV = 1
FOCUS = 2
REFRESH = 3
SELECT = 4
FULL = 5

# Comment this out if only using true command names
ACTIONS += SIMILAR_ACTIONS 

# Captures a photo using cv2
# Input: None 
# Output: frame, a photo in form of np array
def capturePhoto():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened(): 
        raise Exception("Could not open video device")
    
    print("Camera opened.")
    time.sleep(1)
    
    ret, frame = cam.read()
    cam.release()
    cv2.destroyAllWindows()
    del cam

    if not ret:
        raise Exception("Photo could not be captured")
    print("\tPhoto captured.")
    return frame

# Captures input from user as speech and returns as text
# - note: Uses default microphone
# Input: verbose, bool to make function verbose (default is True)
# Output: text, string containing converted speech
def getSpeechInput(verbose = True):
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    # Record audio
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        if verbose: print("\tListening for command!" + ASCII_BEL)
        audio = r.listen(source)
    del mic
    
    # Process audio
    if verbose: print("\tProcessing...")
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        if verbose: print("Your input was not recognized.")
        return -1

# Gets valid voice command for UI
# Input: None
# Output: text_input, valid command converted to text from speech
def getValidCommand():

    badVoice = True
    while badVoice:
        text_input = getSpeechInput()
        # If speech was not recognized (-1 returned), attempt again
        if not isinstance(text_input, str): continue
        text_input = text_input.lower()

        # If text corresponds to an action
        if text_input in ACTIONS:
            badVoice = False
            print("Recognized action:", text_input)
        else:
            # Check if sentinel value was spoken
            for word in text_input.split():
                if word in SENTINEL_VALUES:
                    badVoice = False
                    text_input = word
                    print("Recognized \"{}\": Exiting program...".format(word))
                    break
            # If sentinel value was not spoken, print error message
            if badVoice == True:
                print("\"{}\" is not a valid option.".format(text_input))
    
    return text_input
    


def main():
    print(__doc__)
    print("Starting UI...")
    
    # while we are using the UI, keep running this loop
    run_ui = True
    fullFrame = capturePhoto()
    frame, rects = ssearch.process(fullFrame)
    frameAnnotated = ssearch.annotate_image(frame, rects)
    print("Displaying full scene. Press any key to continue.")
    cv2.imshow("Annotated Scene", frameAnnotated)
    cv2.waitKey(0)
    cv2.destroyWindow("Annotated Scene")

    i = 0
    while run_ui:
        # Create and display window with current recognized image
        x, y, w, h = rects[i]
        currObject = frame[y:y+h, x:x+w]
        print("\nDisplaying object #{}".format(i + 1))
        print("Press any key to continue.")
        cv2.imshow('Current Object', currObject)
        cv2.waitKey(0)
        
        # Get voice command and validate it
        text_input = getValidCommand()

        # If user's command matches a sentinel, quit loop and program
        if text_input in SENTINEL_VALUES:
            break

        # Do action corresponding to given voice command
        # Move to next object
        if text_input == ACTIONS[NEXT]:
            if i < len(rects):
                i += 1
            else:
                print("There are no more next objects; looping back to start")
                i = 0
        # Move to previous object
        elif text_input == ACTIONS[PREV]:
            if i > 0:
                i -= 1
            else:
                print("There are no more previous objects.")
        # Focus in on currObject and do ssearch within that object
        elif text_input == ACTIONS[FOCUS]:
            print("\nAnalyzing current view as new scene...")
            frame = currObject
            frame, rects = ssearch.process(frame, resize=False)
            frameAnnotated = ssearch.annotate_image(frame, rects)
            i = 0
        # Refresh and obtain new frame from camera, redo ssearch and start over
        elif text_input == ACTIONS[REFRESH]:
            fullFrame = capturePhoto()
            frame, rects = ssearch.process(fullFrame)
            frameAnnotated = ssearch.annotate_image(frame, rects)

            print("\nDisplaying new full scene. Press any key to continue.")
            cv2.imshow("Annotated Scene", frameAnnotated)
            cv2.waitKey(0)
            cv2.destroyWindow("Annotated Scene")
            i = 0
        # Select current object
        elif text_input == ACTIONS[SELECT]:
            print("Current object has been selected.")
            print("Object #{}, Coordinates: {}".format(i, rects[i]))
            print("------")
            time.sleep(5)
        # Briefly show full annotated photo
        elif text_input == ACTIONS[FULL]:
            print("Displaying full scene...")
            print("Press any key to continue.")
            cv2.imshow("Full Scene", frameAnnotated)
            cv2.waitKey(0)
        
        # Quickly refresh windows
        cv2.destroyAllWindows()
        
    # Destroy all remaining windows before exiting
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
