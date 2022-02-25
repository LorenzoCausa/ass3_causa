#!/usr/bin/env python

import roslib
import rospy
import smach
import smach_ros
import time
import random
from geometry_msgs.msg import Twist
import math
from exproblab_ass3.srv import *
from exp_assignment3.srv import *
from std_msgs.msg import *

# GLOBAL VARIABLES
move_arm=None
hypotheses=[]
old_hp=[0,0,0,0,0,0]

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
    global hypotheses
    hint_client = rospy.ServiceProxy('oracle_hint',Marker)
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

    print("New hint found!")
    print('ID:',hint.ID,", key: ",hint.key,", value: ",hint.value,"\n")

    # -------------------------------------------------DEBUG-----------------------------------
    print('\n__________________________MY HYPOTHESES_________________________________')
    for i in range(6):
        print('ID',i,'who: ',hypotheses[i].murderer,'where: ', hypotheses[i].murder_place,'what: ',hypotheses[i].murder_weapon)
    print('_________________________________________________________________________\n')
    #--------------------------------------------------------------------------------------------

# MY STATES
# define state Initialize
class Initialize(smach.State):
    """ State in which the investigator move through rooms. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['start_investigation'])
        
    def execute(self, userdata): 
        print('Initialization')

        req = Move_armRequest()
        req.joint0=-1.57
        req.joint1=0
        req.joint2=-3
        req.joint3=3
        req.joint4=0
        res = move_arm(req)
        return 'start_investigation'

# define state Goto_waypoint
class Goto_waypoint(smach.State):
    """ State in which the investigator move through rooms. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['enter_room'])
        
    def execute(self, userdata): 
        print('Going to waypoint')
        time.sleep(1)
        return 'enter_room'

# define state Search_hints
class Search_hints(smach.State):
    """ State in which the investigator search for hints via camera. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['look_for_new_hypotheses'])
        
    def execute(self, userdata):
        print('searching hints')
        time.sleep(1)
        return 'look_for_new_hypotheses'

# define state Check_new_hypotheses
class Check_new_hypotheses(smach.State):
    """ State in which the investigator if have new consistent hypotheses. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['no_new_hypotheses','new_hypotheses'])
        
    def execute(self, userdata):
        print('checking for new hypotheses')
        time.sleep(1)
        return 'new_hypotheses'

# define state Try_hypotheses
class Try_hypotheses(smach.State):
    """ State in which the investigator try its hypotheses. """	
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self, outcomes=['wrong_hypotheses','right_hypothesis'])
        
    def execute(self, userdata):
        print('testing new hypotheses')
        time.sleep(1)
        return 'right_hypothesis'

def main():
    """ main of the finite state machine, it implements the logic of the investigation."""
    global move_arm,hypotheses

    rospy.init_node('FSM')
    
    # Wait all services
    print("Wait for all services needed..")
    rospy.wait_for_service('move_arm_service')
    rospy.wait_for_service('oracle_hint')

    print("All services ready!")

    # initiate all clients
    move_arm = rospy.ServiceProxy('move_arm_service', Move_arm)

    # initiate subscriber
    rospy.Subscriber("/new_hints", Int32, callback_hint_found)
    
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