import numpy as np
import perception

# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle

                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0

                # Steering proportional to the deviation results in
                # small offsets on straight lines and
                # large values in corners and open areas, 0.2 value is trial and error
                offset = 0.2 * np.std(Rover.nav_angles)
                # Set steering to average angle+offset clipped to the range +/- 15
                Rover.steer = np.clip(np.mean((Rover.nav_angles+offset) * 180/np.pi), -15, 15)

                ### The code below tries to find the pixels on worldmap that the rover has visited, so the rover
                # does not explore those pixels. However, there may be bugs that only very few pixels are actually
                # non-zero, although visually those areas are already blue.

                # reverse the pixels back to x and y
                xpix = Rover.nav_dists * np.cos(Rover.nav_angles)
                ypix = Rover.nav_dists * np.sin(Rover.nav_angles)
                xpix_world, ypix_world = perception.pix_to_world(xpix, ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], Rover.scale)
                # those are visited should have blue pixel > 0, so this mask return the unvisited area
                mask = (Rover.worldmap[xpix_world, ypix_world, 2] == 0)
                
                xpix_world_zero = xpix_world[mask]
                ypix_world_zero = ypix_world[mask]
                # after reducing the xpix_world and ypix_world to only unvisited area, use self-defined world_to_pix
                # to map back to rover centric coord.
                xpix_zero, ypix_zero = perception.world_to_pix(xpix_world_zero, ypix_world_zero, \
                    Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], Rover.scale)
                # print("mask shape is: ", np.sum(mask))
                # print("xpix_world shape is: ", xpix_world.shape, "xpix_world_zero shape is: ", xpix_world_zero.shape)
                # print("xpix shape is: ", xpix.shape, "xpix_zero shape is: ", xpix_zero.shape)

                # get the reduced nav_dist and nav_angles
                fresh_nav_dist, fresh_nav_angles = perception.to_polar_coords(xpix_zero, ypix_zero)

                if len(fresh_nav_angles)/len(Rover.nav_angles) > 0.7: # 70% of the area is unexplored
                    print("!!!!!!!!!!!!Explore new area!!!!!!!!!!!!!!!!!!")
                    Rover.steer = np.clip(np.mean((fresh_nav_angles+offset) * 180/np.pi), -15, 15)
                else:
                    Rover.steer = np.clip(np.mean((Rover.nav_angles+offset) * 180/np.pi), -15, 15)


                ### below is another way of doing this, does not seem working as well
                # furthest_dist = np.max(Rover.nav_dists)
                # angle_at_fur_dist = Rover.nav_angles[np.argmax(Rover.nav_dists)]
                # # print("furthest_dist is: ", furthest_dist, "angle_at_fur_dist is: ", angle_at_fur_dist, "np.argmax: ", np.argmax(Rover.nav_dists))
                # in_range_pix = np.nonzero(np.logical_and(Rover.nav_angles>=angle_at_fur_dist-2, Rover.nav_angles<=angle_at_fur_dist+2))
                # area_around_furthest_dist = np.sum(Rover.nav_dists[in_range_pix])
                # # print("area_around_furthest_dist is: ", area_around_furthest_dist)
                # # Now let's also find the global x, y value in Rover.worldmap
                # xpix = furthest_dist * np.cos(angle_at_fur_dist)
                # ypix = furthest_dist * np.sin(angle_at_fur_dist)
                # xpix_world, ypix_world = perception.pix_to_world(xpix, ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], Rover.scale)
                # print("xpix_world and ypix_world are:", xpix_world, ypix_world)

                # if furthest_dist > Rover.nav_dists_thres and np.abs(Rover.mean_angles - angle_at_fur_dist*180/np.pi) < 20 and \
                # area_around_furthest_dist > Rover.area_thres and Rover.worldmap[xpix_world, ypix_world, :].all() == 0:
                #     print("!!!!!!!!!!!!Explore new map!!!!!!!!!!!!!!!!!!")
                #     Rover.steer = np.clip(angle_at_fur_dist * 180/np.pi, -15, 15)
                # else:
                #     Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)

                ### Now we want to check if the rover gets stuck
                # fill in the history list first, if not, update the list. This includes the vel, yaw and pos list
                if None in Rover.vel_hist:
                    ind_None = next(i for i, j in enumerate(Rover.vel_hist) if j is None)
                    Rover.vel_hist[ind_None] = Rover.vel
                else:
                    Rover.vel_hist = Rover.vel_hist[1:] + [Rover.vel]

                if None in Rover.yaw_hist:
                    ind_None = next(i for i, j in enumerate(Rover.yaw_hist) if j is None)
                    Rover.yaw_hist[ind_None] = Rover.yaw
                else:
                    Rover.yaw_hist = Rover.yaw_hist[1:] + [Rover.yaw]

                if None in Rover.pos_hist:
                    ind_None = next(i for i, j in enumerate(Rover.pos_hist) if j is (None, None))
                    Rover.pos_hist[ind_None] = Rover.pos
                else:
                    Rover.pos_hist = Rover.pos_hist[1:] + [Rover.pos]

                # check if it gets stuck, 4 criterias:
                # 1) vel is around 0. 2) pos does not change much. 3) yaw does not change much (so it's not in stop mode)
                # 4) time elapses more than 3 seconds, so when switching back from 'back' mode, it stays in forward mode
                # for at least 3 seconds.
                if None not in Rover.vel_hist and None not in Rover.yaw_hist and None not in Rover.pos_hist:
                    if Rover.vel_hist[0] < 0.1 and Rover.vel_hist[-1] < 0.1 and \
                        np.sqrt((Rover.pos_hist[-1][0] - Rover.pos_hist[0][0])**2 + (Rover.pos_hist[-1][1] - Rover.pos_hist[0][1])**2) < 2 \
                        and np.abs(Rover.yaw_hist[-1] - Rover.yaw_hist[0]) < 10 \
                        and (Rover.total_time - Rover.start_forward_time) > 3:
                        Rover.throttle = 0
                        Rover.brake = 0
                        Rover.steer = 0
                        Rover.start_back_time = Rover.total_time
                        Rover.mode = 'back'

            ### If there's a lack of navigable terrain pixels then go to 'stop' mode

            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    offset = 0.2 * np.std(Rover.nav_angles)
                    Rover.steer = offset + np.clip(np.mean((Rover.nav_angles+offset) * 180/np.pi), -15, 15)

                    # Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'

        # If we're in 'back' mode then make different decisions
        elif Rover.mode == 'back':
            # if stuck in back mode for 5 seconds, maybe something is in the back. We either forward or stop.
            if Rover.total_time - Rover.start_back_time > 5:
                if len(Rover.nav_angles) >= Rover.stop_forward:
                    Rover.start_forward_time = Rover.total_time
                    Rover.mode = 'forward'
                elif len(Rover.nav_angles) < Rover.stop_forward:
                    Rover.mode = 'stop'
            # below situation is when the rover has not been stuck for 5 seconds
            else:
                # we have gain enough speed back
                if Rover.vel < -0.5:
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'
                # we have not gained enough speed, keep backing
                elif Rover.vel >= -0.5:
                    Rover.throttle = -Rover.throttle_set
                    Rover.brake = 0
                    Rover.steer = 0


    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    
    return Rover

