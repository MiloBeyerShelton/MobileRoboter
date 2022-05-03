import math

#speed in range from -500 - 500 
def convert_speed(speed):
    ''' Convert the motor command and return a value in m/s '''
    # TODO: Implementieren Sie hier die Funktion DONE
    return (speed* (1/25)* 0.01)

def deg_to_rad(deg):
    ''' Convert degrees to radians '''
    # TODO: Implementieren Sie hier die Funktion
    return (deg*(math.pi/180))

# speed in m/s degrees in 0-360 
def degrees_to_seconds(degrees, speed):
    ''' Calculate the time it takes to rotate a specific amount on the spot with a given speed '''
    # TODO: Implementieren Sie hier die Funktion
    return distance_to_seconds((deg_to_rad(degrees)*5.6)*0.01,speed)

# distance in m and speed in m/s
def distance_to_seconds(distance, speed):
    ''' Calculate the time it takes to drive a specific distance (in m) with a given speed '''
    # TODO: Implementieren Sie hier die Funktion
    return ((distance/1)*(1/speed))







print("speed: {}".format(convert_speed(200)))

print("degrees {} to rad:{}".format(360, deg_to_rad(360)))

print("degrees {} to seconds: {}".format(60, degrees_to_seconds(60, 0.2)))

print("distance to seconds for given speed {} : {}".format(0.08, distance_to_seconds(0.3, 0.08)))

