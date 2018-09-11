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
import Leap, sys, thread, time, termios, tty, os, datetime
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture



def getch():
    tty.setcbreak(sys.stdin)
    ch = (sys.stdin.read(1))
    
    return ch

button_delay = 0.2



def printFrameInfo(frame):
    frame = frame
    finger_names = ['T', 'I', 'M', 'R', 'P']
    bone_names = ['metacarpal', 'proximal', 'intermediate', 'distal']
        
        
    for hand in frame.hands:
        
        handType = "left_Hand" if hand.is_left else "rightHand"
        
        print "\b%s_position %i %i %i\b" % (
                                      handType, hand.palm_position.x, hand.palm_position.y, hand.palm_position.z )
            

    
    
        # Get fingers
        for finger in hand.fingers:
            
            fingerName = finger_names[finger.type]
            
            # Get bones
            for b in range(0, 4):
                bone = finger.bone(b)
                print "%s_%s %i %i %i" % (
                                    fingerName,          bone_names[bone.type],
                                    bone.next_joint.x, bone.next_joint.y, bone.next_joint.z )
        
        
        
        if not (frame.hands.is_empty):
            print ""



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
        self.printFrameInfo(self.mostRecentFrameId)
        #print "PAUSED"
    
    def on_frame(self, controller):
        
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        
        #if this is the first frame in this recording session, save this
        if (self.first):
            print("RECORDING... Hit d to print frame data to file...")
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
            
            if (ch == "p"):
                print("Hit r to resume.")
                paused = True
                controller.remove_listener(listener)
                recording = False
            if (ch == "d" and  recording):
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

