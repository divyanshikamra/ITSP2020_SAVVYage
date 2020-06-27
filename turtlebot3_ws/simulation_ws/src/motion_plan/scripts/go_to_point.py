#! /usr/bin/env python

# import ros stuff
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from tf import transformations
from std_srvs.srv import *

import math
import re 
# Import BeautifulSoup
from bs4 import BeautifulSoup as bs
content = []

def splt(b):
    res = re.split(' ',b)
    return res

def pose(a):
    # Read the XML file
    with open("/home/divyanshi/turtlebot3_ws/simulation_ws/src/motion_plan/scripts/savvyage.xml", "r") as file:
        # Read each line in the file, readlines() returns a list of lines
        content = file.readlines()
        # Combine the lines in the list into a string
        content = "".join(content)
        bs_content = bs(content, "lxml")
    tags = bs_content.find_all("model")
    if (a=="room-2") or (a=="room-3"):
        for tag in tags:
            if(tag["name"]==a):
                res1 = splt(tag.find("pose").getText())[:2]

        res = []
        res.append(float(res1[0])+1.2)
        res.append(float(res1[1])-0.2)

    elif (a=="store") or (a=="room-1"):
        for tag in tags:
            if(tag["name"]==a):
                res1 = splt(tag.find("pose").getText())[:2]

        res = []
        res.append(float(res1[0])+2.0)
        res.append(float(res1[1])-1)        


    else:
        find1 = a+"-1"
        find2 = a+"-2"
        for tag in tags:
            if(tag["name"]==find1):
                pose1 = splt(tag.find("pose").getText())[:2]
            if(tag["name"]==find2):
                pose2 = splt(tag.find("pose").getText())[:2]

        res = []
        res.append((float(pose1[0])+float(pose2[0]))/2)
        res.append((float(pose1[1])+float(pose2[1]))/2)

    return res


active_ = False

# robot state variables
position_ = Point()
yaw_ = 0
# machine state
state_ = 0
# goal
desired_position_ = Point()
desired_position_.x = pose(rospy.get_param('des_pos'))[0]
desired_position_.y = pose(rospy.get_param('des_pos'))[1]
desired_position_.z = 0
# parameters
yaw_precision_ = math.pi / 90 # +/- 2 degree allowed
dist_precision_ = 0.3

# publishers
pub = None

def go_to_point_switch(req):
    global active_
    active_ = req.data
    res = SetBoolResponse()
    res.success = True
    res.message = 'Done!'
    return res

# callbacks
def clbk_odom(msg):
    global position_
    global yaw_
    
    # position
    position_ = msg.pose.pose.position
    
    # yaw
    quaternion = (
        msg.pose.pose.orientation.x,
        msg.pose.pose.orientation.y,
        msg.pose.pose.orientation.z,
        msg.pose.pose.orientation.w)
    euler = transformations.euler_from_quaternion(quaternion)
    yaw_ = euler[2]

def change_state(state):
    global state_
    state_ = state
    print 'State changed to [%s]' % state_

def fix_yaw(des_pos):
    global yaw_, pub, yaw_precision_, state_
    desired_yaw = math.atan2(des_pos.y - position_.y, des_pos.x - position_.x)
    err_yaw = desired_yaw - yaw_
    
    twist_msg = Twist()
    if math.fabs(err_yaw) > yaw_precision_:
        twist_msg.angular.z = -0.7 if err_yaw > 0 else 0.7
    
    pub.publish(twist_msg)
    
    # state change conditions
    if math.fabs(err_yaw) <= yaw_precision_:
        print 'Yaw error: [%s]' % err_yaw
        change_state(1)

def go_straight_ahead(des_pos):
    global yaw_, pub, yaw_precision_, state_
    desired_yaw = math.atan2(des_pos.y - position_.y, des_pos.x - position_.x)
    err_yaw = desired_yaw - yaw_
    err_pos = math.sqrt(pow(des_pos.y - position_.y, 2) + pow(des_pos.x - position_.x, 2))
    
    if err_pos > dist_precision_:
        twist_msg = Twist()
        twist_msg.linear.x = 0.3
        pub.publish(twist_msg)
    else:
        print 'Position error: [%s]' % err_pos
        change_state(2)
    
    # state change conditions
    if math.fabs(err_yaw) > yaw_precision_:
        print 'Yaw error: [%s]' % err_yaw
        change_state(0)

def done():
    twist_msg = Twist()
    twist_msg.linear.x = 0
    twist_msg.angular.z = 0
    pub.publish(twist_msg)

def main():
    global pub
    
    rospy.init_node('go_to_point')
    
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    
    sub_odom = rospy.Subscriber('/odom', Odometry, clbk_odom)

    srv= rospy.Service('go_to_point_switch', SetBool, go_to_point_switch)
    
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        if not active_:
            continue
        else:
            if state_ == 0:
                fix_yaw(desired_position_)
            elif state_ == 1:
                go_straight_ahead(desired_position_)
            elif state_ == 2:
                done()
                pass
            else:
                rospy.logerr('Unknown state!')
                pass

        rate.sleep()

if __name__ == '__main__':
    main()
