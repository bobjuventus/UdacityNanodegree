## Project: Follow Me

---

### Required Steps for a Passing Submission:

1. Clone the project repo.
2. Fill out the TODO's in the project code.
3. Optimize your network and hyper-parameters.
4. Train your network and achieve an accuracy of 40% (0.40) using the Intersection over Union IoU metric which is final_grade_score at the bottom of your notebook.
5. Make a brief writeup report summarizing why you made the choices you did in building the network.


[//]: # (Image References)

[network]: ./misc_images/network.jpg
[error]: ./misc_images/error.png
[evaluation]: ./misc_images/evaluation.png


## [Rubric](https://review.udacity.com/#!/rubrics/1155/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### The write-up conveys the an understanding of the network architecture.

The network I am using can be shown here, basically composed of two encoding, 1x1 convolution and three decoding. Two of the decoding processes also involve skipping (concatenating) with two encoding layers.

![alt text][network]

As I did not collect any data myself, I just used the ~ 4000 images provided. I first used a simplier network and found that the cost keeps going down even after 20 epochs, so underfitting. I then used a more complicated network and validation cost starts to go up meaning overfitting. I ended up with this network based on the amount of data and also fine tuned the hyperparameters.


#### The write-up conveys the student's understanding of the parameters chosen for the the neural network.

Here are the parameters that I finally used.

* learning_rate = 0.003
* batch_size = 100
* num_epochs = 15
* steps_per_epoch = 250
* validation_steps = 50

I pretty much fixed Epoch at 15 due to training time (~ 30mins). For batch_size and steps_per_epoch, these are related to computer memory. My computer is quite good, so these numbers are relatively high. Learning_rate is what I played with the most. I started with 0.1 and noticed that the cost was all over the place, meaning that it needs to be lower. I then used 0.001 and ended up with both training and validation cost decreasing even after 15 epochs. The final score is around 0.37 so not passing. Finally I bumped it up to 0.003. Both training and validation cost still decrease very slowly after 15 epochs, but the final score is just above 0.4 which is good enough.

#### The student has a clear understanding and is able to identify the use of various techniques and concepts in network layers indicated by the write-up.

1 by 1 convolutions are used in FCN (Fully Convoluted Network) so that the network can take different input sizes. FCNs are useful also because they are able to keep spatial information as the data preserves in 4D (length, width, height, value). Notice using 1 by 1 convolutions does not mean the feature layer after encoding has height and width equal to 1. It usually has the smallest height and width, but it just equals to the previous layer. In my example, it is `40x40x128` after the 1 by 1 convolutions.

Fully (dense) connected layer are used in places where input image sizes are more fixed. AlexNet and VGGnet are famous examples. They lack the flexibility as in FCNs, also flattens the data to 2D (index, value) so lose spatial information. The last conv layer is simply densily connected to the full layer. However, it is able to capture the global feature, thus probably better for classification task.


#### The student has a clear understanding of image manipulation in the context of the project indicated by the write-up.

During the encoding, neighboring spatial information is grouped together and abstracted, eventually form into a feature tensor. At decoding, we try to restore the images. However, instead of getting the original image, we try to get interesting/desired images based on the abstracted features. For example, in this project, we try to label the output images into 3 classes: background, non-hero human, hero human.

#### The student displays a solid understanding of the limitations to the neural network with the given data chosen for various follow-me scenarios which are conveyed in the write-up.

Just with human data, this model won't work for another object (dog, cat, car, etc) out of the box. The reason is the mask (labelled) data is human, thus cost function was calculated with human data. To use the model for another object, we have to collect new mask data for the new object to re-train the model. However, we can probably use transfer learning, as many low level features between objects may be similar. In this scenerio, we may only retrain the last few layers based on the new object labelled data.


### Results

The training and validation loss after 15 epochs are both below 0.03, which is quite good. Both seem still may decrease with more epochs, but certainly not go up which means overfitting. 

![alt text][error]

For evaluation, it can be seen that when the quad is following behind the target, it's doing quite well. When the quad is on patrol and the target is not visable, it's also doing a good job noticing other people. When the quad tries to detect the target from far away, it does struggle with 144 false negatives, meaning in a lot of the images the hero exists but not detected. It could be because the number of pixels is quite small and does not make the threshold. This is difficult that if we decrease the threshold, other people that are close to the camera can have a body part with similar patterns thus some pixels labelled positive and give out false positive. More training data is definitely helpful.

Overall, the score is 0.402.

![alt text][evaluation]

At the end, I tried to use the model [model_weights1](https://github.com/bobjuventus/UdacityNanodegree/tree/master/RoboND-DeepLearning-Project/data/weights) in simulator, and it works quite well! The quad follows the hero all the time once it locks on the hero.

### Things to do in the future:
* The amount of data is obviously not enough for a high score. More data is needed, especially for detecting the target from far away scenerio. However, we have to be careful about the balance of data so we are not overfitting to a certain scenerio.
