#!/usr/bin/env python
import rospy
import random
from std_msgs.msg import Header
from sensor_msgs.msg import JointState

global JOINT_POSITIONS
JOINT_POSITIONS = []

NUM_INTERPOLATIONS = 500

global TARGET_JOINT_POSITIONS
TARGET_JOINT_POSITIONS = []

global POSITION_STEPS
POSITION_STEPS = []

global JOINT_NAMES
JOINT_NAMES = []

def jointStatePublisher():
    # Create ROS publisher
    data_publisher = rospy.Publisher('joint_states_interpolated', JointState, queue_size=10)
    # Give node name
    rospy.init_node('joint_state_interpolated_publisher')
    # Set operation frequency
    rate = rospy.Rate(100) # 10hz

    # Create a robot joint state message
    robot_arm_joint_state = JointState()
    robot_arm_joint_state.header = Header()
    robot_arm_joint_state.header.stamp = rospy.Time.now()
    robot_arm_joint_state.name = JOINT_NAMES

    robot_arm_joint_state.velocity = []
    robot_arm_joint_state.effort = []

    current_interpolation = 0
    
    # Generate a target       
    generateNewTargets()

    while not rospy.is_shutdown():

        robot_arm_joint_state.header.stamp = rospy.Time.now()

        if (current_interpolation < NUM_INTERPOLATIONS) and (len(POSITION_STEPS)):
            current_interpolation += 1 
            new_data = []
            for index, data in enumerate(TARGET_JOINT_POSITIONS):
                global POSITION_STEPS
                new_data.append(JOINT_POSITIONS[index] + POSITION_STEPS[index])
            robot_arm_joint_state.position = new_data

            # Publish robot joint state data to the topic
            data_publisher.publish(robot_arm_joint_state)
            rate.sleep()

        if (current_interpolation == NUM_INTERPOLATIONS - 1):
            current_interpolation = 0
            generateNewTargets()

def generateNewTargets():
    revolute_limits = [-3.14, 3.14]
    prismatic_limits = [-0.10, 0.06]

    global TARGET_JOINT_POSITIONS
    TARGET_JOINT_POSITIONS = [random.uniform(revolute_limits[0], revolute_limits[1]) for i in range(4)]
    TARGET_JOINT_POSITIONS.append(random.uniform(prismatic_limits[0], prismatic_limits[1]))

    if (len(JOINT_POSITIONS)) and (len(TARGET_JOINT_POSITIONS)):
        global POSITION_STEPS
        POSITION_STEPS = [(target-current)/float (NUM_INTERPOLATIONS) for (target, current) in zip(TARGET_JOINT_POSITIONS, JOINT_POSITIONS)]

    print ("Current Joint Positions: %s" %(str(JOINT_POSITIONS)))
    print ("New Target joint positions: %s and steps: %s" %(str(TARGET_JOINT_POSITIONS), str(POSITION_STEPS)))

def jointStatesCallback(msg):
    global JOINT_NAMES
    JOINT_NAMES = msg.name

    temp_list = msg.position

    global JOINT_POSITIONS
    JOINT_POSITIONS = msg.position

    global JOINT_VELOCITIES
    JOINT_VELOCITIES = msg.velocity
    global JOINT_EFFORTS
    JOINT_EFFORTS = msg.effort

if __name__ == "__main__":
    try:
        # Create joint states' subscriber
        data_subscriber = rospy.Subscriber('joint_states', JointState, jointStatesCallback)
        jointStatePublisher()
    except rospy.ROSInterruptException:
        pass
