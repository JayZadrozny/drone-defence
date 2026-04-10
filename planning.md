# **planning**

Simple plan of what to make and do.

# rendering

• create a simple rendering file/script
• libraries like: pygame, opengl, moderngl, pyopengl, glfw
• simple rending at first, i.e - cuboids for everything. Potentially 3d CAD models imported.

# how it will work

• Radars will detect the drone and will point a laser distance sensor at the drone to get the distance from the radar to the drone.
• Using radars and laser distance sensors, the position, direction and speed of the drone can be found using some mathematics and multiple recordings. Ensure that the radar script cannot access any drone variables or data directly.
• Sentries will fire targeted radio waves at the drone to jam the drone.
• With multiple sentries firing at the drone, A 'hotspot' will be formed around the drone causing it to jam. This also means the jam will happen quicker and will be more accurate.

# drone logic

• Once jammed, the drone will enter a jammed state where it can not be controlled and will execute random events.
• An upwards force will be applied to the drone based on the orentation of the drone in order to mimmick lift.
• The drone will have a drag constant and the drone will have gravity applied.

# sentry logic

• The sentry would fire radio waves at the drones.
• The radio waves would be directed at a targeted area to prevent the waves affecting other devices.
• The sentry has a 2-point arm. This is to enure the sentry can look around in every direction
• The 2-point arm ensures the logic will be simple and less areas for errors.