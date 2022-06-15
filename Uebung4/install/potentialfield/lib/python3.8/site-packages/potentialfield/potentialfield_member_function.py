import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data
import numpy as np

class PotentialField(Node):
    x_vel =0.0
    y_vel =0.0
    z_angular_vel = 0.0 
    def __init__(self):
        super().__init__('potential_field')
        # TODO: create publisher and subscriber 
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sensor = self.create_subscription(LaserScan,"scan",self.callback, qos_profile=qos_profile_sensor_data)
        timer_period = 0.2  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = Twist()
        msg.linear = Vector3(x=self.x_vel, y=0.0, z=0.0)
        msg.angular = Vector3(x=0.0, y=0.0, z=self.z_angular_vel)
        self.publisher_.publish(msg)
        #self.get_logger().info('Publishing: linear: {} angular: {}'.format(msg.linear, msg.angular))
        self.i += 1

    def callback(self,msg): 
        x = 0
        y = 0
        for idx, i in enumerate(msg.ranges):
            if i != float("inf") and i < 2:
                #print("idx: {} i: {} x: {} y: {}".format(idx, i, -math.cos(idx), -math.sin(idx)))
                x += -math.cos(math.radians(idx)) *(1/i)
                y += -math.sin(math.radians(idx)) *(1/i)
            if i == float("inf") and (idx in range(0,90) or idx in range(270, 360)):
                x += math.cos(math.radians(idx))*2
                y += math.sin(math.radians(idx))*2
                

        angularZ = math.acos(math.radians(((x*1)+(y*0))/(math.sqrt(x**2+y**2)*(1))))*(math.pi/180)*1.3
        if angularZ > 1.82:
            if y < 0:
                self.z_angular_vel = -1.82
            else:
                self.z_angular_vel = 1.82
        else:
            if y < 0:
                self.z_angular_vel = -angularZ
            else:
                self.z_angular_vel = angularZ

        xVel = math.sqrt(x**2+y**2)/100
        if xVel > 0.26:
            self.x_vel = 0.26
        else:
            self.x_vel = xVel

        print("direction x: {} y: {} x_Vel: {} angZ: {}".format(x,y, self.x_vel, self.z_angular_vel))
        #self.x_vel = 0.0
        #self.z_angular_vel = 0.0
        # TODO: implement repulsive and attractice potential field  
        #self.get_logger().info("I sensor: {} avr:".format( msg.ranges[90] ))
        
        
        
    
    def destroy_node(self):
        # stop robot on shutdown 
        self.command_publisher.publish(Twist()) 
        super().destroy_node()

def main(args=None): 
    rclpy.init(args=args)
    potentialfield = PotentialField()
    try:
        rclpy.spin(potentialfield)
    except KeyboardInterrupt:
        print("\nShutdown Potentialfield Node")
    finally:
        potentialfield.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

