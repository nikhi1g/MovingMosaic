# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from threading import Thread
from time import sleep
from odrive.enums import *  # enumerations, enums, gives each sensor numbers
import odrive
import self as self
# buttons are actually buttons -1
from pidev.Joystick import Joystick
from ODrive_Ease_Lib import *

# variables
  # findodrive
odboard = odrive.find_any(serial_number='208D3388304B')
odboard.clear_errors()

# setup the Joystick



class Runner():
    joystick = Joystick(0, False)
    JoystickIsOn = False
    def start_joy_thread(self):
        self.JoystickIsOn = True
        print('Joystick thread Running')
        Thread(target=self.joy_update).start()

    def joy_update(self):
        speed = 1
        switch = 0
        while self.JoystickIsOn:
            x = self.joystick.get_axis('x')
            y = self.joystick.get_axis('y')
            if 0.2 > x > -0.2:#stops
                self.ax.set_vel(0)
                sleep(0.2)
            if y == 0: #should decel to a stop, but is does not
                self.ay.set_ramped_vel(0,8)
                sleep(0.3)
            if x > 0.2:#x actions
                self.ax.set_vel(speed)
                print('x pos:',self.joystick.get_axis('x'))
                sleep(0.2)
            if x < -0.2:#x actions
                self.ax.set_vel(-speed)
                print('x pos:',self.joystick.get_axis('x'))
                sleep(0.2)
            if y > 0.2:#y actions
                self.ay.set_vel(speed)
                print('y pos:',self.joystick.get_axis('y'))
                sleep(0.2)
            if y < -0.2:#y actions #dump errors and idel button
                self.ay.set_vel(-speed)
                print('y pos:',self.joystick.get_axis('y'))
                sleep(0.2)
            if self.joystick.get_button_state(4) == 1 and speed <= 7: #increase le speed
                speed += 1
                print('speed:',speed)
                sleep(0.2)
            if self.joystick.get_button_state(3) == 1 and speed > 1: #decrease le speed
                speed -= 1
                print('speed:',speed)
                sleep(0.2)
            #idlebutton
            if self.joystick.get_button_state(7) == 1:
                self.ax.idle()
                self.ay.idle()
                sleep(1)
            #dumperrorsbutton
            if self.joystick.get_button_state(8) == 1:
                dump_errors(odboard)
                sleep(0.5)
                odboard.clear_errors()
            if self.joystick.get_button_state(0) == 1: #triggerbutton
                if switch == 0:
                    self.ax.set_vel(speed)
                    switch = 1
                    sleep(0.2)
                elif switch == 1:
                    self.ax.set_vel(-speed)
                    switch = 0
                    sleep(0.2)
            if self.joystick.get_button_state(1) == 1:
                self.ax.set_vel(0)
                sleep(0.2)
                self.ay.set_vel(0)
                sleep(0.2)



    def onstartup(self):
            #dumperrors
            dump_errors(odboard)
            #define ax and ay
            self.ax = ODrive_Axis(odboard.axis0, 15, 10)  # currentlim, vlim
            self.ay = ODrive_Axis(odboard.axis1, 40, 10)  # currentlim, vlim
            #calibrate
            if not self.ax.is_calibrated():#calibrate x (left right)
                print("calibrating...")
                self.ax.calibrate_with_current(25)
            # if not self.ay.is_calibrated(): #calibrate y (top bottom)
            #     print("calibrating...")
            #     self.ay.calibrate_with_current(60)
            #odboard.save_configuration()
            #odboard.reboot()
            #COMMENCE THE GAINZ
            self.ax.set_pos_gain(20)
            self.ax.set_vel_gain(0.16)
            self.ax.set_vel_integrator_gain(0.32)
            self.ax.axis.controller.config.enable_overspeed_error = False
            odboard.clear_errors()

            self.ax.idle()
            self.ay.idle()

if __name__ == '__main__':
    r = Runner()
    r.onstartup()
    r.start_joy_thread()

# odrv0 208D3388304B
# odrv1 2065339E304B


# Odrv1 = odrive.find_any(serial_number=serial1)
# Odrv2 = odrive.find_any(serial_number=serial2)
