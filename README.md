# Experimental Robotics Laboratory: Third assignment

## Introduction
ROS package that simulates a simple investigation similar to Cluedo. It uses smach for the state machine behavior and moveit to move the arm so that the camera can retrieve the hints from the arucos.

## Software Architecture
The assignment is divided in five packages:
1) **exproblab_ass3:** Main part of the assignment, it is the only package that I implemented from scratch
2) **moveit_ass3_pkg:** Package built with moveit_setup_assistant
3) **exp_assignment3:** Package provided by the prof, only few modifications have been done to this package
4) **erl2:** Package provided by the prof, no modifications have been done to this package
5) **aruco_ros:** Package for arucos recognition

### Component Diagram
In the diagram below you can see all the nodes necessary for the correct functioning of the code *smach_viewer* is not there as it is only useful for displaying the states while the code is running (so it is not necessary but optional).

![Alt text](/images/ass3_component.png?raw=true)

* **move_arm:** It provides a service to use moveit and move the arm.
* **marker_publisher:** It continuosly publishes on the topic `/new_hints` the markers ID.
* **oracle(simulation.cpp):** Professor's node, it provide two services: `/oracle_hint` and `/oracle_solution`.
* **move_base & gmapping:** Methods for SLAM(*Simultaneous localization and mapping*).
* **FSM:** It implements a finite state machine that simulates the investigation using smach.
* **SIMULATION:** This component represents all nodes and interfaces of the simulation like gazebo and rviz.

### State Diagram
Here below you can see the state machine diagram generated with smach_viewer.

![Alt text](/images/smach_viewer.PNG?raw=true)

* **INITIALIZE:** Move the arm to the proper configuration for moving the robot.
* **GOTO_WAYPOINT:** Use the move_base action to control the robot through the rooms. 
* **SEARCH_HINTS:** Move your arm with predefined movements to explore the room.
* **CHECK_NEW_HYPOTHESES:** Check if I have new consistent hypotheses to be tested.
* **TRY_HYPOTHESES:** Move the robot to the center of the map and check my consistent hypotheses. 


### Temporal Diagram

![Alt text](/images/ass3_temporal.png?raw=true)

In the diagram below you can see the behavior of the code over time.
Depending on where the clues to the correct hypothesis are, the investigation can take very different times. You may need to visit only one room or, in the worst case, you may need to do more than one waypoint tour.

### List of msgs and srvs
#### msgs
* **Twist:** to publish on cmd_vel the speeds and control the robot
* **Pose:** subscribe to odom and know the current position of the turtle
* **MoveBaseActionGoal:** to set the goal of the move_base action service
* **actionlib_msgs/GoalID:** to cancel the goal of the move_base action service
* **int32:** used by `/marker_publisher`

### srvs
* **exproblab_ass3/Move_arm:** This service allows the robot arm to be moved in any configuration. It takes as input 5 floats each representing the angle of one of the 5 joints.
* **erl2/Oracle:** Used by the service `/oracle_solution`
* **exp_assignment3/Marker:** Used by the service `/oracle_hint`

## Installation and running procedure

### Requirements
To use this code some external modules are needed:
* moveit
* smach
* move_base 
* gmapping

### Installation
You have to install all the required modules mentioned earlier, you can do it using the usual command in the terminal: 
```
sudo apt-get install ros-<ros distribution you are using>-<module>
```

After you installed all the requirements you just need to clone this repository in your ros workspace:
```
git clone https://github.com/LorenzoCausa/ass3_causa
```

**Note:** If you already have some of the packages from this repository, please delete those and not the ones in this repo as some changes have been made to some of these packages. 

### Running procedure
If the package and requirements have been installed correctly, the execution procedure is simple. 
1) Open a terminal and launch:
```
roslaunch exproblab_ass3 robot_in_the_map.launch 2>/dev/null
```
Which will launch the simulation and all the services needed

**Note:** `2>/dev/null` Allows you to avoid the terminal full of warning messages 

2) Open a second terminal and start the state machine node:
```
rosrun exproblab_ass3 FSM.py
```

## Modifications on provided packages
Few changes have been made to the packages provided to facilitate interfacing 

### Modification on exp_assignment3/src/simulation.cpp
The marker_publisher often misinterprets arucos and finds markerIDs that don't match any hints, to make the service robust to a bad request an *exception* has been set for when the markerID is out of bounds [11,40]. 

![Alt Text](images/Screenshot%20from%202022-02-28%2022-30-25.png?raw=true) 

### Modification on aruco_ros/src/marker_publish.cpp
The marker publisher has been changed to publish the markerIDs found on the topic `/new_hints`

![Alt Text](images/Screenshot%20from%202022-02-28%2022-29-04.png?raw=true) 


## Video demo 
If you run properly the code you should see something like this:

![Alt Text](images/ass3_gif.gif?raw=true) 

You can take a look at the complete video demo of the project from here:

[Click here](https://drive.google.com/file/d/1rqe8EBINgaookiuIDy9umUpwCN_3O3D6/view?usp=sharing)

**Note:** Both GIF and video have been accelerated to make them shorter and with less downtime.

## Environment and working hypothesis
The system is designed to be robust and flexible. The program is in fact independent both from the map and from the arrangement of the aruco, with very few modifications it is also possible to modify the waypoints and the number of rooms and hypotheses. 

### System's features
* move_base + gmapping for Simultaneous Localization and Mapping (SLAM)
* moveable arm trough moveit equipped with camera
* laser scanner for sensing the enviroment
* the robot explores the rooms in order only on the first lap, after completing it it moves randomly between the waypoints. In this way, any aruco that was not recognized on the first round have the possibility of being recognized later thanks to a behavior that differs from the first time. 

### System’s limitations
The main problem with the system lies in the recognition of the aruco. The robot has great difficulty in recognizing aruco that are not very close to the waypoints. If the correct hypothesis contains IDs of these aruco the robot may not be able to find the solution after the first waypoint round, in this case the robot will start spinning randomly in the map. Generally it still manages to find the solution but the process tends to take a very long time. There are several possible solutions to the problem which are addressed in the *improvements* section.

**Note:** 
The system takes a long time to complete the first lap as well. On my Linux computer, for example, it takes about 50 minutes, while on the same computer in Docker it takes too long to test due to the slow simulation (it worked below 5 fps). 

### Improvements

## Doxygen documetation

## Author and contacts



# NOTA
piccola modifica ad aruco_ros marker_publisher, aggiunto publisher con il aruco ID
piccole modifiche anche a simulation.cpp
modifica in go_to_point_service del pacchetto planning
modificato gazebo world
