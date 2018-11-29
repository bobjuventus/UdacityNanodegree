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

[DH]: ./misc_images/DH.png
[DH_Transform_between_frames]: ./misc_images/DH_Transform_between_frames.png
[rotation]: ./misc_images/rotation.png
[EE]: ./misc_images/EE.png
[Derivation]: ./misc_images/Derivation.jpg
[theta]: ./misc_images/theta.png
[step1]: ./misc_images/step1.png
[step2]: ./misc_images/step2.png
[step3]: ./misc_images/step3.png
[step4]: ./misc_images/step4.png
[grip]: ./misc_images/grip.png
[DH_cal]: ./misc_images/DH_cal.jpg
[matrices]: ./misc_images/matrices.png
[T0_G]: ./misc_images/T0_G.png
[theta4-6]: ./misc_images/theta4-6.png

## [Rubric](https://review.udacity.com/#!/rubrics/972/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

### Kinematic Analysis
#### 1. Run the forward_kinematics demo and evaluate the kr210.urdf.xacro file to perform kinematic analysis of Kuka KR210 robot and derive its DH parameters.

Here is the screen shot of the frames' setup using DH parameters.

![alt text][DH]

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

The way I obtained this table is from the table below, combining the info in the URDF file and the DH frame definition.

![alt text][DH_cal]

#### 3. Using the DH parameter table derived above, create individual transformation matrices about each joint. In addition, also generate a generalized homogeneous transform between base_link and gripper_link using only end-effector(gripper) pose.

For individual transformation matrices, they all follow the same format. As a result, I am just pasting the equations defined in code instead of pluging in the detailed numbers.

![alt text][DH_Transform_between_frames]

To print out these individual transformation matrices after plugging in the DH table, we get:

![alt text][matrices]

Finally, from base_link to gripper_link, we multiply all the transformation matrices and get the below matrix. This can be used for FK calculation.

![alt text][T0_G]

For the homogeneous transform between base_link and gripper_link using the EE pose, break it into the rotation part and translation part. For the rotation part, it is <img src="https://latex.codecogs.com/gif.latex?R_{xyz}&space;=&space;R_zR_yR_xR_{corr}" title="R_{xyz} = R_zR_yR_xR_{corr}" />.

Specifically,

![alt text][rotation]

where q1, q2 and q3 represent roll, pitch and yaw from EE pose.

For the translation part, it's simply <img src="https://latex.codecogs.com/gif.latex?[px,&space;py,&space;pz]^T" title="[px, py, pz]^T" />, which is from the EE pose as well. Putting it together, we get

![alt text][EE]

#### 4. Decouple Inverse Kinematics problem into Inverse Position Kinematics and inverse Orientation Kinematics; doing so derive the equations to calculate all individual joint angles.

These steps are involved:
* Get coordinates of wrist center <img src="https://latex.codecogs.com/gif.latex?t_{WC}" title="t_{WC}" />
* Calculate <img src="https://latex.codecogs.com/gif.latex?\theta_{1-3}" title="\theta_{1-3}" /> using geometry information
* Get <img src="https://latex.codecogs.com/gif.latex?R_{3->6}" title="R_{3->6}" /> symbolic matrix from transformation matrix <img src="https://latex.codecogs.com/gif.latex?R_{3->4}R_{4->5}R_{5->6}" title="R_{3->4}R_{4->5}R_{5->6}" /> and its actual value matrix from <img src="https://latex.codecogs.com/gif.latex?R_{0->6}" title="R_{0->6}" /> and <img src="https://latex.codecogs.com/gif.latex?R_{0->3}" title="R_{0->3}" />
* Compare the symbolic matrix and value matrix to calculate <img src="https://latex.codecogs.com/gif.latex?\theta_{4-6}" title="\theta_{4-6}" />

The derivation of <img src="https://latex.codecogs.com/gif.latex?\theta_2" title="\theta_2" /> and <img src="https://latex.codecogs.com/gif.latex?\theta_3" title="\theta_3" /> are below. <img src="https://latex.codecogs.com/gif.latex?\theta_1" title="\theta_1" /> is trivial. <img src="https://latex.codecogs.com/gif.latex?\theta_{4-6}" title="\theta_{4-6}" /> are from comparing the symbolic matrix and the value matrix.

![alt text][Derivation]

For <img src="https://latex.codecogs.com/gif.latex?\theta_{4-6}" title="\theta_{4-6}" />, we compare the value matrix calculated from the inverted matrix of <img src="https://latex.codecogs.com/gif.latex?R_{0->3}" title="R_{0->3}" /> and the symbolic matrix using the individual transformation matrix. We get:

![alt text][theta4-6]

By comparing these two matrices, we can get <img src="https://latex.codecogs.com/gif.latex?\theta_{4-6}" title="\theta_{4-6}" /> pretty easily by using cos and sin functions. The detailed codes for wrist center <img src="https://latex.codecogs.com/gif.latex?t_{WC}" title="t_{WC}" /> and all the angles are here:

![alt text][theta]

### Project Implementation

#### 1. Fill in the `IK_server.py` file with properly commented python code for calculating Inverse Kinematics based on previously performed Kinematic Analysis. Your code must guide the robot to successfully complete 8/10 pick and place cycles. Briefly discuss the code you implemented and your results. 

Most of the codes have been snipped and attached above. Here is the summary of the basic flow:

1. Define the symbols and create the DH parameters
2. Calculate all the transformation matrices between each DH frames
3. Define the extrinsic rotation from base link to EE link and the correction matrix between DH and URDF frame. Later we can plug in the value from the EE orientation to get the value rotation matrix.
4. From the EE position we can get the EE position in base link. Combined with the rotation matrix, we can get the WC (wrist center) position.
5. <img src="https://latex.codecogs.com/gif.latex?\theta_{1-3}" title="\theta_{1-3}" /> can be calculated using the WC position.
6. Knowing <img src="https://latex.codecogs.com/gif.latex?\theta_{1-3}" title="\theta_{1-3}" />, we can get the value matrix of <img src="https://latex.codecogs.com/gif.latex?R_{3->6}&space;=&space;R_{0->3}^{-1}R_{0->6}" title="R_{3->6} = R_{0->3}^{-1}R_{0->6}" />. We also know the symbolic matrix from individual transform matrix from step 2. <img src="https://latex.codecogs.com/gif.latex?\theta_{4-6}" title="\theta_{4-6}" /> can then be calculated by comparing the sympolic matrix and the value matrix.
7. Populate all the <img src="https://latex.codecogs.com/gif.latex?\theta" title="\theta" /> values back to the response object.


Useful things that I found and can be used in the future:
* **This one throws me off the most!** I got stuck at a bug for quite a while that involves the function `.inv("LU")`. For some reason, using this function to invert is not stable. Sometimes it returns the correct invert, but at certain angles (see test case 4 in IK_debug.py), it returns wrong invert. As a result, it gives me wrong <img src="https://latex.codecogs.com/gif.latex?\theta_{4-6}" title="\theta_{4-6}" /> time to time. Use `.transpose()` to calculate invert is much safer!
* All the matrix definitions should be outside the for loop to reduce runtime
* Be careful with the `atan2` usage. It matters where you put the negative sign
* I need to convert <img src="https://latex.codecogs.com/gif.latex?\theta" title="\theta" /> to float format explicitly with `float`, otherwise it keeps symbolic (like the usage of `pi`)
* When debugging, there is more than one solution for IK. So don't get throw off if your solution is different from the suggested one. Do a FK to verify.
* This approach of getting a lot of EE poses along the way and calculate IK for each of the pose works, but is fairly computational intensive and causing awkward jerking motion. The MoveIt! package does generate a very smooth motion. I am interested to find out how MoveIt! solves the motion planning problem in the future.

Things that I could not fix at the end:
* There is one thing I could not fix at the end, that is the object can not be gripped. The gripper closes for a solid 5 seconds (`ros::Duration(5.0).sleep()` is in place) but slides off the object when retriving. It can be seen that the object shakes a little bit when gripping, so contact is made. I also looked at the Gazebo grasp plugin, but did not mess with th e parameters there. As a result, I can only see the trajectory, but not see the robot actually gripping and dropping object.
* I fixed the wrong <img src="https://latex.codecogs.com/gif.latex?\theta_{4-6}" title="\theta_{4-6}" /> values by using `.transpose()` instead of `.inv("LU")`, but I am not sure why `.inv("LU")` gives me wrong invert values at certain joint angles yet.

A prove that the gripper actually grips the object.

![alt text][grip]

Going further...
* I would like to study MoveIt! package to see how it achieves such smooth motion, like RRT* algorithm and other algorithms.
* Debug that object slipping issue above. 

#### 2. Results.

I was able to perform the pick and place movement 100%, although the object is not physically gripped. Below are some screenshots at different steps.

_Moving to the target location (terminal outputs the angles of joints)_
![alt text][step1]

_Reached target location_
![alt text][step2]

_Moving to the drop-off location (again terminal outputs the angles of joints)_
![alt text][step3]

_Reached drop-off location (no object on gripper though)_
![alt text][step4]

#### 3. Verification of FK.

In `IK_debug.py`, I have tested all 4 test cases. Here are the results.
* For <img src="https://latex.codecogs.com/gif.latex?t_{WC}" title="t_{WC}" />, errors are all very small.
* For thetas, some of them are very small, but some of them are way off. This is due to multiple IK solutions given an EE pose.
* For FK verification, I added verification of quaternion and a 4th test case. **Notice:**, when using `.transpose()` to calculate inverse function, all errors are very small. But when using `.inv("LU")` to calculate inverse function, the position errors are small but the quaternion errors are way off sometimes. Again, this error in quaternion is not always, only happens at certain joint angles. The 4th test case was included for this purpose, try out yourself!
