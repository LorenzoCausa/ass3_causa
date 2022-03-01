#!/usr/bin/env python

## @package exproblab_ass3
#   \file FSM.py
#   \brief This node provides the finite state machine
#   \author lorenzo Causa
#   \version 1.0
#   \date 28/2/2022
#
#   \details
#
#   Clients : <BR>
#        /move_arm_service
#
#        /oracle_hint
#
#        /oracle_solution
# 
#   Subscribers : <BR>
#        /new_hints
#
#        /odom
#        
#   Publishers : <BR>
#        /cmd_vel
#
#   Actions : <BR>
#        /MoveBaseAction
#
#
# Description:    
# 
# This node implements the finite state machine thanks to smach and manages the 
# investigation. It is the node to be run for last (smach_viewer node is optional 
# and it can be run in any moment).
#  


from turtle import right
import roslib
import rospy
import smach
import smach_ros
import time
import random
from geometry_msgs.msg import *
import math
from exproblab_ass3.srv import *
from exp_assignment3.srv import *
from std_msgs.msg import *
from nav_msgs.msg import *
from move_base_msgs.msg import *
import actionlib
from tf import transformations
from erl2.srv import *

# GLOBAL VARIABLES
move_arm=None
hypotheses=[]
old_hp=[0,0,0,0,0,0]
cons_IDs=[0,0,0,0,0,0]
room1=[-4,-3]
room2=[-4,2]
room3=[-4,7]
room4=[5,1]
room5=[5,-3]
room6=[5,-7]
rooms=[room1,room2,room3,room4,room5,room6]
count=0
first_round=True
position = Point()
position.x = 0
position.y = 0
yaw = 0
pub_cmd_vel=None
old_mark=-2
hint_client=None
solution_client=None

# FUNCTION
def move_my_arm(my_joint0,my_joint1,my_joint2,my_joint3,my_joint4):
        """This function is just an interface for the move_arm service"""
        req = Move_armRequest()
        req.joint0=my_joint0
        req.joint1=my_joint1
        req.joint2=my_joint2
        req.joint3=my_joint3
        req.joint4=my_joint4

        res = move_arm(req) 
        res = move_arm(req) 
        res = move_arm(req) 

# MY CLASS
class Hypothesis:
    """ This class contains the hypothesis of the game """
    
    def __init__(self):
        """ Initializer of the class."""
        self.murderer = []
        self.murder_weapon = []
        self.murder_place = []
        self.ID=-1

# CALLBACKS
def callback_hint_found(mark_id):
    """Callback for when a hint is found  """
    global hypotheses,old_mark,hint_client
    req=mark_id.data
    res = hint_client(req)
    hint=res.oracle_hint

    flag_duplicate=False
    i=0
    if(hint.value!='-1'):
        if(hint.key=='who'):
            while ((i<len(hypotheses[hint.ID].murderer))and (flag_duplicate==False)):
                if(hint.value==hypotheses[hint.ID].murderer[i]):
                    hypotheses[hint.ID].murderer.remove(hint.value)
                    flag_duplicate=True
                i=i+1
            hypotheses[hint.ID].murderer.append(hint.value)

        flag_duplicate=False
        i=0    
        if(hint.key=='where'):
            while ((i<len(hypotheses[hint.ID].murder_place))and (flag_duplicate==False)):
                if(hint.value==hypotheses[hint.ID].murder_place[i]):
                    hypotheses[hint.ID].murder_place.remove(hint.value)
                    flag_duplicate=True
                i=i+1
            hypotheses[hint.ID].murder_place.append(hint.value)

        flag_duplicate=False
        i=0     
        if(hint.key=='what'):
            while ((i<len(hypotheses[hint.ID].murder_weapon))and (flag_duplicate==False)):
                if(hint.value==hypotheses[hint.ID].murder_weapon[i]):
                    hypotheses[hint.ID].murder_weapon.remove(hint.value)
                    flag_duplicate=True
                i=i+1
            hypotheses[hint.ID].murder_weapon.append(hint.value)

    if(mark_id.data!=old_mark):
        print('Hint found from marker',mark_id.data,' -> ID:',hint.ID,", key: ",hint.key,", value: ",hint.value)
        old_mark=mark_id.data

    # -------------------------------------------------DEBUG-----------------------------------
    #print('\n__________________________MY HYPOTHESES_________________________________')
    #for i in range(6):
    #    print('ID',i,'who: ',hypotheses[i].murderer,'where: ', hypotheses[i].murder_place,'what: ',hypotheses[i].murder_weapon)
    #print('_________________________________________________________________________\n')
    #--------------------------------------------------------------------------------------------

def clbk_odom(msg):
    """Callback of the subscriber at odom, save the robot positions in global variables"""
    global position
    global yaw

    # position
    position = msg.pose.pose.position

    # yaw
    quaternion = (
        msg.pose.pose.orientation.x,
        msg.pose.pose.orientation.y,
        msg.pose.pose.orientation.z,
        msg.pose.pose.orientation.w)
    euler = transformations.euler_from_quaternion(quaternion)
    yaw_ = euler[2]


# MY STATES
# define state Initialize
class Initialize(smach.State):
    """ State in which the investigator move through rooms. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['start_investigation'])
        
    def execute(self, userdata): 
        print('Initialization')
        move_my_arm(-1.57,0,-3,3,0)
        return 'start_investigation'

# define state Goto_waypoint
class Goto_waypoint(smach.State):
    """ State in which the investigator move through rooms. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['enter_room'])
        
    def execute(self, userdata): 
        global count,first_round
        print('Going to room ',count)
        client = actionlib.SimpleActionClient('move_base', move_base_msgs.msg.MoveBaseAction)

        my_goal=move_base_msgs.msg.MoveBaseActionGoal()
        my_goal.goal.target_pose.header.frame_id = "odom"
        my_goal.goal.target_pose.pose.position.x = rooms[count][0]
        my_goal.goal.target_pose.pose.position.y = rooms[count][1]
        my_goal.goal.target_pose.pose.orientation.w = 1

        client.wait_for_server()
        #time.sleep(1)
    
        client.send_goal(my_goal.goal)
        
        while ((position.x-rooms[count][0])*(position.x-rooms[count][0])+(position.y-rooms[count][1])*(position.y-rooms[count][1]))>0.04:
            time.sleep(0.1)
        

        client.cancel_all_goals()
        twist_msg = Twist()
        twist_msg.linear.x=0
        twist_msg.angular.z=0
        pub_cmd_vel.publish(twist_msg)
        time.sleep(0.5)

        print('Room ',count,' reached')

        if (count<5) and (first_round): # on the first lap I go in order, then I go randomly   
            count=count+1
        else:
            old_count=count
            first_round=False
            while(old_count==count):
                count= random.randint(0, 5)
        
        return 'enter_room'

# define state Search_hints
class Search_hints(smach.State):
    """ State in which the investigator search for hints via camera. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['look_for_new_hypotheses'])
        
    def execute(self, userdata):
        global pub_cmd_vel
        print('searching hints')

        time.sleep(0.5)
        move_my_arm(math.pi/2,0,0,0,-math.pi/4)
        time.sleep(0.5)
        move_my_arm(0,0,0,0,-math.pi/4)
        time.sleep(0.5)
        move_my_arm(-math.pi/2,0,0,0,-math.pi/4)
        time.sleep(0.5)
        move_my_arm(-math.pi,0,0,0,-math.pi/4)

        time.sleep(0.5)
        move_my_arm(math.pi/2,0,-3,3,0)
        time.sleep(0.5)
        move_my_arm(0,0,-3,3,0)
        time.sleep(0.5)
        move_my_arm(-math.pi/2,0,-3,3,0)
        time.sleep(0.5)
        move_my_arm(-math.pi,0,-3,3,0)


        time.sleep(0.5)
        move_my_arm(-math.pi/2,0,-3,3,0)

        return 'look_for_new_hypotheses'

# define state Check_new_hypotheses
class Check_new_hypotheses(smach.State):
    """ State in which the investigator if have new consistent hypotheses. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['no_new_hypotheses','new_hypotheses'])
        
    def execute(self, userdata):
        print('checking for new hypotheses')

        global old_hp,cons_IDs
        new_cons_IDs=False
        
        print('\n__________________________MY HYPOTHESES_________________________________')
        for i in range(6):
            print('ID',i,'who: ',hypotheses[i].murderer,'where: ', hypotheses[i].murder_place,'what: ',hypotheses[i].murder_weapon)

            cons_IDs[i]=0

            if(len(hypotheses[i].murderer)==1 and len(hypotheses[i].murder_place)==1 and len(hypotheses[i].murder_weapon)==1):
                cons_IDs[i]=1

                if(old_hp[i]==0): # per tornare 1 solo quando e la prima volta che trovi l'ipotesi
                    new_cons_IDs = True
                    old_hp[i]=1
        print('_________________________________________________________________________\n')
        
        if new_cons_IDs:
            return 'new_hypotheses'
        else:
            return 'no_new_hypotheses'

# define state Try_hypotheses
class Try_hypotheses(smach.State):
    """ State in which the investigator try its hypotheses. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['wrong_hypotheses','right_hypothesis'])
        
    def execute(self, userdata):
        global cons_IDs,solution_client
        print('testing hypotheses')

        found_solution=-1
        right_HP_ID=solution_client()

        print('Going to test room ')
        client = actionlib.SimpleActionClient('move_base', move_base_msgs.msg.MoveBaseAction)

        my_goal=move_base_msgs.msg.MoveBaseActionGoal()
        my_goal.goal.target_pose.header.frame_id = "odom"
        my_goal.goal.target_pose.pose.position.x = 0
        my_goal.goal.target_pose.pose.position.y = -1
        my_goal.goal.target_pose.pose.orientation.w = 1

        client.wait_for_server()
        #time.sleep(1)
    
        client.send_goal(my_goal.goal)
        
        while ((position.x-0)*(position.x-0)+(position.y+1)*(position.y+1))>0.04:
            time.sleep(0.1)
        

        client.cancel_all_goals()
        twist_msg = Twist()
        twist_msg.linear.x=0
        twist_msg.angular.z=0
        pub_cmd_vel.publish(twist_msg)
        time.sleep(0.5)
        print('Arrived in test room ')

        for i in range(len(cons_IDs)):
            if (cons_IDs[i]==1) and (i==right_HP_ID.ID): #test that the response is consistent and if it is equal to the solution
                found_solution=i

        if found_solution==-1:
            print('solution not found')
            return 'wrong_hypotheses'
        
        else:
            print('solution found!')
            print('ID: ',hypotheses[found_solution].ID)
            print('murderer: ',hypotheses[found_solution].murderer)
            print('murder place: ',hypotheses[found_solution].murder_place)
            print('murder weapon: ',hypotheses[found_solution].murder_weapon)
            
            return 'right_hypothesis'

def main():
    """ main of the finite state machine, it implements the logic of the investigation."""
    global move_arm,hypotheses,pub_cmd_vel,solution_client,hint_client

    rospy.init_node('FSM')
    
    # Wait all services
    print("Wait for all services needed..")
    rospy.wait_for_service('move_arm_service')
    rospy.wait_for_service('oracle_hint')
    rospy.wait_for_service('oracle_solution')

    print("All services ready!")

    # initiate all clients
    move_arm = rospy.ServiceProxy('move_arm_service', Move_arm)
    hint_client = rospy.ServiceProxy('oracle_hint',Marker)
    solution_client = rospy.ServiceProxy('oracle_solution',Oracle)

    # initiate subscribers
    rospy.Subscriber("/new_hints", Int32, callback_hint_found)
    rospy.Subscriber('/odom', Odometry, clbk_odom)

    # initiate publishers
    pub_cmd_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    
    #Generate Hypotheses
    for i in range(6):
        HP = Hypothesis()
        HP.ID=i
        hypotheses.append(HP)

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['CASE_SOLVED'])
    # sm.userdata.first=True

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('INITIALIZE', Initialize(), 
                               transitions={'start_investigation':'GOTO_WAYPOINT'})

        smach.StateMachine.add('GOTO_WAYPOINT', Goto_waypoint(), 
                               transitions={'enter_room':'SEARCH_HINTS'})

        smach.StateMachine.add('SEARCH_HINTS', Search_hints(), 
                               transitions={'look_for_new_hypotheses':'CHECK_NEW_HYPOTHESES'})

        smach.StateMachine.add('CHECK_NEW_HYPOTHESES', Check_new_hypotheses(), 
                               transitions={'no_new_hypotheses':'GOTO_WAYPOINT', 
                                            'new_hypotheses':'TRY_HYPOTHESES'})

        smach.StateMachine.add('TRY_HYPOTHESES', Try_hypotheses(), 
                               transitions={'wrong_hypotheses':'GOTO_WAYPOINT', 
                                            'right_hypothesis':'CASE_SOLVED'})


    # Create and start the introspection server for visualization
    sis = smach_ros.IntrospectionServer('server_name', sm, '/SM_ROOT')
    sis.start()

    # Execute the state machine
    outcome = sm.execute()

    # Wait for ctrl-c to stop the application
    rospy.spin()
    sis.stop()


if __name__ == '__main__':
    main()
