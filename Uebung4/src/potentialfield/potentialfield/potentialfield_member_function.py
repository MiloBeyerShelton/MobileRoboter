import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data
import numpy as np

class PotentialField(Node):
    def __init__(self):
        super().__init__('potential_field')
        # TODO: create publisher and subscriber 

    def callback(self,msg):
        # TODO: implement repulsive and attractice potential field  
        
    
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

