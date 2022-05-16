'''
### Ueb2_template.py ###

Alle Stellen an denen Code fehlt sind mit TODO markiert.
Implementieren Sie die Verhalten mithilfe eines Arbiters.

'''

import argparse
import time
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

class ThymioNetworkNode:
    def __init__(self, robot):
        # Robot-Objekt
        self.robot = robot

        # True = Roboter wurde gestartet, False = Roboter ist gestoppt
        self.start = False 

        # Liste der Verhalten 
        self.behaviors = []

        # TODO: Definieren Sie hier eigene benoetigte Variablen.
        self.drive_speed = 200
        
        self.escape_drive_speed = 400
        self.escape_turn_speed = 200
        self.escape_turn_deg = 180

        self.avoid_speed = self.drive_speed 

    
    class Cruise:
        def __init__(self, node):
            self.arbiter = node
            self.command = [0, 0]

        def action(self):
            self.command = [self.arbiter.drive_speed, self.arbiter.drive_speed]
            return True

    class Escape:
        def __init__(self, node):
            self.arbiter = node
            self.command = [0, 0]
            self.backup_duration = 0 
            self.turn_duration = 0
            self.action_running = False 


        def action(self): #TODO check IR-sensor values
            if self.arbiter.prox_ground[0] < 500 or self.arbiter.prox_ground[1] < 500 or self.action_running: 
                if not self.action_running: # check if this action is currently running. If NOT start backup phase
                    self.action_running = True
                    self.backup_duration = time.time()+ distance_to_seconds(0.20 , convert_speed(self.arbiter.escape_drive_speed))
                    self.command = [-self.arbiter.escape_drive_speed, -self.arbiter.escape_drive_speed] #set motor speeds
                
                elif time.time() >= self.backup_duration: # check if reverse duration is over. If so start phase Turn
                    self.turn_duration = time.time()+ degrees_to_seconds(self.arbiter.escape_turn_deg, convert_speed(self.arbiter.escape_turn_speed))
                    self.command[-self.arbiter.escape_turn_speed, self.arbiter.escape_turn_speed]
                elif time.time() >= self.turn_duration: # check if turnduration is over. If so end behavior
                    self.action_running = False 
                    return False
                return True
            return False


    class Avoid:
        def __init__(self, node):
            self.arbiter = node
            self.command = [0, 0]

        def action(self):
            if self.arbiter.prox_horizontal[0] > 3200 or self.arbiter.prox_horizontal[1] > 3200:
                self.command[self.arbiter.avoid_speed, -self.arbiter.avoid_speed]
                return True                
            elif self.arbiter.prox_horizontal[3] > 3200 or self.arbiter.prox_horizontal[4] > 3200:
                self.command[-self.arbiter.avoid_speed, self.arbiter.avoid_speed]
                return True
            
            return False


    def Arbiter(self):

        # TODO: Instantiierung der Verhalten und Hinzufuegen zur Liste 'behaviors'
        # e.g. self.behaviors.append(self.Cruise(self))
        self.behaviors.append(self.Escape(self))
        self.behaviors.append(self.Avoid(self))
        self.behaviors.append(self.Cruise(self))

        # Control-Loop
        while True:

            if self.robot["button.forward"] == 1 :
                self.start = True  
            elif self.robot["button.center"] == 1 :
                self.start = False


            # Update der IR-Sensoren
            if self.start:
                self.prox_horizontal = self.robot["prox.horizonal"]
                self.prox_ground = self.robot["prox.ground.reflected"]
            
            # choose behavior and set motor speeds
            for behaviors in self.behaviors:
                if behaviors.action():
                    self.robot["motor.left.target"] = behaviors.command[0]
                    self.robot["motor.right.target"] = behaviors.command[1]


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
        thymio = ThymioNetworkNode(robot)
        thymio.Arbiter()

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
