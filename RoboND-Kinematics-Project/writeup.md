## Project: Kinematics Pick & Place

---


**Steps to complete the project:**  


1. Set up your ROS Workspace.
2. Download or clone the [project repository](https://github.com/udacity/RoboND-Kinematics-Project) into the ***src*** directory of your ROS Workspace.  
3. Experiment with the forward_kinematics environment and get familiar with the robot.
4. Launch in [demo mode](https://classroom.udacity.com/nanodegrees/nd209/parts/7b2fd2d7-e181-401e-977a-6158c77bf816/modules/8855de3f-2897-46c3-a805-628b5ecf045b/lessons/91d017b1-4493-4522-ad52-04a74a01094c/concepts/ae64bb91-e8c4-44c9-adbe-798e8f688193).
5. Perform Kinematic Analysis for the robot following the [project rubric](https://review.udacity.com/#!/rubrics/972/view).
6. Fill in the `IK_server.py` with your Inverse Kinematics code. 


[//]: # (Image References)

[image1]: ./misc_images/misc1.png
[image2]: ./misc_images/misc3.png
[image3]: ./misc_images/misc2.png

## [Rubric](https://review.udacity.com/#!/rubrics/972/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

### Kinematic Analysis
#### 1. Run the forward_kinematics demo and evaluate the kr210.urdf.xacro file to perform kinematic analysis of Kuka KR210 robot and derive its DH parameters.

Here is the screen shot of the frames' setup using DH parameters.

![DH.png](:storage/3641ecc9-0c89-44d9-b57a-c3eee056bef1/85cf7150.png)

![alt text][image1]

#### 2. Below is the DH-parameter table created according to this frame definition and the URDF file.

Links | alpha(i-1) | a(i-1) | d(i-1) | theta(i)
--- | --- | --- | --- | ---
0->1 | 0 | 0 | 0.75 | q1
1->2 | - pi/2 | 0.35 | 0 | -pi/2 + q2
2->3 | 0 | 1.25 | 0 | q3
3->4 | - pi/2 | -0.054 | 1.5 | q4
4->5 | pi/2 | 0 | 0 | q5
5->6 | - pi/2 | 0 | 0 | q6
6->EE | 0 | 0 | 0.303 | 0

#### 3. Using the DH parameter table derived above, create individual transformation matrices about each joint. In addition, also generate a generalized homogeneous transform between base_link and gripper_link using only end-effector(gripper) pose.

For individual transformation matrices, they all follow the same format. As a result, I am just pasting the equations defined in code instead of pluging in the detailed numbers.

![DH_Transform_between_frames.png](:storage/3641ecc9-0c89-44d9-b57a-c3eee056bef1/c4c944b4.png)

For the homogeneous transform between base_link and gripper_link using the EE pose, break it into the rotation part and translation part. For the rotation part, it is $R_{xyz} = R_zR_yR_xR_{corr}$.

Specifically,

![rotation.png](:storage/3641ecc9-0c89-44d9-b57a-c3eee056bef1/4a91cad1.png)
where q1, q2 and q3 represent roll, pitch and yaw from EE pose.

For the translation part, it's simply $[px, py, pz]^T$, which is from the EE pose as well. Putting it together, we get

![EE.png](:storage/3641ecc9-0c89-44d9-b57a-c3eee056bef1/f4e9b713.png)

#### 4. Decouple Inverse Kinematics problem into Inverse Position Kinematics and inverse Orientation Kinematics; doing so derive the equations to calculate all individual joint angles.

These steps are involved:
* Get coordinates of wrist center $t_{WC}$
* Calculate $\theta_{1-3}$ using geometry information
* Get $R_{3->6}$ symbolic matrix from transformation matrix $R_{3->4}R_{4->5}R_{5->6}$ and its actual value matrix from $R_{0->6}$ and $R_{0->3}$
* Compare the symbolic matrix and value matrix to calculate $\theta_{4-6}$

The derivation of $\theta_2$ and $\theta_3$ are below. $\theta_1$ is trivial. $\theta_{4-6}$ are from comparing the symbolic matrix and the value matrix.

![Derivation.jpg](:storage/3641ecc9-0c89-44d9-b57a-c3eee056bef1/c5d65828.jpg)

The detailed codes for wrist center $t_{WC}$ and all the angles are here:

![theta.png](:storage/3641ecc9-0c89-44d9-b57a-c3eee056bef1/6b883a7e.png)

![alt text][image2]

### Project Implementation

#### 1. Fill in the `IK_server.py` file with properly commented python code for calculating Inverse Kinematics based on previously performed Kinematic Analysis. Your code must guide the robot to successfully complete 8/10 pick and place cycles. Briefly discuss the code you implemented and your results. 

Most of the codes have been snipped and attached above. Here is the summary of the basic flow:

1. Define the symbols and create the DH parameters
2. Calculate all the transformation matrices between each DH frames
3. Define the extrinsic rotation from base link to EE link and the correction matrix between DH and URDF frame. Later we can plug in the value from the EE orientation to get the value rotation matrix.
4. From the EE position we can get the EE position in base link. Combined with the rotation matrix, we can get the WC (wrist center) position.
5. $\theta_{1-3}$ can be calculated using the WC position.
6. Knowing $\theta_{1-3}$, we can get the value matrix of $R_{3->6} = R_{0->3}^{-1}R_{0->6}$. We also know the symbolic matrix from individual transform matrix from step 2. $\theta_{4-6}$ can then be calculated by comparing the sympolic matrix and the value matrix.
7. Populate all the $\theta$ values back to the response object.


Useful things that I found and can be used in the future:
* All the matrix definitions should be outside the for loop to reduce runtime
* Be careful with the `atan2` usage. It matters where you put the negative sign
* I need to convert $\theta$ to float format explicitly with `float`, otherwise it keeps symbolic (like the usage of `pi`)
* When debugging, there is more than one solution for IK. So don't get throw off if your solution is different from the suggested one. Do a FK to verify.
* This approach of getting a lot of EE poses along the way and calculate IK for each of the pose works, but is fairly computational intensive and causing awkward jerking motion. The MoveIt! package does generate a very smooth motion. I am interested to find out how MoveIt! solves the motion planning problem in the future.

Things that I could not fix at the end:
* There is one thing I could not fix at the end, that is the object can not be gripped. The gripper closes for a solid 5 seconds (`ros::Duration(5.0).sleep()` is in place) but slides off the object when retriving. It can be seen that the object shakes a little bit when gripping, so contact is made. I also looked at the Gazebo grasp plugin, but did not mess with th e parameters there. As a result, I can only see the trajectory, but not see the robot actually gripping and dropping object.

Going further...
* I would like to study MoveIt! package to see how it achieves such smooth motion, like RRT* algorithm and other algorithms.
* Debug that object slipping issue above. 

#### 2. Results.

I was able to perform the pick and place movement 100%, although the object is not physically gripped. Below are some screenshots at different steps.



And just for fun, another example image:
![alt text][image3]


