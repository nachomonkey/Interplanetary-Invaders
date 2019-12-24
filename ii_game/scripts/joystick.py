import pygame
import copy

pygame.init()
pygame.joystick.init()


# Button Codes for XBOX 360 controller:
# A:     0
# B:     1
# X:     2
# Y:     3
# Back:  6
# Start: 7

class JoystickState:
    def __init__(self):
        self.joystick_down = False
        self.joystick_up = False
        self.joystick_left = False
        self.joystick_right = False
        self.joystick_half_down = False
        self.X_val = 0
        self.A = False
        self.B = False
        self.X = False
        self.Y = False
        self.Back = False
        self.Start = False
        self.LT_val = -1
        self.RT_val = -1
        self.LT = False
        self.RT = False
        self.LB = False
        self.RB = False

    def is_X_anywhere(self):
        return self.X_val > .15 or self.X_val < -.15

    def TransferFrom(self, Other):
        for X in Other.__dict__:
            self.__dict__[X] = copy.copy(Other.__dict__[X])

    def __str__(self):
        return f"<JoystickState L={self.joystick_left} R={self.joystick_right} U={self.joystick_up} D={self.joystick_down} A={self.A} B={self.B} X={self.X} Y={self.Y} Bk={self.Back} Srt={self.Start} LT={self.LT_val} RT={self.RT_val} RB={self.RB} LB={self.LB}>"

hasJoystick = False
Joystick = None
CurrentState = JoystickState()
OldState = JoystickState()
name = ""

try:
    Joystick = pygame.joystick.Joystick(0)
    Joystick.init()
    name = Joystick.get_name()
    hasJoystick = True
except:
    print("No joysticks detected")

def IsSupported():
    if (not ("x" in name and "box" in name.lower())):
        return False
    return True

def Update(event):
    OldState.TransferFrom(CurrentState)
    if event.type == pygame.JOYBUTTONDOWN:
        if event.button == 0:
            CurrentState.A = True
        if event.button == 1:
            CurrentState.B = True
        if event.button == 2:
            CurrentState.X = True
        if event.button == 3:
            CurrentState.Y = True
        if event.button == 4:
            CurrentState.LB = True
        if event.button == 5:
            CurrentState.RB = True
        if event.button == 6:
            CurrentState.Back = True
        if event.button == 7:
            CurrentState.Start = True
    if event.type == pygame.JOYBUTTONUP:
        if event.button == 0:
            CurrentState.A = False
        if event.button == 1:
            CurrentState.B = False
        if event.button == 2:
            CurrentState.X = False
        if event.button == 3:
            CurrentState.Y = False
        if event.button == 4:
            CurrentState.LB = False
        if event.button == 5:
            CurrentState.RB = False
        if event.button == 6:
            CurrentState.Back = False
        if event.button == 7:
            CurrentState.Start = False
    if event.type == pygame.JOYAXISMOTION:
        if event.axis == 0:
            CurrentState.X_val = event.value
            if event.value <= -.7:
                CurrentState.joystick_left = True
            if event.value > -.7:
                CurrentState.joystick_left = False

            if event.value >= .7:
                CurrentState.joystick_right = True
            if event.value < .7:
                CurrentState.joystick_right = False
        if event.axis == 1:
            if event.value <= -.7:
                CurrentState.joystick_up = True
            if event.value > -.7:
                CurrentState.joystick_up = False

            if event.value >= .35:
                CurrentState.joystick_half_down = True
            if event.value < .35:
                CurrentState.joystick_half_down = False

            if event.value >= .7:
                CurrentState.joystick_down = True
            if event.value < .7:
                CurrentState.joystick_down = False
        if event.axis == 2:
            CurrentState.LT_val = event.value
            if event.value >= .75:
                CurrentState.LT = True
            if event.value < .75:
                CurrentState.LT = False
        if event.axis == 5:
            CurrentState.RT_val = event.value
            if event.value >= .75:
                CurrentState.RT = True
            if event.value < .75:
                CurrentState.RT = False

def StartEvent(attr_name):
    if (getattr(CurrentState, attr_name, False) and not getattr(OldState, attr_name, False)):
        return True
    return False

def EndEvent(attr_name):
    if (not getattr(CurrentState, attr_name, False) and getattr(OldState, attr_name, False)):
        return True
    return False

def JustWentLeft():
    return StartEvent("joystick_left")

def JustWentRight():
    return StartEvent("joystick_right")

def JustWentUp():
    return StartEvent("joystick_up")

def JustWentDown():
    return StartEvent("joystick_down")

def JustPressedA():
    return StartEvent("A")

def JustPressedB():
    return StartEvent("B")

def JustPressedX():
    return StartEvent("X")

def JustPressedY():
    return StartEvent("Y")

def JustPressedStart():
    return StartEvent("Start")

def JustPressedBack():
    return StartEvent("Back")

def JustPressedLT():
    return StartEvent("LT")

def JustPressedLB():
    return StartEvent("LB")

def JustPressedRT():
    return StartEvent("RT")

def JustPressedRB():
    return StartEvent("RB")

def JustWentHalfDown():
    return StartEvent("joystick_half_down")

def JustStoppedHalfDown():
    return EndEvent("joystick_half_down")

def BackEvent():
    return JustPressedBack() or JustPressedB()

def GoEvent():
    return JustPressedA() or JustPressedStart()
 
def WasEvent():
    return JustWentLeft() or JustWentRight() or JustWentUp() or JustWentDown() or JustPressedA() or JustPressedB() or JustPressedX() or JustPressedY() or JustPressedStart() or JustPressedBack() or JustPressedRT() or JustPressedLT() or GoEvent() or JustPressedLB() or JustPressedRB() or JustWentHalfDown() or JustStoppedHalfDown() or EndEvent("A")

def Reset():
    CurrentState.TransferFrom(JoystickState())
    OldState.TransferFrom(JoystickState())
