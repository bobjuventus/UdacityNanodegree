## Project: Perception Pick & Place

---

### Required Steps for a Passing Submission:

1. Extract features and train an SVM model on new objects (see `pick_list_*.yaml` in `/pr2_robot/config/` for the list of models you'll be trying to identify). 
2. Write a ROS node and subscribe to `/pr2/world/points` topic. This topic contains noisy point cloud data that you must work with.
3. Use filtering and RANSAC plane fitting to isolate the objects of interest from the rest of the scene.
4. Apply Euclidean clustering to create separate clusters for individual items.
5. Perform object recognition on these objects and assign them labels (markers in RViz).
6. Calculate the centroid (average in x, y and z) of the set of points belonging to that each object.
7. Create ROS messages containing the details of each object (name, pick_pose, etc.) and write these messages out to `.yaml` files, one for each of the 3 scenarios (`test1-3.world` in `/pr2_robot/worlds/`).  [See the example `output.yaml` for details on what the output should look like.](https://github.com/udacity/RoboND-Perception-Project/blob/master/pr2_robot/config/output.yaml)  
8. Submit a link to your GitHub repo for the project or the Python code for your perception pipeline and your output `.yaml` files (3 `.yaml` files, one for each test world).  You must have correctly identified 100% of objects from `pick_list_1.yaml` for `test1.world`, 80% of items from `pick_list_2.yaml` for `test2.world` and 75% of items from `pick_list_3.yaml` in `test3.world`.
9. Congratulations!  Your Done! 

### Extra Challenges: Complete the Pick & Place

7. To create a collision map, publish a point cloud to the `/pr2/3d_map/points` topic and make sure you change the `point_cloud_topic` to `/pr2/3d_map/points` in `sensors.yaml` in the `/pr2_robot/config/` directory. This topic is read by Moveit!, which uses this point cloud input to generate a collision map, allowing the robot to plan its trajectory.  Keep in mind that later when you go to pick up an object, you must first remove it from this point cloud so it is removed from the collision map!
8. Rotate the robot to generate collision map of table sides. This can be accomplished by publishing joint angle value(in radians) to `/pr2/world_joint_controller/command`
9. Rotate the robot back to its original state.
10. Create a ROS Client for the “pick_place_routine” rosservice.  In the required steps above, you already created the messages you need to use this service. Checkout the [PickPlace.srv](https://github.com/udacity/RoboND-Perception-Project/tree/master/pr2_robot/srv) file to find out what arguments you must pass to this service.
11. If everything was done correctly, when you pass the appropriate messages to the `pick_place_routine` service, the selected arm will perform pick and place operation and display trajectory in the RViz window
12. Place all the objects from your pick list in their respective dropoff box and you have completed the challenge!
13. Looking for a bigger challenge?  Load up the `challenge.world` scenario and see if you can get your perception pipeline working there!

[//]: # (Image References)

[model1_prediction]: ./misc_images/model1_prediction.png
[model2_prediction]: ./misc_images/model2_prediction.png
[model3_prediction]: ./misc_images/model3_prediction.png

## [Rubric](https://review.udacity.com/#!/rubrics/1067/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

### Exercises 1-3 implemented

This is a separated exercise that the corresponding changes are implemented in this [repo folder](https://github.com/bobjuventus/UdacityNanodegree/tree/master/RoboND-Perception-Exercises).

In general...

Validate the codes in the next section...

### Pick and Place Setup

#### 1. Validating the segmentation and recognition from the previous exercises.

Insert 3 pics...

Explain stuff...

![alt text][model1_prediction]

![alt text][model2_prediction]

![alt text][model3_prediction]

#### 2. Read from pick list and output specific .yaml file.

Output files are generated at ...

Problem: `RRTConnect: Unable to sample any valid states for goal tree` 


### Project Implementation

#### 1. Fill in the `IK_server.py` file with properly commented python code for calculating Inverse Kinematics based on previously performed Kinematic Analysis. Your code must guide the robot to successfully complete 8/10 pick and place cycles. Briefly discuss the code you implemented and your results. 

Most of the codes have been snipped and attached above. Here is the summary of the basic flow:

1. Define the symbols and create the DH parameters
2. Calculate all the transformation matrices between each DH frames
3. Define the extrinsic rotation from base link to EE link and the correction matrix between DH and URDF frame. Later we can plug in the value from the EE orientation to get the value rotation matrix.
4. From the EE position we can get the EE position in base link. Combined with the rotation matrix, we can get the WC (wrist center) position.
5. $/theta_{1-3}$ can be calculated using the WC position.
6. Knowing $/theta_{1-3}$, we can get the value matrix of $R_{3->6} = R_{0->3}^{-1}R_{0->6}$. We also know the symbolic matrix from individual transform matrix from step 2. $/theta_{4-6}$ can then be calculated by comparing the sympolic matrix and the value matrix.
7. Populate all the $/theta$ values back to the response object.


Useful things that I found and can be used in the future:
* All the matrix definitions should be outside the for loop to reduce runtime
* Be careful with the `atan2` usage. It matters where you put the negative sign
* I need to convert $/theta$ to float format explicitly with `float`, otherwise it keeps symbolic (like the usage of `pi`)
* When debugging, there is more than one solution for IK. So don't get throw off if your solution is different from the suggested one. Do a FK to verify.
* This approach of getting a lot of EE poses along the way and calculate IK for each of the pose works, but is fairly computational intensive and causing awkward jerking motion. The MoveIt! package does generate a very smooth motion. I am interested to find out how MoveIt! solves the motion planning problem in the future.

Things that I could not fix at the end:
* There is one thing I could not fix at the end, that is the object can not be gripped. The gripper closes for a solid 5 seconds (`ros::Duration(5.0).sleep()` is in place) but slides off the object when retriving. It can be seen that the object shakes a little bit when gripping, so contact is made. I also looked at the Gazebo grasp plugin, but did not mess with th e parameters there. As a result, I can only see the trajectory, but not see the robot actually gripping and dropping object.

Going further...
* I would like to study MoveIt! package to see how it achieves such smooth motion, like RRT* algorithm and other algorithms.
* Debug that object slipping issue above. 

#### 2. Results.

I was able to perform the pick and place movement 100%, although the object is not physically gripped. Below are some screenshots at different steps.


