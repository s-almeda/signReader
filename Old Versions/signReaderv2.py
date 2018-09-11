################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
#
#   written by Sarah Almeda at The College of New Jersey 2/2018
#
################################################################################
from __future__ import with_statement
import Leap, sys, thread, time, termios, tty, os, datetime, math
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture


def getSign(fingers, hand):
    statuses = dict(fingers) #make a dictionary with finger initials as keys

def getFingerStatuses(fingers, hand):
    
    result = []
    status = 'unknown'
    
    for a, f in fingers:
        length = f.length
        metacarpalLength = f.bone(0).length
        print "finger length: %d" % length
        distanceFromPalm = getDistance(f.bone(3).center, hand.palm_position)
        if (abs(distanceFromPalm - length) > 25):
           
            status = 'extended'
        
        
        else:
            status = 'bent'
            #elif distanceFromProximal < (length/3):
            #status = 'curled'
            if (distanceFromPalm <= length) or (abs(distanceFromPalm - length) < 5):
                status = 'down'
                    #print ("%s is %s") % (a, status)
        result.append((a, status))
    return result


def getDistance(vector1, vector2):
    x1 = vector1.x
    y1 = vector1.y
    z1 = vector1.z
    x2 = vector2.x
    y2 = vector2.y
    z2 = vector2.z
    result = math.sqrt( ((x1 - x2)**2)+((y1 - y2)**2) + ((z1 - z2)**2) )
    print "POINT 1: %d %d %d POINT 2:  %d %d %d DISTANCE: %d" % (x1, y1, z1, x2, y2, z2, result)
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



#def getStatus(coords, lengths, fingers):
#   finger_names = ['T', 'I', 'M', 'R', 'P']
#   bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
#   isExtended = 0
#   for finger in fingers:



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
    



def main():
    paused = False
    recording = False
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()
    frame1 = 0
    frame2 = 0
    myCoords = []
    fingerStatuses = []
    myFingerList = []
    i = 0
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S')
    
    # Have the sample listener receive events from the controller
    
    
    # Keep this process running until Enter is pressed
    print "Press r to begin."
    #frame2 = controller.frame()
    try:
        ch = getch()
        while(not(ch == "q")):
            if (ch == "r" and not recording):
                print("Hit any key to resume recording. Hit p to pause")
                recording = True
            if (ch == "f"):
                frame1 = frame2;
                
                orig_stdout = sys.stdout
                fileName = st + str(i) + ".txt"
                i += 1
                f = open(fileName, "w")
                sys.stdout = f
                frame2 = controller.frame()
                printFrameInfo(frame2)
                sys.stdout = orig_stdout
                f.close()
                print "printed to file %s" % fileName
            if (ch == "p"):
                print("Hit r to resume.")
                paused = True
                controller.remove_listener(listener)
                recording = False
            if (ch == "d" and recording):
                frame1 = frame2;
                frame2 = controller.frame()
                myCoords = getCoordList(frame2)
                myFingerList = getFingers(frame2)
                if myFingerList:
                    for a, y in myFingerList:
                        print "%s length: %f" % (a, y.length)
                if myCoords:
                    for a, y in myCoords:
                        print "%s: (x: %f, y: %f, z: %f)" % (a, y.x, y.y, y.z)
            if (ch == " " and  recording):
                frame1 = frame2;
                frame2 = controller.frame()
                myCoords = getCoordList(frame2)
                myFingerList = getFingers(frame2)
                #fingerlengths = getFingerLengths(frame2)
                    #if myFingerList:
                    #for a, y in myFingerList:
                    #    print "%s length: %f" % (a, y.length)
                    #fingerStatus = getStatus(dict(myCoords), dict(fingerLengths), myFingerList)
                fingerStatuses = getFingerStatuses(myFingerList, frame2.hands.frontmost)
                for a, f in fingerStatuses:
                       print "%s is %s" % (a,f)
                getSign(fingerStatuses, frame2.hands.frontmost)
                
            if (recording):
                controller.add_listener(listener)


            ch = getch()
        recording = False

    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)



if __name__ == "__main__":
  main()

