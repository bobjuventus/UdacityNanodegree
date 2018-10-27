import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

# Identify pixels below the threshold for obstacle
# Threshold of RGB <= 160 does a nice job of identifying obstacle pixels only
def obstacle_thresh(img, warped_full_image, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that either pixel be below the corresponding threshold value in RGB
    # below_thresh will now contain a boolean array with "True"
    # where threshold was met
    below_thresh = (img[:,:,0] <= rgb_thresh[0]) \
                | (img[:,:,1] <= rgb_thresh[1]) \
                | (img[:,:,2] <= rgb_thresh[2])
    
    below_thresh = below_thresh & (warped_full_image[:,:,0] > 0)
    # Index the array of zeros with the boolean array and set to 1
#     print(below_thresh)
    color_select[below_thresh] = 1
    # Return the binary image
    return color_select

# Identify pixels between boundaries for yellow rocks
# !!!Notice here the img is the original/unwrapped image! To have a slightly higher resolution
def rock_thresh(unwrapped_img, source, destination):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(unwrapped_img[:,:,0])
    # Use HSV boundaries for yellow rocks selection
    img_bgr = unwrapped_img[...,::-1]
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)  
    lower_yellow = np.array([20, 150, 100], np.uint8)
    upper_yellow = np.array([40, 255, 255], np.uint8)
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    res = cv2.bitwise_and(unwrapped_img, unwrapped_img, mask= mask)
    res_wrap = perspect_transform(res, source, destination)
#     print(res.shape)
    # Index the array of zeros with the boolean array and set to 1
    color_select[res_wrap[:,:,0].nonzero()] = 1
    # Return the binary image
    return color_select


# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

def world_to_pix(x_pix_world, y_pix_world, xpos, ypos, yaw, world_size, scale):
    xpix_tran = (x_pix_world - xpos) * scale
    ypix_tran = (y_pix_world - ypos) * scale
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix_tran * np.cos(yaw_rad)) + (ypix_tran * np.sin(yaw_rad))           
    ypix_rotated = -(xpix_tran * np.sin(yaw_rad)) + (ypix_tran * np.cos(yaw_rad))
    return xpix_rotated, ypix_rotated

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    # 2) Apply perspective transform
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image

    # 5) Convert map image pixel values to rover-centric coords
    # 6) Convert rover-centric pixel values to world coordinates
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    
    # 1) Define source and destination points for perspective transform
    # 2) Apply perspective transform
    # Define calibration box in source (actual) and destination (desired) coordinates
    # These source and destination points are defined to warp the image
    # to a grid where each 10x10 pixel square represents 1 square meter
    # The destination box will be 2*dst_size on each side
    dst_size = 5 
    # Set a bottom offset to account for the fact that the bottom of the image 
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], 
                      [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                      ])
    warped = perspect_transform(Rover.img, source, destination)

    # Get the pixels that the rover cannot see, specifically the triangles at the bottom left and right
    full_image = np.ones_like(Rover.img).astype(np.float)
    warped_full_image = perspect_transform(full_image, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples, binary image
    nav_threshed = color_thresh(warped)
    obstacle_threshed = obstacle_thresh(warped, warped_full_image)
    rock_threshed = rock_thresh(Rover.img, source, destination)

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:,:,0] = obstacle_threshed*255
    Rover.vision_image[:,:,1] = rock_threshed*255
    Rover.vision_image[:,:,2] = nav_threshed*255

    # 5) Convert map image pixel values to rover-centric coords
    # Make worldmap, R is obstacle, G is rock, B is navigable
    obstacle_x, obstacle_y = rover_coords(obstacle_threshed)
    rock_x, rock_y = rover_coords(rock_threshed)
    nav_x, nav_y = rover_coords(nav_threshed)

    # 6) Convert rover-centric pixel values to world coordinates
    obstacle_x_world, obstacle_y_world = pix_to_world(obstacle_x, obstacle_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], Rover.scale)
    rock_x_world, rock_y_world = pix_to_world(rock_x, rock_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], Rover.scale)
    nav_x_world, nav_y_world = pix_to_world(nav_x, nav_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], Rover.scale)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 255
    Rover.worldmap[rock_y_world, rock_x_world, 1] += 255
    Rover.worldmap[nav_y_world, nav_x_world, 2] += 255

    # 8) Convert rover-centric pixel positions to polar coordinates
    dist, angles = to_polar_coords(nav_x, nav_y)
    mean_dir = np.mean(angles)
    Rover.nav_dists = dist
    Rover.nav_angles = angles
    Rover.mean_angles = mean_dir
    # Rover.steer = mean_dir # Nah, actually not needed
    
    return Rover