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
import numpy as np
import numpy.linalg 
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

#margin of error used for comparing distances to detect finger status
thumbExtendedMargin = 70 #if angle between thumb and palm is > this, thumb is extended
extendedMargin = 9
thumbStraightMargin = 30
Vmargin = 30
touchingMargin = 10
tipTouchingMargin = 30
straightOutMargin = 30
curledMargin = 3
downMargin = 10
maxFrames = 10      # maximum number of frames to store
maxDistance = 2 # max distance between steady frames

def getSign(fingers, hand, anglesToPalm, fingerAngles, thumbFingersTouching):
    angleToPalmOf = dict(anglesToPalm) #make a dictionary with angles from fingers to palm
    angleBetween = dict(fingerAngles) #Returns dict with angles in this order: ['TI', 'IM', 'MR', 'RP']
    statusOf = dict(fingers) #make a dictionary with finger initials as keys
    if not (statusOf):
        print "I can't see your full hand!"
        return
    if (statusOf['P'] == 'curled' and statusOf['M'] != 'extended'): #PINKY IS CURLED.
            print "You signed an E"
            return
    if (statusOf['P'] == 'bent' or statusOf['P'] == 'straightOut'): #PINKY IS BENT. D O C
        if (statusOf['R'] == 'extended' and statusOf['T'] != 'extended'):
            print "You signed a W"
            return
        else:
            if (statusOf['I'] == 'extended'):
                if (statusOf['T'] == 'extended'):
                    print "You signed an L"
                    return
                if (statusOf['T'] == 'down'):
                    print "You signed a D"
                    return
            elif (statusOf['M'] != 'extended'):
                if (thumbFingersTouching):
                    print "You signed an O" 
                else:
                    print "You signed a C" 
        return
    elif(statusOf['P'] == 'down' or statusOf['P'] == 'bent'): #PINKY IS DOWN OR BENT
        #CHECK MIDDLE FINGER STATUS
        if (statusOf['M'] == 'down'):
            if (statusOf['I'] == 'extended' and statusOf['T'] == 'extended'):
                print "You signed an L"
                return
            elif (statusOf['I'] == 'down' or statusOf['I'] == 'curled'): #all fingers down
                if (statusOf['T'] == 'down'):
                    print "You signed an S" #or  a T
                    return
                else:
                    print "You signed an A"
                    return
            elif (angleToPalmOf['I'] < 80): #finger is curled
                print "You signed an X"
                return
            else:
                print "You signed a D"
                return
        elif (statusOf['M'] == 'bent'):
            print "You signed a K, M, or N. I can't tell yet!"
            return
        elif (statusOf['M'] == 'extended'):
            if (statusOf['I'] == 'extended' ):
                if (angleBetween['IM'] > Vmargin):
                    print "You signed a V"
                    return
                if (angleBetween['IM'] < touchingMargin):
                    print "You signed a U"
                    return
                else:
                    print "You signed an R"
                    return
            elif(statusOf['R'] != 'extended'):
                print "Peace among worlds!"
        return
    elif(statusOf['P'] == 'extended'): #PINKY IS EXTENDED
        if (statusOf['R'] == 'extended'): #RING IS EXTENDED
            if (statusOf['I'] == 'extended'): #INDEX IS EXTENDED
                     if (statusOf['T'] == 'down' and angleBetween['IM'] <= (touchingMargin+10) ): #THUMB IS DOWN AND FINGERS ARE CLOSE
                        print "You signed a B"
                        return
                     else:
                        print "That's an open palm. High five!"
                        return
            else: #INDEX IS NOT EXTENDED
                print "You signed an F"
                return
        else: #RING IS NOT EXTENDED
            if (statusOf['T'] == 'extended' ): #THUMB EXTENDED
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

def getFingerStatuses(fingers, hand, printRequested):
    
    result = []
    status = 'unknown'
    angles = dict(anglesToPalm(fingers, hand, False))
    
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
            thumbHandAngle = (180*((f.direction.angle_to(hand.direction)))/np.pi)
            if (printRequested):
                print "thumbHandAngle : %f" % thumbHandAngle
            if (angles[a] > thumbExtendedMargin):
                
                status = 'extended' #the finger is  extended
                
            else:
                status = 'bent'

                if (thumbHandAngle < thumbStraightMargin):
                        status = 'straight'
                elif ((intToPalm-proxToPalm) < downMargin): #if middle of thumb is closer to palm than base of thumb
                        status = 'down'


        #for all fingers except the thumb
        else:
            #finger to hand
            fingerHandAngle = (180*((f.direction.angle_to(hand.direction)))/np.pi)
            #if the tip of the finger is farther than the estimated length by a certain margin,
            if ((tipToPalm - fullLength) > extendedMargin):
                
                
                status = 'extended' #the finger must be extended
                
                #otherwise, the finger is curled or down (as in a fist)
            else:
                #print "tip to palm - short length %f" % (tipToPalm - shortLength)
                status = 'bent'
                #if the tip is substantially closer to the palm than the finger center is
                if ((tipToPalm - intToPalm) < curledMargin):
                    status = 'curled'
                if ((tipToPalm - shortLength) < downMargin):
                    status = 'down'
                elif ((angles[a] < straightOutMargin) and (fingerHandAngle > 70)):
                    if (printRequested):
                        print "fingerHandAngle: %f" % fingerHandAngle

                #if the finger to palm angle is small and the finger to hand direction is large, then the finger is probably pointing straight out.
                    status = 'straightOut'

        result.append((a, status))
    return result

def isTouching(myCoords, bone1, bone2, printRequested):
    coords = dict(myCoords)
    thisDistance = coords[bone1].distance_to(coords[bone2]);
    if (printRequested):
            print "this Distance: %f" % thisDistance
    if (thisDistance < tipTouchingMargin):
        if (printRequested):
            print "touching"
        return True

    if(printRequested):
        print "not touching"
    return False


def anglesToPalm(fingers, hand, printRequested):
    #compares angles of fingers to normal direction of palm (that is, a vector pointing straight out of the palm)
    #Returns array with angles in this order:
    #thumb and palm, index and palm, middle and palm, ring and palm, pinky and palm
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    angle_names = ['T', 'I', 'M', 'R', 'P']
    status = 'unknown'
    first = True;
    result = []
    if (printRequested):
        print "ANGLES FROM EACH FINGER TO PALM:"

    for a, f in fingers:
        vectorA = f.direction
        vectorB = hand.palm_normal
        myAngle = 180*(vectorA.angle_to(vectorB))/np.pi
        if (printRequested):
            print "angle %s is %f" % (angle_names[f.type], myAngle)
        result.append((angle_names[f.type], myAngle))
    if (printRequested):
       print "ANGLE TO DOWN AXIS: %f" % (180*(hand.palm_normal.angle_to(Leap.Vector.down))/np.pi)
       print "ROLL: %f" % (180*(hand.direction.roll)/np.pi)
    return result;
    
def getFingerAngles(fingers,hand, printRequested):
    #Returns array with angles in this order:
    #thumb and index, index and middle, middle and ring, ring and pinky
    finger_names = ['T', 'I', 'M', 'R', 'P']
    angle_names = ['TI', 'IM', 'MR', 'RP']
    status = 'unknown'
    first = True;
    result = []

    for a, f in fingers:
        if (first):
            lastFinger = f;
            lastFingerName = finger_names[f.type];
            first = False
        else: #find the angle between the last finger and the current finger
            vectorA = lastFinger.direction
            vectorB = f.direction
            myAngle = 180*(vectorA.angle_to(vectorB))/np.pi
            if (printRequested):
                print "angle %s is %f" % (angle_names[f.type-1], myAngle)
            lastFinger = f;
            lastFingerName = finger_names[f.type]
            result.append((angle_names[f.type-1], myAngle))

    anglesToPalm(fingers, hand, printRequested)
    return result;
        

def printFingerStatuses(fingers, hand):
    
    status = 'unknown'
    angles = dict(anglesToPalm(fingers, hand, False))
    
    for a, f in fingers:
        shortLength = f.length
        metacarpalLength = f.bone(0).length
       # print "%d short length" % shortLength
        fullLength = shortLength + (metacarpalLength/2)
       # print "%d full length" % fullLength
      #  
        
        tipToPalm = getDistance(f.bone(3).next_joint, hand.palm_position) #distance from finger tip to palm
        print "%d tip to palm " % tipToPalm
        intToPalm = getDistance(f.bone(2).center, hand.palm_position) #distance from finger center to palm
       # print "%d int to palm" % intToPalm
        proxToPalm = getDistance(f.bone(1).center, hand.palm_position)
       # print "%d proximal distance" % proxToPalm
        
        
        ##DECIDE FINGER STATUS
        #special logic for thumb
        if (a == 'T'):
            thumbHandAngle = (180*((f.direction.angle_to(hand.direction)))/np.pi)
            print "thumbHandAngle : %f" % thumbHandAngle
            if (angles[a] > thumbExtendedMargin):
                
                status = 'extended' #the finger is  extended
                
            else:
                status = 'bent'

            if (thumbHandAngle < thumbStraightMargin):
                    status = 'straight'
            elif ((intToPalm-proxToPalm) < downMargin): #if middle of thumb is closer to palm than base of thumb
                    status = 'down'


        #for all fingers except the thumb
        else:
            #finger to hand
            fingerHandAngle = (180*((f.direction.angle_to(hand.direction)))/np.pi)
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
                if ((angles[a] < straightOutMargin) and (fingerHandAngle > 70)):

                #if the finger to palm angle is small and the finger to hand direction is large, then the finger is probably pointing straight out.
                    status = 'straightOut'
        
        print "%s is %s\n=========\n" % (a,status)



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

    frames = []
        

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
            print("RECORDING... Hit space to get sign, 2 to print data, 3 to print finger length/coordinates, f to print data to file, and p to pause.")
            self.first = False
            self.firstFrameId = frame
        else:
            self.mostRecentFrameId = frame
            self.frames.append(frame)
            if (len(self.frames) > maxFrames):
                del self.frames[0] #delete the oldest
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
    
def framesEqual(frame1, frame2): 
    """framesEqual() function returns true if the 2 frames are about equal

        takes 2 frames and checks each finger (each frame should only have 1 hand)

        Parameters
        ----------
        frame1: frame
            first frame
        frame2: frame
            second frame to compare

        Returns
        -------
        bool
            true if frames are about equal, false if not
        """
    if (frame1.fingers.is_empty or frame2.fingers.is_empty):
        return False

    for finger_type in range(0,5): #iterates from 0(TYPE_THUMB) to 4 (TYPE_PINKY):
        group1 = getFingers(frame1)
        group2 = dict(getFingers(frame2)) 

        if(len(group1) != len(group2)): #if one frame has more fingers than the other frame
            print f.stabilized_tip_position
            return False

        for a,f in group1:
            distance = (f.stabilized_tip_position).distance_to(group2[a].stabilized_tip_position)
            if (distance >= maxDistance):
                return False


    return True


def isSteady(frameList, frameCount): 
    """ isSteady function returns true if the hand is steady

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
    total = len(frameList)

    frame1 = frameList[total - frameCount] #first frame that we want to check
    i = (total - frameCount + 1)           #index of the frame after that one
    frame2 = frameList[i]

    for x in range(i, frameCount):          #iterate through the selected frames

        if (not(framesEqual(frame1, frame2))): #if they're not about equal,
            print "NOT STEADY"
            return False                    #then quit
        frame1 = frame2                     #otherwise, iterate to the next 2 frames.
        frame2 = frameList[x]
    #print "STEADY"
    return True                             #return true if you get through the entire loop 



def isSteady(listener):
    if (framesEqual(listener.frames[-1], listener.frames[-2]) and framesEqual(listener.frames[-2], listener.frames[-3])):
        return True
    return False
#######################################################

def main():
    """Main Function, body of program"""
    paused = False
    recording = False

    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    frames = []         # list, store recent frames
    frameCounter = 0    # current number of frames stored



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


            #---------------
            # q     -> quits program
            # r     -> resume recording 
            # p     -> pause recording

            if ((ch == "r" or ch == "R") and not recording):   #RESUME RECORDING
                print("Hit any key to resume recording. Hit p to pause")
                recording = True

            if (ch == "p"):                     #PAUSE RECORDING
                print("Hit r to resume.")
                paused = True
                controller.remove_listener(listener)
                recording = False

            #--------------------
            # Get next frame, store in array at index frameCounter #
            frames.append(controller.frame())

            if (not len(frames) >= maxFrames): ##if we already have 10 frames, delete the oldest   
                frameCounter += 1
            else:      
                del frames[0]

            mostRecentFrame = frames[frameCounter-1]

            



            #---------------
            # OTHER OPTIONS:
            # 2         -> prints finger lengths, statuses, and distances from palm
            # 3         -> prints finger coordinates and length
            # 4         -> prints finger angles between each other and palm
            # spacebar  -> manually sends frame, checks for a sign


            if (ch == "2" and recording): #PRINT FINGER STATUSES
                
                myFingerList = getFingers(mostRecentFrame)
                printFingerStatuses(myFingerList, mostRecentFrame.hands.frontmost);
            if (ch == "3" and recording): #PRINT FINGER COORDINATES AND LENGTH 
                myCoords = getCoordList(mostRecentFrame)
                myFingerList = getFingers(mostRecentFrame)
                if myFingerList:
                    for a, y in myFingerList:
                        print "%s length: %f" % (a, y.length)
                if myCoords:
                    for a, y in myCoords:
                        print "%s: (x: %f, y: %f, z: %f)" % (a, y.x, y.y, y.z)
            if (ch == "4" and recording): #PRINT FINGER ANGLES
                print "FINDING ANGLES..."
                myFingerList = getFingers(mostRecentFrame)
                getFingerAngles(myFingerList, mostRecentFrame.hands.frontmost, True);
            
            #~ GET SIGN ~#
            if (ch == " " and  recording): #PRINT CURRENT SIGN
                if (isSteady(listener)):
                    myCoords = getCoordList(mostRecentFrame)
                    myFingerList = getFingers(mostRecentFrame)
                    myHand = mostRecentFrame.hands.frontmost
                    fingerStatuses = getFingerStatuses(myFingerList, myHand, False)

                    getSign(fingerStatuses, mostRecentFrame.hands.frontmost, anglesToPalm(myFingerList, myHand, False), getFingerAngles(myFingerList,myHand, False), isTouching(myCoords, 'T_Distal', 'M_Distal', False))
                else:
                    print "Hand is unsteady."
            if (ch == "\n" and  recording):
                if (isSteady(listener)):
                    print "STEADY"
                else:
                    print "NOT STEADY"

            if(recording):
                controller.add_listener(listener)
                


            ch = getch()

        recording = False

    #                                                         #
    # ========================================================#

    except KeyboardInterrupt: 
        os.system("stty echo")
        pass
    finally:
        os.system("stty echo")
        controller.remove_listener(listener) #Remove the sample listener when done



if __name__ == "__main__":
  main()

