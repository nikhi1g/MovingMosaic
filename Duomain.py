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
odboard1 = odrive.find_any(serial_number='2065339E304B')
odboard1.clear_errors()
# setup the Joystick



class Runner():
    joystick = Joystick(0, False)
    JoystickIsOn = False
    Prox_Sensor_Number = 10000000
    SensingIsOn = False
    def start_joy_thread(self):
        self.JoystickIsOn = True
        print('Joystick thread Running')
        Thread(target=self.joy_update).start()

    def joy_update(self):
        speed = 1
        while self.JoystickIsOn:
            x = self.joystick.get_axis('x')
            y = self.joystick.get_axis('y')
            if 0.2 > x > -0.2:#stops
                self.ax.set_vel(0)
                sleep(0.2)
            if -0.2 < y < 0.2: #should decel to a stop, but is does not
                self.ay.set_ramped_vel(0,8)
                sleep(0.2)
                self.ay.idle()
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
            if self.joystick.get_button_state(1) == 1:
                self.ax.set_vel(0)
                sleep(0.2)
                self.ay.set_vel(0)
                sleep(0.2)
                self.az.set_vel(0)

    def start_prox_thread(self):  # thread checking gpio, sensing
        print('Starting Proximity Sensor Thread on GPIO', self.Prox_Sensor_Number)
        self.SensingIsOn = True
        Thread(target=self.prox_update).start()

    def prox_update(self):
        switch = 0
        print('Running Proximity Sensor Thread on GPIO', self.Prox_Sensor_Number)
        while self.SensingIsOn:
            # print(self.ax.axis.min_endstop.endstop_state, 'Prox_Sensor_State')
            # sleep(0.5)
            if self.joystick.get_button_state(0) == 1: #triggerbutton  FOR Z axis
                if switch == 0:
                    self.az.set_vel(2)
                    print('forwards')
                    switch = 1
                    sleep(0.1)
                elif switch == 1:
                    self.az.set_vel(-2)
                    print('backwards')
                    switch = 0
                    sleep(0.1)
            if self.az.axis.min_endstop.endstop_state:  # if switch, or in this case the prox is pressed
                # clear errors will get rid of freeze man
                print('Reached Prox on GPIO', self.Prox_Sensor_Number)
                dump_errors(odboard1)
                odboard1.clear_errors()
                self.az.set_vel(-1)
                sleep(0.2)
                # self.ax.axis.min_endstop.config.enabled = True
                self.az.set_vel(0)




    def onstartup(self):
            #dumperrors
            dump_errors(odboard)
            #define ax and ay
            self.ax = ODrive_Axis(odboard.axis0, 15, 10)  # currentlim, vlim
            self.ay = ODrive_Axis(odboard.axis1, 40, 10)  # currentlim, vlim
            self.az = ODrive_Axis(odboard1.axis0, 15, 10)
            #calibrate
            if not self.ax.is_calibrated():#calibrate x (left right)
                print("calibrating x...")
                self.ax.calibrate_with_current_lim(25)
            if not self.az.is_calibrated():#calibrate z (left right)
                print("calibrating z...")
                self.az.calibrate_with_current_lim(25)
            # if not self.ay.is_calibrated(): #calibrate y (top bottom)
            #     print("calibrating y...")
            #     self.ay.calibrate_with_current(60)
            #odboard.save_configuration()
            #odboard.reboot()
            #COMMENCE THE GAINZ
            self.ax.gainz(20,0.16,0.32,False)
            self.az.gainz(20,0.16,0.32,False)
            odboard.clear_errors()

            self.ax.idle()
            self.ay.idle()
            self.az.idle()


        #PROXSENSOR
            axisshortcut = self.az.axis  # shortcut

            # homing_sensor_prox
            odboard1.config.gpio8_mode = GPIO_MODE_DIGITAL
            axisshortcut.min_endstop.config.gpio_num = 2  # pin 8 for x, 2 for y, 2 for z
            self.Prox_Sensor_Number = axisshortcut.min_endstop.config.gpio_num  # setting to global class Runner variable just so that I can reference it in the Thread print statements
            axisshortcut.min_endstop.config.enabled = True  # Turns sensor on, says that I am using it
            axisshortcut.min_endstop.config.offset = 1  # stops 1 rotation away from sensor
            axisshortcut.min_endstop.config.debounce_ms = 20  # checks again after 20 milliseconds if actually pressed, which is what debounce is :D
            axisshortcut.min_endstop.config.offset = -1.0 * (8192)  # hop back from GPIO in order to allow for function again
            odboard1.config.gpio8_mode = GPIO_MODE_DIGITAL_PULL_DOWN

if __name__ == '__main__':
    r = Runner()
    r.onstartup()
    r.start_joy_thread()
    r.start_prox_thread()

# odrv0 208D3388304B
# odrv1 2065339E304B


# Odrv1 = odrive.find_any(serial_number=serial1)
# Odrv2 = odrive.find_any(serial_number=serial2)
