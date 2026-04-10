# drone-defence

This program is a simple simulation that immetates drone physics. It also shows a method of drone interception.

When the program is ran:
• A window is opened.
• 7 cuboids
• are made, 3 greens, 3 blues and 1 red.
• A green box is a radar. This radar shoots a red laser. This is a laser-distance sensor.
• A blue box is a sentry, after 2.5 seconds, a blue beam, which are radio waves, is shot.
• After the radio waves are launched, the drone will enter a jammed state.
• The red box is the drone.
• Once the drone is jammed, the drone will do random inputs, based of a random bias between -1 and 1 for all 3 rotations. Along with the throttle will be randomly set between 0 and 0.6666
• If the drone touches the ground, then the drone will become static and point upwards.

These images are from when the drone is initially static:
![When the program starts](images\image.png)
![When the drone is being intercepted](images\image-1.png)
![When the drone hits the ground](images\image-2.png)

Theses images are from when the drone starts moving from left to right:
![When the program starts](images\image-3.png)
![When the drone is being intercpted](images\image-4.png)
![When the drone has successfully been intercepted](images\image-5.png)

And these images are from when the drone starts moving diagonally, left to right and close to far:
![When the program starts](images\image-6.png)
![When the drone is being intercepted](images\image-7.png)
![When the drone has successfully been intercepted](images\image-8.png)