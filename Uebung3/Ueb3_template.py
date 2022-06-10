'''
### Ueb3_template.py ###

Alle Stellen an denen Code fehlt sind mit TODO markiert.
Implementieren Sie den Beeclust Algorithmus als finite state machine.

'''

import argparse
from multiprocessing import set_forkserver_preload
from re import S
import time
import math
from random import randint, random
from thymiodirect import Connection 
from thymiodirect import Thymio


def convert_speed(speed):
    ''' Convert the motor command (-500 to 500) and return a value in m/s '''
    return (speed* (1/25)* 0.01)

def deg_to_rad(deg):
    ''' Convert degrees to radians '''
    return (deg*(math.pi/180))


def degrees_to_seconds(degrees, speed):
    ''' Calculate the time (s) it takes to rotate (0-360 degrees) a specific amount on the spot with a given speed (m/s) '''
    return distance_to_seconds((deg_to_rad(degrees)*5.7)*0.01,speed)

def distance_to_seconds(distance, speed):
    ''' Calculate the time (s) it takes to drive a specific distance (m) with a given speed (m/s). '''
    return ((distance/1)*(1/speed))


# I2C light intensity sensor  configuration
I2Cadr = 0x29
I2Cbus = None

# Only needed for real robot. !!! Comment out in simulation !!!

import smbus
import RPi.GPIO as GPIO
I2Cbus = smbus.SMBus(1)
I2Cbus.write_byte_data(I2Cadr, 0x00 | 0x80, 0x03)
I2Cbus.write_byte_data(I2Cadr, 0x01 | 0x80, 0x00)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT, initial=GPIO.LOW)


class ThymioNetworkNode:
    def __init__(self, robot, sim):
        # Robot-Objekt
        self.robot = robot

        # True = Roboter ist eine Simulation, False = Roboter ist real
        self.sim = sim	

        # True = Roboter wurde gestartet, False = Roboter ist gestoppt
        self.start = False 

        # State of the robot
        self.state = None

        # TODO: Definieren Sie hier eigene benoetigte Variablen.
        self.behaviors = []

        self.light_sensor = 0
        self.prox_ground = []
        self.prox_horizontal = []
        self.drive_speed = 250
        
        self.escape_drive_speed = 200
        self.escape_turn_speed = 200
        self.escape_turn_deg = 60

        self.avoid_turn_speed = 200 
        self.avoid_turn_deg = 180

    
    class Cruise:
        def __init__(self, node):
            self.arbiter = node
            self.command = [0, 0]

        def action(self):
            self.command = [self.arbiter.drive_speed, self.arbiter.drive_speed]
            print("cruise")
            return True

    class Escape:
        def __init__(self, node):
            self.arbiter = node
            self.command = [0, 0]
            self.backup_duration = 0 
            self.turn_duration = 0
            #self.action_running = False 
            self.state = "sensorCheck" # sensoreCheck, activeBackup, activeTurn

        def action(self): #TODO check IR-sensor values
            print(self.arbiter.prox_ground[0])
            if self.state == "sensorCheck" and (self.arbiter.prox_ground[0] > 650 or self.arbiter.prox_ground[1] > 650):
                self.backup_duration = time.time() + distance_to_seconds(0.20, convert_speed(self.arbiter.escape_drive_speed ))
                self.turn_duration = self.backup_duration + degrees_to_seconds(self.arbiter.escape_turn_deg, convert_speed(self.arbiter.escape_turn_speed))
                self.state = "activeBackup"
                self.command = [-200, -200]
                return True
            elif self.state == "activeBackup":
                if self.backup_duration < time.time():
                    self.state = "activeTurn"
                    return True
                self.command = [-200, -200]
                return True
            elif self.state == "activeTurn":
                if self.turn_duration < time.time():
                    self.state = "sensorCheck"
                    return False
                self.command = [-self.arbiter.escape_turn_speed, self.arbiter.escape_turn_speed]
                return True
            return False

    class Avoid:
        def __init__(self, node):
            self.arbiter = node
            self.command = [0, 0]
            self.wait_duration = 0
            self.turn_duration = 0
            #self.action_running = False 
            self.state = "colisionCheck" # colisionCheck, activeWait, activeTurn

        def action(self):
            luminance = self.arbiter.get_luminance(self.arbiter.robot) 
            proxis = self.arbiter.prox_horizontal

            if self.state == "colisionCheck" and [True for i in proxis if i > 2500]:
                self.command= [0,0]
                self.state = "activeWait"
                self.wait_duration = time.time() + self.arbiter.calc_waiting(I_SCALE = luminance)
                self.turn_duration = self.wait_duration + degrees_to_seconds(self.arbiter.avoid_turn_deg, convert_speed(self.arbiter.avoid_turn_speed))
                return True
            elif self.state == "activeWait":
                if self.wait_duration < time.time():
                    self.state = "activeTurn"
                    self.command= [self.arbiter.avoid_turn_speed,-self.arbiter.avoid_turn_speed]
                    return True
                self.command= [0,0]
                return True
            elif self.state == "activeTurn":
                if self.turn_duration < time.time():
                    self.state = "colisionCheck"
                    return False
                self.command= [self.arbiter.avoid_turn_speed,-self.arbiter.avoid_turn_speed]
                return True 
            return False

    def run_beeclust(self):
        ''' Beeclust algorithm '''
        self.behaviors.append(self.Avoid(self))
        self.behaviors.append(self.Escape(self))
        self.behaviors.append(self.Cruise(self))

        # Control-Loop
        while True:

            if self.robot["button.forward"] == 1 :
                self.start = True  
            if self.robot["button.center"] == 1 :
                self.start = False
                self.robot["motor.left.target"] = 0
                self.robot["motor.right.target"] = 0

            if self.start:
               # print("{}   {}".format(self.robot["prox.ground.reflected"][0] , self.robot["prox.horizontal"]))

                self.prox_horizontal = self.robot["prox.horizontal"]
                self.prox_ground = self.robot["prox.ground.reflected"]
                self.light_sensor = self.get_luminance(self.robot)

            # TODO: Update des State

            # TODO: Berechnung der Motorwerte

            # TODO: Setzen der Motorwerte
                for behaviors in self.behaviors:
                    if behaviors.action():
                        self.robot["motor.left.target"] = behaviors.command[0]
                        self.robot["motor.right.target"] = behaviors.command[1]
                        break

    def get_luminance(self, robot):
        ''' Reads the luminance from the light sensor '''
        if self.sim: 
            return robot['light']
        else:
            data = I2Cbus.read_i2c_block_data(I2Cadr, 0x14 | 0x80, 2)
            return int((data[1] << 8) + data[0])


    def calc_waiting(self, I_SCALE = 1500, I_MAX = 65000, I_MIN = 300, W_MAX = 90, C = 7000.0 * 5625.0/81.0):
        ''' Calculates the waiting time for the robot '''
        luminance = self.get_luminance(self.robot)
        waitingTime = 0
        i_scale = (I_SCALE - I_MIN)*((1500)/(I_MAX-I_MIN))
        waitingTime = math.ceil((W_MAX*math.pow(i_scale, 2))/(math.pow(i_scale, 2)+C))

        print('luminance = ' + str(luminance))
        print('waiting time = ' + str(waitingTime))

        return waitingTime 


def main(use_sim=False, ip='localhost', port=2001):
    try:
        # Configure Interface to Thymio robot
        if use_sim:
            th = Thymio(use_tcp=True, host=ip, tcp_port=port, 
                        on_connect=lambda node_id: print(f' Thymio {node_id} is connected'))
        else:
            port = Connection.serial_default_port()
            th = Thymio(serial_port=port, 
                        on_connect=lambda node_id: print(f'Thymio {node_id} is connected'))

        # Connect to Robot
        th.connect()
        robot = th[th.first_node()]

        # Delay to allow robot initialization of all variables
        time.sleep(1)

        # Create ThymioNetworkNode Object and start Arbiter
        thymio = ThymioNetworkNode(robot, use_sim)
        thymio.run_beeclust()

        # Stop robot
        robot['motor.left.target'] = 0
        robot['motor.right.target'] = 0 

    except Exception as err:
        # Stop robot
        robot['motor.left.target'] = 0
        robot['motor.right.target'] = 0 
        print(err)


if __name__ == '__main__':
    # Parse commandline arguments to cofigure the interface for a simulation (default = real robot)
    parser = argparse.ArgumentParser(description='Configure optional arguments to run the code with simulated Thymio. '
                                                    'If no arguments are given, the code will run with a real Thymio.')
    
    # Add optional arguments
    parser.add_argument('-s', '--sim', action='store_true', help='set this flag to use simulation')
    parser.add_argument('-i', '--ip', help='set the TCP host ip for simulation. default=localhost', default='localhost')
    parser.add_argument('-p', '--port', type=int, help='set the TCP port for simulation. default=2001', default=2001)

    # Parse arguments and pass them to main function
    args = parser.parse_args()
    main(args.sim, args.ip, args.port)
