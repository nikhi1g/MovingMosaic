# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from threading import Thread
from time import sleep
from odrive.enums import *#enumerations, enums, gives each sensor numbers
import odrive
import self as self
 # buttons are actually buttons -1
from pidev.Joystick import Joystick

import ODrive_Ease_Lib
#variables
od = odrive.find_any()#findodrive

od.clear_errors()


#setup the Joystick

joystick = Joystick(0, False)

class Runner():
    JoystickIsOn = False
    SensingIsOn = False
    Endstop = False
    switch = 0
    Prox_Sensor_Number = 10000000
    od = odrive.find_any()
    whichaxis = 'eeee'#creates an axis
    def start_prox_thread(self):#thread checking gpio, sensing
        print('Starting Proximity Sensor Thread on GPIO', self.Prox_Sensor_Number)
        self.SensingIsOn = True
        Thread(target = self.prox_update).start()
    def prox_update(self):
        print('Running Proximity Sensor Thread on GPIO', self.Prox_Sensor_Number)
        while self.SensingIsOn:
            # print(self.ax.axis.min_endstop.endstop_state, 'Prox_Sensor_State')
            # sleep(0.5)
            if self.ax.axis.min_endstop.endstop_state: #if switch, or in this case the prox is pressed
                #clear errors will get rid of freeze man
                print('Reached Prox on GPIO',self.Prox_Sensor_Number)
                od.clear_errors()
                self.ax.set_vel(-1)
                sleep(0.2)
                # self.ax.axis.min_endstop.config.enabled = True
                self.ax.set_vel(0)


            if not self.ax.axis.min_endstop.endstop_state:# if switch,or in this case the prox is not pressed
                print('GPIO',self.Prox_Sensor_Number,'Not Reached')
                sleep(4)
    def start_joy_thread(self):
        print("Starting Joystick Thread")
        self.JoystickIsOn = True
        Thread(target = self.joy_update).start()

    def joy_update(self):
        #sleep_implementation: sleep is used here to cause a delay between the button joystick pressed and the command executed, otherwise commands are repeated multiple times
        #self.PrintPosition()
        print("Running Joystick Thread")

        sped = 0
        rawpos = self.ax.get_raw_pos()
        if self.JoystickIsOn:
            print("Joystick is On")
        while self.JoystickIsOn:#previously True to avoid errors
            if joystick.get_button_state(0) == 1 and 10 > rawpos > -3.7: #Trigger Button
                print(self.ax.get_pos())
                time1 = 0.15
                if self.switch == 0: #left?in?
                    self.ax.set_vel(sped)
                    self.switch = 1
                    sleep(time1)
                elif self.switch == 1: #out?
                    self.ax.set_vel(-sped)
                    self.switch = 0
                    sleep(time1)
            #attempt to set limits
                #positionlimit
            if rawpos < -3.7:
                self.ax.set_vel(4)
                sleep(0.5)
                self.ax.set_vel(0)
            if rawpos > 10:
                self.ax.set_vel(-4)
                sleep(0.5)
                self.ax.set_vel(0)
                #speed control and limiter
            if joystick.get_button_state(2) == 1:
                self.ax.set_vel(0)
                print('Stopped')
                print(self.ax.get_raw_pos())
            if joystick.get_button_state(3) == 1 and sped > 1:#left button on top
                sped -= 1 #decrease speed
                sleep(0.3)
            if joystick.get_button_state(4) == 1 and sped < 14:# right button on top
                sped += 1 #increase speed
                sleep(0.3)

            if joystick.get_button_state(9) == 1: #button 10
                #print('Erasing current configuration')
                #od.erase_configuration()
                print('Save configuration and reboot')
                od.save_configuration()
                print('Saving Configuration...')
                sleep(4)
                od.reboot()
                print('rebooting...')



    def onstartup(self):
        ODrive_Ease_Lib.dump_errors(od)
        od.clear_errors()
        self.ax = ODrive_Ease_Lib.ODrive_Axis(od.axis0, 10, 15)#currentlim, vlim

        axisshortcut = self.ax.axis#shortcut

        #homing_sensor_prox
        od.config.gpio8_mode = GPIO_MODE_DIGITAL
        axisshortcut.min_endstop.config.gpio_num = 2#pin 8 for x, 2 for y, 2 for z
        self.Prox_Sensor_Number = axisshortcut.min_endstop.config.gpio_num #setting to global class Runner variable just so that I can reference it in the Thread print statements
        axisshortcut.min_endstop.config.enabled = True #Turns sensor on, says that I am using it
        axisshortcut.min_endstop.config.offset = 1# stops 1 rotation away from sensor
        axisshortcut.min_endstop.config.debounce_ms = 20#checks again after 20 milliseconds if actually pressed, which is what debounce is :D
        axisshortcut.min_endstop.config.offset = -1.0 * (8192)# hop back from GPIO in order to allow for function again
        od.config.gpio8_mode = GPIO_MODE_DIGITAL_PULL_DOWN



        #axisshortcut.min_endstop.config.is_active_high = False #changes how the sensor interprets the signal, activated when high or low, if change ot low, or if change to high, most time active low

        #gainz
        self.ax.set_pos_gain(20)
        self.ax.set_vel_gain(0.16)
        self.ax.set_vel_integrator_gain(0.32)
        self.ax.axis.controller.config.enable_overspeed_error = False
        od.clear_errors()
        #smart calibrator
        if not self.ax.is_calibrated():# or od.error != 0:
            print("calibrating...")
            self.ax.calibrate_with_current(20)
        #bugtesting
        #print(od.vbus_voltage)
       # print(self.ax.get_calibration_current(), self.ax.axis.mot)
        #endbug
        self.ax.idle()

    def end_limit_calibration(self):
        print('Calibrating end Limit')#garbage function



'''
    def PrintPosition(self):
        while self.isOn:
            print("Position is: ", self.ax.get_pos(), "Updating Position...")
            sleep(1)
'''
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    r = Runner()
    r.onstartup()
    r.start_joy_thread()
    r.start_prox_thread()



