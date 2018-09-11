################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
#
#   written by Sarah Almeda at The College of New Jersey 9/2018
#
################################################################################
from __future__ import with_statement
import Leap, sys, thread, time, termios, tty, os, datetime, math
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

#margin of error used for comparing distances to detect finger status
extendedMargin = 9;
curledMargin = 3;
downMargin = 1;

def getSign(fingers, hand):
    statusOf = dict(fingers) #make a dictionary with finger initials as keys
    if not (statusOf):
        print "I can't see your full hand!"
        return
    if (statusOf['P'] == 'curled' and statusOf['M'] != 'extended'): #PINKY IS CURLED.
            print "You signed an E"
            return
    if (statusOf['P'] == 'bent'): #PINKY IS BENT. D O C
        if (statusOf['R'] == 'extended'):
            print "You signed a W"
            return
        else:
            if (statusOf['I'] == 'extended'):
                if (statusOf['T'] == 'extended'):
                    print "You signed an L"
                else:
                    print "You signed a D"
            elif (statusOf['M'] != 'extended'):
                print "You signed an O or C" #or a C
        return
    elif(statusOf['P'] == 'down' or statusOf['P'] == 'bent'): #PINKY IS DOWN OR BENT
        #CHECK MIDDLE FINGER STATUS
        if (statusOf['M'] == 'down'):
            if (statusOf['I'] == 'extended' and statusOf['T'] == 'extended'):
                print "You signed an L"
                return
            if (statusOf['I'] == 'down'): #all fingers down
                if (statusOf['T'] == 'down'):
                    print "You signed an S" #or  a T
                    return
                else:
                    print "You signed an A"
                    return
            else:
                print "You signed an X"
                return

        elif (statusOf['M'] == 'bent'):
            print "You signed a K, M, or N. I can't tell yet!"
            return
        elif (statusOf['M'] == 'extended'):
            if (statusOf['I'] == 'extended' ):
                print "You signed a R, U, or V. I can't tell yet!"
            elif(statusOf['R'] != 'extended'):
                print "Peace among worlds!"
        return
    elif(statusOf['P'] == 'extended'): #PINKY IS EXTENDED
        if (statusOf['R'] == 'extended'): #RING IS EXTENDED
            if (statusOf['I'] == 'extended'): #INDEX IS EXTENDED
                     if (statusOf['T'] == 'extended'): #THUMB IS EXTENDED
                        print "That's an open palm. High five!"
                        return
                     else:
                        print "You signed a B"
                        return
            else: #INDEX IS NOT EXTENDED
                print "You signed an F"
                return
        else: #RING IS NOT EXTENDED
            if (statusOf['T'] == 'extended'): #THUMB EXTENDED
                if (statusOf['I'] == 'extended'): #INDEX IS EXTENDED
                    print "I love you too ;)"
                    return
                else:
                    print "You signed a Y"
                    return
            else:
                print "You signed an I"
                return
    print "I don't know what you signed!"

#######################################################################
#
# getFingerStatuses - used to get status of each finger                 #
#   either extended, or bent, and a bent finger can be curled or down   #
#
########################################################################

def getFingerStatuses(fingers, hand):
    
    result = []
    status = 'unknown'
    
    for a, f in fingers:
        
        ##GET DATA
        shortLength = f.length
        metacarpalLength = (f.bone(0).length/2) #length of half the metacarpal
        fullLength = shortLength + metacarpalLength #estimated length from center of palm to tip of finger

        tipToPalm = getDistance(f.bone(3).next_joint, hand.palm_position) #distance from finger tip to palm
        intToPalm = getDistance(f.bone(2).center, hand.palm_position) #distance from finger center to palm
        proxToPalm = getDistance(f.bone(1).prev_joint, hand.palm_position) #distance from beginning of finger to palm
        proxToPalm
        ##DECIDE FINGER STATUS
        #special logic for thumb
        if (a == 'T'):
            if (f.is_extended):
                
                status = 'extended' #the finger must be extended
                
            else:
                status = 'bent'
                if ((tipToPalm - intToPalm) < curledMargin):
                    status = 'curled'
                if ((intToPalm-proxToPalm) < downMargin): #if middle of thumb is closer to palm than base of thumb
                    status = 'down'
            
        #for all fingers except the thumb
        else:
            #if the tip of the finger is farther than the estimated length by a certain margin,
            if ((tipToPalm - fullLength) > extendedMargin):
               
               
                status = 'extended' #the finger must be extended
            
            #otherwise, the finger is curled or down (as in a fist)
            else:
                status = 'bent'
                #if the tip is substantially closer to the palm than the finger center is
                if ((tipToPalm - intToPalm) < curledMargin):
                    status = 'curled'
                if ((tipToPalm - shortLength) < downMargin):
                    status = 'down'

        result.append((a, status))
    return result


def printFingerStatuses(fingers, hand):
    
    status = 'unknown'
    
    for a, f in fingers:
        shortLength = f.length
        metacarpalLength = f.bone(0).length
        print "%d short length" % shortLength
        fullLength = shortLength + (metacarpalLength/2)
        print "%d full length" % fullLength
        
        
        tipToPalm = getDistance(f.bone(3).next_joint, hand.palm_position) #distance from finger tip to palm
        print "%d tip to palm " % tipToPalm
        intToPalm = getDistance(f.bone(2).center, hand.palm_position) #distance from finger center to palm
        print "%d int to palm" % intToPalm
        proxToPalm = getDistance(f.bone(1).center, hand.palm_position)
        print "%d proximal distance" % proxToPalm
        
        
        ##DECIDE FINGER STATUS
        #special logic for thumb
        if (a == 'T'):
            if (f.is_extended):
                
                status = 'extended' #the finger must be extended
            
            else:
                status = 'bent'
                if ((tipToPalm - intToPalm) < curledMargin):
                    status = 'curled'
                if ((intToPalm-proxToPalm) < downMargin): #if middle of thumb is closer to palm than base of thumb
                    status = 'down'
    
        #for all fingers except the thumb
        else:
            #if the tip of the finger is farther than the estimated length by a certain margin,
            if ((tipToPalm - fullLength) > extendedMargin):
                
                
                status = 'extended' #the finger must be extended
                
                #otherwise, the finger is curled or down (as in a fist)
            else:
                status = 'bent'
                #if the tip is substantially closer to the palm than the finger center is
                if ((tipToPalm - intToPalm) < curledMargin):
                    status = 'curled'
                if ((tipToPalm - shortLength) < downMargin):
                    status = 'down'
        
        print "------\n%s is %s\n=========\n" % (a,status)



def getDistance(vector1, vector2):
    x1 = vector1.x
    y1 = vector1.y
    z1 = vector1.z
    x2 = vector2.x
    y2 = vector2.y
    z2 = vector2.z
    result = math.sqrt( ((x1 - x2)**2)+((y1 - y2)**2) + ((z1 - z2)**2) )
    #print "POINT 1: %d %d %d POINT 2:  %d %d %d DISTANCE: %d" % (x1, y1, z1, x2, y2, z2, result)
    return result

def getch():
    tty.setcbreak(sys.stdin)
    ch = (sys.stdin.read(1))
    
    return ch

button_delay = 0.2


def printFrameInfo(frame):
    frame = frame
    
    if not (frame.hands.is_empty):

        for hand in frame.hands:
            
            handType = "left_Hand" if hand.is_left else "rightHand"
            
            print "%f %f %f" % (
                                                hand.palm_position.x, hand.palm_position.y, hand.palm_position.z )
                
                
                
            
            # Get fingers
            for finger in hand.fingers:
                
            
                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    print "%f %f %f" % (
                                            
                                              bone.next_joint.x, bone.next_joint.y, bone.next_joint.z )






def getSign1(coords, fingers):
    #signs = dict.fromkeys(["isA", "isF", "isW", "isY", "isD"], False)
    isExtended = []
    if not (fingers):
        print "No hand detected."
        return
    #dFingers = dict(fingers)
    palmOpen = True
    isA = True
    statusExtended = False
    for a, f in fingers:
        statusExtended = False
        if not (f.is_extended):
            palmOpen = False
        if (f.is_extended):
            isA = False
            statusExtended = True
        isExtended.append((a, statusExtended))
    if (palmOpen and isExtended):
        print "Your palm is open... High five!"
        return
    if (isA):
        print "You signed an A"
        return
    isExtended = dict(isExtended) #make a dictionary from bools
    if (isExtended['T'] and not isExtended['I'] and not isExtended['M'] and not isExtended['R'] and  isExtended['P']):
        print "You signed a Y"
        return
    if (not isExtended['T'] and isExtended['I'] and isExtended['M'] and isExtended['R'] and not isExtended['P']):
        print "You signed a W"
        return
    if (not isExtended['T'] and not isExtended['I'] and isExtended['M'] and isExtended['R'] and  isExtended['P']):
        print "You signed an F"
        return
    if (not isExtended['T'] and  isExtended['I'] and not isExtended['M'] and not isExtended['R'] and not isExtended['P']):
        print "You signed a D"
        return
    if (not isExtended['T'] and not isExtended['I'] and not isExtended['M'] and not isExtended['R'] and  isExtended['P']):
        print "You signed an I"
        return
    print "You signed something else."
#if dFingers['T'].is_extended #Thumb is Extended




def getFingers(frame):
    finger_names = ['T', 'I', 'M', 'R', 'P']
    frame = frame
    result = []
    if not (frame.hands.is_empty):
        for hand in frame.hands:
            
            
            # Get fingers
            for finger in hand.fingers:
                #fingerLength = 0.0
                fingerName = finger_names[finger.type]
                
                
                result.append((fingerName, finger))

    return result

def getFingerLengths(frame):
    finger_names = ['T', 'I', 'M', 'R', 'P']
    frame = frame
    result = []
    fingerLength = 0.0
    if not (frame.hands.is_empty):
        for hand in frame.hands:
            
            
            
            # Get fingers
            for finger in hand.fingers:
                #fingerLength = 0.0
                fingerName = finger_names[finger.type]
                
                
                result.append((fingerName, finger.length))
    
            
        return result

def getCoordList(frame):
    finger_names = ['T', 'I', 'M', 'R', 'P']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    frame = frame
    result = []
    if not (frame.hands.is_empty):
        for hand in frame.hands:
            
            handType = "left_Hand" if hand.is_left else "rightHand"
            
            result.append((handType, hand.palm_position))
            
            
            
            # Get fingers
            for finger in hand.fingers:
                
                fingerName = finger_names[finger.type]
                
                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    result.append(
                                  (fingerName+"_"+ bone_names[bone.type],
                                   bone.next_joint))
        
            return result

# def printFrameInfo(Frame):


class SampleListener(Leap.Listener):
    finger_names = ['T', 'I', 'M', 'R', 'P']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal  ']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    first = False
    firstFrameId = 0
    mostRecentFrameId = 0
    
    
    def on_init(self, controller):
        print "Initialized"
        self.first = True
        self.firstFrameId = 0
        self.mostRecentFrameId = 0
    
    
    
    def on_connect(self, controller):
        print "Connected"
        
        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);
    
    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"
    
    def on_exit(self, controller):
        #print("First  frame: " + str(self.firstFrameId) + "\n")
        #self.printFrameInfo(self.firstFrameId)
        #print("Most recent frame: " + str(self.mostRecentFrameId))
        #self.printFrameInfo(self.mostRecentFrameId)
        print "EXIT"
    
    def on_frame(self, controller):
        
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        
        #if this is the first frame in this recording session, save this
        if (self.first):
            print("RECORDING... Hit space to get sign, d to print data, f to print data to file, and p to pause.")
            self.first = False
            self.firstFrameId = frame
        else:
            self.mostRecentFrameId = frame
            #print("Most recent frame: " + str(self.mostRecentFrameId))
            #self.printFrameInfo(self.mostRecentFrameId)


    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"
            
        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"
        
        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"
            
        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"
    


def isSteady(frameList=[], frameCount): 
     """isSteady function returns true if the hand is steady

    checks if the last (framecount) frames in the list (frameList) are about equal
    if so, the hand is steady, return true. otherwise return false.

    Parameters
    ----------
    frameList : list of frames
        list of recent frames, should have more than framecount
    frameCount : int
        number of frames to check

    Returns
    -------
    bool
        true if hand is steady, false otherwise.

    """
    for x in frameList:

    return True
    return False



def main():
    """Main Function, body of program"""
    paused = False
    recording = False

    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    frames = []
    frameCounter = 0 #current number of frames stored
    maxFrames = 10 # maximum number of frames to store


    myCoords = []
    fingerStatuses = []
    myFingerList = []
    i = 0
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S')
    
    # Have the sample listener receive events from the controller
    
    
    # ========================================================#
    #    Keep this process running until Enter is pressed     #
    #
    print "Press r to begin."
    #frame2 = controller.frame()
    try:
        ch = getch()
        while(not(ch == "q")):

            # RESUME/ PAUSE

            if (ch == "r" and not recording): #RESUME RECORDING
                print("Hit any key to resume recording. Hit p to pause")
                recording = True
            if (ch == "p"): #PAUSE RECORDING
                print("Hit r to resume.")
                paused = True
                controller.remove_listener(listener)
                recording = False


            # Get next frame, store in array at index frameCounter #
            frames[frameCounter] = controller.frame()

            if (frameCounter == maxFrames): ##if we already have 10 frames, delete the oldest
                del frames[0]
            else
                frameCounter++



            
            if (ch == "2" and recording): #PRINT FINGER STATUSES
                
                myFingerList = getFingers(frame2)
                printFingerStatuses(myFingerList, frame2.hands.frontmost);
            if (ch == "3" and recording): #PRINT FINGER COORDINATES AND LENGTH 
                myCoords = getCoordList(frame2)
                myFingerList = getFingers(frame2)
                if myFingerList:
                    for a, y in myFingerList:
                        print "%s length: %f" % (a, y.length)
                if myCoords:
                    for a, y in myCoords:
                        print "%s: (x: %f, y: %f, z: %f)" % (a, y.x, y.y, y.z)
            if (ch == " " and  recording): #PRINT CURRENT SIGN
                myCoords = getCoordList(frame2)
                myFingerList = getFingers(frame2)
                #fingerlengths = getFingerLengths(frame2)
                    #if myFingerList:
                    #for a, y in myFingerList:
                    #    print "%s length: %f" % (a, y.length)
                    #fingerStatus = getStatus(dict(myCoords), dict(fingerLengths), myFingerList)
                fingerStatuses = getFingerStatuses(myFingerList, frame2.hands.frontmost)
                #for a, f in fingerStatuses:
                    #  print "%s is %s" % (a,f)
                getSign(fingerStatuses, frame2.hands.frontmost)
                
            if (recording):
                controller.add_listener(listener)


            ch = getch()
        recording = False

    #                                                         #
    # ========================================================#

    except KeyboardInterrupt: 
        pass
    finally:
        controller.remove_listener(listener) #Remove the sample listener when done



if __name__ == "__main__":
  main()

