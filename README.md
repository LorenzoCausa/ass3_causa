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

![Alt text](/images/ass3_state_diagram.png?raw=true)
![Alt text](/images/smach_viewer.PNG?raw=true)

### Temporal Diagram

![Alt text](/images/ass3 temporal.png?raw=true)

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

### Installation

### Running procedure

## Behavior

## Video demo 
If you run properly the code you should see something like this:

![Alt Text](images/ass3_gif.gif?raw=true) 

You can take a look at the complete video demo of the project from here:

[Click here](https://drive.google.com/file/d/19CJEttzlF02bgv060-hVGbhpjzxToKuG/view?usp=sharing)

## Environment and working hypothesis

### System's features

### System’s limitations

### Improvements

## Doxyden documetation

## Author and contacts



# NOTA
piccola modifica ad aruco_ros marker_publisher, aggiunto publisher con il aruco ID
piccole modifiche anche a simulation.cpp
modifica in go_to_point_service del pacchetto planning
