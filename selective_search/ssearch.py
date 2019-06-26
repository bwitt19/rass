#!/usr/bin/env python
'''
Usage:
    ./ssearch.py input_image (f|q)[l]
    f=fast, q=quality
    l=large bounding boxes
When displaying image:
Use "l" to display less rects, 'm' to display more rects, "q" to quit.
'''
 
import sys
import cv2
import numpy as np

# Indices for np.shape of ndarray
HEIGHT = 0
WIDTH = 1

# Upper bound of image
UPPER_BOUND = 500

# Minimum ratio of the image that the area of a given large bounding box (LBB) must be
LBB_RATIO = 1/32


# process(): Processes image using selective search
# Input: im, numpy.ndarray containing image to be processed
# Input: mode, string determining what mode (fast, quality, lbb); Default = "ql"
# Input: multithread, bool determining whether to multithread; Default = True
# Output: im, numpy.array containing data for resized image used in search
# Output: rects, numpy.ndarray containing proposed regions from selective search
def process(oldIm, mode="ql", multithread=True):

    if not isinstance(oldIm, np.ndarray):
        raise TypeError("Passed argument im must be of type numpy.ndarray")
    if len(oldIm.shape) != 3:
        raise ValueError("Passed argument im must be a 3 dimensional numpy \
            array containing image data")
    im = oldIm.copy()

    if multithread == True:
        # speed-up using multithreads
        cv2.setUseOptimized(True)
        cv2.setNumThreads(4)

    # resize image
    # set by upper bound specified below
    oldHeight = im.shape[HEIGHT]
    oldWidth = im.shape[WIDTH]

    if oldHeight > oldWidth:
        newHeight = UPPER_BOUND
        newWidth = int(oldWidth * newHeight / oldHeight)
    else:
        newWidth = UPPER_BOUND
        newHeight = int(oldHeight * newWidth / oldWidth)

    # Old: newWidth = int(im.shape[LENGTH] * newHeight / im.shape[HEIGHT])
    im = cv2.resize(im, (newWidth, newHeight))    
 
    # create Selective Search Segmentation Object using default parameters
    ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()
 
    # set input image on which we will run segmentation
    ss.setBaseImage(im)
 
    # adjusting mode based on second argument
    qualityMode = None
    largeMode = None
    if (mode == 'fl'):
        qualityMode = False
        largeMode = True
    elif (mode == 'f'):
        qualityMode = False
        largeMode = False
    elif (mode == 'ql'):
        qualityMode = True
        largeMode = True
    elif (mode == 'q'):
        qualityMode = True
        largeMode = False
    # if second argument is not recognized
    else:
        print(__doc__)
        raise ValueError("Passed argument mode must be in form of '(f|q)[l]'")

    # Switch to high recall but slow Selective Search method
    if qualityMode:
        ss.switchToSelectiveSearchQuality()
    # Switch to fast but low recall Selective Search method
    elif not qualityMode:
        ss.switchToSelectiveSearchFast()

    # run selective search segmentation on input image
    rects = ss.process()
    # Large bounding box mode:
    if largeMode:
        totalImageArea = newHeight * newWidth
        lbbMinArea = totalImageArea * LBB_RATIO

        # Filter list of rects so that they are of a certain size: lbbMinArea
        largeRects = []
        for rect in rects:
            x, y, w, h = rect
            # Calculating membership to rects here based on calculation of area
            area = w * h
            if (area > lbbMinArea):
                largeRects.append([x,y,w,h])
        rects = np.array(largeRects)
    print('Total Number of Region Proposals: {}'.format(len(rects)))
    
    return im, rects


# Displays region proposals given image data and proposed region info
# Input: im, numpy.ndarray containing image data
# Input: rects, numpy.ndarray containing data for proposed regions in image
# Output: imOut, numpy.ndarray containing image data with region proposals
def annotate_image(im, rects):

    # Check that im and rects are of correct type
    if not isinstance(im, np.ndarray):
        raise TypeError("Passed argument im must be of type numpy.ndarray")
    if not isinstance(rects, np.ndarray):
        raise TypeError("Passed argument rects must be of type numpy.ndarray")
    if len(rects.shape) != 2:
        raise TypeError("Passed argument rects must be 2D numpy.ndarray of shape (n, 4)")

    # Check that rects is width 4 (x,y,w,h)
    if rects.shape[WIDTH] != 4:
        raise ValueError("Values in rects should be width 4 (storing x, y, w, h)")


    # number of region proposals to show
    numShowRects = 100
 
    # create a copy of original image
    imOut = im.copy()

    # itereate over all the region proposals
    for i, rect in enumerate(rects):
        # draw rectangle for region proposal till numShowRects
        if (i < numShowRects):
            x, y, w, h = rect
            cv2.rectangle(imOut, (x, y), (x+w, y+h), (0, 255, 0), 1, cv2.LINE_AA)
        else:
            break

    return imOut
    

if __name__ == '__main__':
    # If image path and f/q is not passed as command
    # line arguments, quit and display help message
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    im_name = sys.argv[1]
    mode = sys.argv[2]
    im = cv2.imread(im_name)
    im, rects = process(im, mode)


    ### Below is a version of annotate_image(), but interactive
    ### Can use l, m, and q, to display different info about regions proposed

    # number of region proposals to show
    numShowRects = 100
    # increment to increase/decrease total number
    # of reason proposals to be shown
    increment = 50
 
    while True:
        # create a copy of original image
        imOut = im.copy()
 
        # itereate over all the region proposals
        for i, rect in enumerate(rects):
            # draw rectangle for region proposal till numShowRects
            if (i < numShowRects):
                x, y, w, h = rect
                cv2.rectangle(imOut, (x, y), (x+w, y+h), (0, 255, 0), 1, cv2.LINE_AA)
            else:
                break
 
        # show output
        cv2.imshow("Output", imOut)
 
        # record key press
        k = cv2.waitKey(0) & 0xFF
 
        # m is pressed
        if k == 109:
            # increase total number of rectangles to show by increment
            numShowRects += increment
        # l is pressed
        elif k == 108 and numShowRects > increment:
            # decrease total number of rectangles to show by increment
            numShowRects -= increment
        # q is pressed
        elif k == 113:
            break
    # close image show window
    cv2.destroyAllWindows()
