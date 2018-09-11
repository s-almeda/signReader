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

import Leap, sys, thread, time, termios, tty, os
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture



def getch():
    tty.setcbreak(sys.stdin)
    ch = (sys.stdin.read(1))
    
    return ch

button_delay = 0.2


# def printFrameInfo(Frame):


class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'DISTAL:  ']
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
        print("First  frame: " + str(self.firstFrameId) + "\n")
        self.printFrameInfo(self.firstFrameId)
        print("Most recent frame: " + str(self.mostRecentFrameId))
        self.printFrameInfo(self.mostRecentFrameId)
        print "PAUSED"
    
    def on_frame(self, controller):
        
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        
        #if this is the first frame in this recording session, save this
        if (self.first):
            print("RECORDING... Hit d to print frame data...")
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

'''def getFrameDifference(self, frame1, frame2):
    frame1 = frame1
    frame2 = frame2
    print "Frame 1 id: %d, timestamp: %d" %(frame1.id, frame1.timestamp)
    print "Frame 2 id: %d, timestamp: %d" %(frame2.id, frame2.timestamp)
    # Get hands
    for hand in frame1.hands:
    handType = "Left hand" if hand.is_left else "Right hand"
    print "  %s, id %d, position: %s" % (handType, hand.id, hand.palm_position)
    
    # Get the hand's normal vector and direction
    normal = hand.palm_normal
    direction = hand.direction
    
    
    
    # Get fingers
    for finger in hand.fingers:
    
    print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
    self.finger_names[finger.type],
    finger.id,
    finger.length,
    finger.width)
    
    # Get bones
    for b in range(0, 4):
    bone = finger.bone(b)
    print "      Bone: %s, start: %s, end: %s, direction: %s" % (
    self.bone_names[bone.type],
    bone.prev_joint,
    bone.next_joint,
    bone.direction)
    
    
    
    if not (frame.hands.is_empty):
    print ""'''
        
        def printFrameInfo(self, frame):
        frame = frame
            print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" %(frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))
            # Get hands
            for hand in frame.hands:

handType = "Left hand" if hand.is_left else "Right hand"
    
    print "  %s, id %d, position: %s" % (
                                         handType, hand.id, hand.palm_position)
        
        # Get the hand's normal vector and direction
        normal = hand.palm_normal
            direction = hand.direction
                
                # Calculate the hand's pitch, roll, and yaw angles
                print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (direction.pitch * Leap.RAD_TO_DEG, normal.roll * Leap.RAD_TO_DEG, direction.yaw * Leap.RAD_TO_DEG)
                
                # Get arm bone
                arm = hand.arm
                    print "  Arm direction: %s, wrist position: %s, elbow position: %s" % (
                                                                                           arm.direction,
                                                                                           arm.wrist_position,
                                                                                           arm.elbow_position)
                
                # Get fingers
                for finger in hand.fingers:
                    
                    print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
                                                                                self.finger_names[finger.type],
                                                                                finger.id,
                                                                                finger.length,
                                                                                finger.width)
                        
                        # Get bones
                        for b in range(0, 4):
                            bone = finger.bone(b)
                                print "      Bone: %s, start: %s, end: %s, direction: %s" % (
                                                                                             self.bone_names[bone.type],
                                                                                             bone.prev_joint,
                                                                                             bone.next_joint,
                                                                                             bone.direction)
                
                
                
                if not (frame.hands.is_empty):
                    print ""
                                         
def printFrameDistance(self, frame):
    frame = frame
        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" %(frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))
        # Get hands
        for hand in frame.hands:
            # Get the hand's normal vector and direction
            normal = hand.palm_normal
                direction = hand.direction
            
            for finger in hand.fingers:
                
                print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
                                                                            self.finger_names[finger.type],
                                                                            finger.id,
                                                                            finger.length,
                                                                            finger.width)
                                                                            
                                                                            # Get bones
                                                                            for b in range(0, 4):
                                                                                bone = finger.bone(b)
                                                                                print "      Bone: %s, start: %s, end: %s, direction: %s" % (
                                                                                                                                             self.bone_names[bone.type],
                                                                                                                                             bone.prev_joint,
                                                                                                                                             bone.next_joint,
                                                                                                                                             bone.direction)
            
            
            
            if not (frame.hands.is_empty):
                print ""

def main():
    
    recording = False
    paused = False
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()
    frame1 = 0
    frame2 = 0
    
    # Have the sample listener receive events from the controller
    
    
    # Keep this process running until Enter is pressed
    print "Press r to begin."
    frame2 = controller.frame()
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
                frame2 = controller.frame()
                (controller.getFrameDifference(frame1, frame2))
            
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
