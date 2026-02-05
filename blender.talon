app.name: Blender
-
# Tag to indicate Blender is active
tag(): user.blender_running

# Viewport panning commands
view pan left: user.blender_pan_left(100)
view pan right: user.blender_pan_right(100)
view pan up: user.blender_pan_up(100)
view pan down: user.blender_pan_down(100)

# Faster panning with "far"
view pan left far: user.blender_pan_left(300)
view pan right far: user.blender_pan_right(300)
view pan up far: user.blender_pan_up(300)
view pan down far: user.blender_pan_down(300)

# Slower panning with "slow"
view pan left slow: user.blender_pan_left(30)
view pan right slow: user.blender_pan_right(30)
view pan up slow: user.blender_pan_up(30)
view pan down slow: user.blender_pan_down(30)
