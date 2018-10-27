## Project: Search and Sample Return
### Below is my writeup

---


**The goals / steps of this project are the following:**  

###Training / Calibration**

**Notice: the ipynb file is under RoboND-Rover-Project folder, not under `/code` folder. All the images have been displayed in the notebook.**  

* The functions in the Jupyter Notebook have been tested. Additional functions to detect obstacles and samples of interest (golden rocks) are added.
* The rotate and translate functions in the coordinate transformations have been added. A new function `world_to_pix()` was also added for later autonomous mode.
* The `process_image()` function was modified with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` contained the camera image, perspective view, ground truth, rover-centric view and overlay on the ground truth.
* The video was generated and attached.


* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.

### Autonomous Navigation and Mapping

**Most comments have been added inside the functions. Below is what I changed to `perception.py`, `driver_rover.py`, `supporting_functions.py` and `decision.py`.**

#### 1. `perception.py`: I have filled up all the functions in the jupyter notebook, including the added `world_to_pix()` function. At the end, the `Rover.worldmap` is updated with `R`, `G` and `B` channels corresponding to obstacles, rocks and navigable terrain.

#### 2. `driver_rover.py`: Added a few parameters to the `RoverState()` class. Mostly to track the history of vel, yaw and pos, so to decide if the rover is stuck. Also added some threshold values.

#### 3. `supporting_functions.py`: Did not change much other than commenting out some printouts.

#### 4. `decision.py`: This one has the most change. Mostly I have made the 3 changes below.

* Added an offset to the `Rover.steer` to the rover slightly prefers steering left. This helps the rover stick closer to the left wall.
* Try to let the rover explore new area instead of visit explored area. This is done by using pix_to_world to check if any pixels have `B` channel == 0 meaning it is unexplored, then using world_to_pix to get those unexplored pixels in rover-centric coordinate. After this, steering using the unexplored pixels instead of the whole navigable pixels. This part is still buggy, that only very few pixels are actually non-zero, although visually those areas are already blue on the mini map. Over time it seems more pixels are non-zero though.
* Added a 'back' mode to get the rover out when it is stuck. Basically, when it is not moving for a few seconds and it is in 'forward' mode, let it back off. If it stucks in the 'back' mode, let it move forward and resume into 'forward' mode.

Before making these changes, the rover navigates less than 30% of the map constantly (only explore one branch) and gets stuck constantly. After making the changes, it navigates over 70% of the map most of the time and rarely gets stuck.

#### Things to improve:
* The rover still sometimes revisit the explored area instead of an unexplored branch. This is partially caused by the buggy function implemented.
* The rover should have a speed change, that it moves faster when the road is wide open and slower when an obstacle may be ahead.
* Did not have time to implement picking up the rock.

**My simulator settings are: 840x524, quality is Good, frames per second is ~30 at its best.**
