'''
### Ueb1_template.py ###

Alle Stellen an denen Code fehlt sind mit TODO markiert.
Implementieren Sie die Verhalten in der Funtion main().

'''

import argparse
import time
import math
from thymiodirect import Connection 
from thymiodirect import Thymio

def convert_speed(speed):
    ''' Convert the motor command (-500 to 500) and return a value in m/s '''
    # TODO: Implementieren Sie hier die Funktion DONE
    return (speed* (1/25)* 0.01)

def deg_to_rad(deg):
    ''' Convert degrees to radians '''
    # TODO: Implementieren Sie hier die Funktion
    return (deg*(math.pi/180))


def degrees_to_seconds(degrees, speed):
    ''' Calculate the time (s) it takes to rotate (0-360 degrees) a specific amount on the spot with a given speed (m/s) '''
    # TODO: Implementieren Sie hier die Funktion
    return distance_to_seconds((deg_to_rad(degrees)*5.7)*0.01,speed)

def distance_to_seconds(distance, speed):
    ''' Calculate the time (s) it takes to drive a specific distance (m) with a given speed (m/s). '''
    # TODO: Implementieren Sie hier die Funktion
    return ((distance/1)*(1/speed))


def main(use_sim=False, ip='localhost', port=2001):
    ''' Main function '''
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
        
        # Main loop

        #keep these positive!
        dirve_speed = 200
        reverse_speed = 200
        reverse_len = 0.3 
        turn_speed = 100
        turn_deg = 60

        while True:
           
            # TODO: Implementieren Sie hier das gewünschte Verhalten

            if robot["prox.ground.reflected"][0]>= 600 or robot["prox.ground.reflected"][1]>= 600:
                state = "GO"
            elif robot["prox.ground.reflected"][0]< 600 or robot["prox.ground.reflected"][1]< 600:
                state = "TurnL"
            

            if state == "GO":
                robot["motor.left.target"]=dirve_speed
                robot["motor.right.target"]=dirve_speed
            elif state == "TurnL":
                robot["motor.left.target"]=-reverse_speed
                robot["motor.right.target"]=-reverse_speed
                time.sleep(distance_to_seconds(reverse_len, convert_speed(reverse_speed))) #hopefully only this thread sleeps not the robor

                robot["motor.left.target"]=-turn_speed
                robot["motor.right.target"]=turn_speed
                time.sleep(degrees_to_seconds(turn_deg, convert_speed(turn_speed))) #hopefully only this thread sleeps not the robor

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



