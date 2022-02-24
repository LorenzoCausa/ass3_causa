#!/usr/bin/env python

## @package exproblab_ass3
#   \file move_arm.py
#   \brief move the robot arm 
#   \author Lorenzo Causa
#   \version 1.0
#
#
#   Services: <BR>
#        /move_arm_service
#          
# Description:    
# 
# This node provide a service to move the robot arm
#

import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
from exproblab_ass3.srv import *

#GLOBAL VARIABLES
group=None

def move_arm_callback(req):
    """ Callback of the move_arm_service."""
    global group
    # We get the joint values from the group and adjust some of the values:
    joint_goal = group.get_current_joint_values()
    joint_goal[0] = req.joint0
    joint_goal[1] = req.joint1
    joint_goal[2] = req.joint2
    joint_goal[3] = req.joint3
    joint_goal[4] = req.joint4

    # The go command can be called with joint values, poses, or without any
    # parameters if you have already set the pose or joint target for the group
    group.set_start_state_to_current_state()
    group.go(joint_goal, wait=True)

    # Calling ``stop()`` ensures that there is no residual movement
    group.stop()
  
    return True 
    
def main():
    """main of the move_arm node"""
    global group
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('move_arm',anonymous=True)
    robot = moveit_commander.RobotCommander()
    scene = moveit_commander.PlanningSceneInterface()
    group_name = "my_arm"
    group = moveit_commander.MoveGroupCommander(group_name)
    display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path',moveit_msgs.msg.DisplayTrajectory,queue_size=20)
    # We get the name of the reference frame for this robot:
    planning_frame = group.get_planning_frame()
    print ("============ Reference frame: %s" % planning_frame)

    # We  also print the name of the end-effector link for this group:
    eef_link = group.get_end_effector_link()
    print ("============ End effector: %s" % eef_link)

    # We get a list of all the groups in the robot: 
    group_names = robot.get_group_names()
    print ("============ Robot Groups:", robot.get_group_names())

    # for debugging it is useful to print the entire state of the
    # robot:
    print ("============ Printing robot state")
    print (robot.get_current_state())
    print ("")
    
    #Set goal high tolerance since we don't need high precision
    group.set_goal_tolerance(0.05)
    
    # create services
    move_arm_server = rospy.Service('move_arm_service', Move_arm, move_arm_callback)
    
    rospy.spin()
    
    
if __name__ == '__main__':
    main()
