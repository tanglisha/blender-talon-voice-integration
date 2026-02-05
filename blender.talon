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

# Numbered pan commands for precise control
view pan left <number_small>: user.blender_pan_left(number_small)
view pan right <number_small>: user.blender_pan_right(number_small)
view pan up <number_small>: user.blender_pan_up(number_small)
view pan down <number_small>: user.blender_pan_down(number_small)

# Viewport zoom commands
view zoom in: user.blender_zoom_in(5)
view zoom out: user.blender_zoom_out(5)

# Faster zooming with "far"
view zoom in far: user.blender_zoom_in(15)
view zoom out far: user.blender_zoom_out(15)

# Slower zooming with "slow"
view zoom in slow: user.blender_zoom_in(2)
view zoom out slow: user.blender_zoom_out(2)

# Numbered zoom commands for precise control
view zoom in <number_small>: user.blender_zoom_in(number_small)
view zoom out <number_small>: user.blender_zoom_out(number_small)

# Viewport orbit commands
view orbit left: user.blender_orbit_left(15)
view orbit right: user.blender_orbit_right(15)
view orbit up: user.blender_orbit_up(15)
view orbit down: user.blender_orbit_down(15)

# Faster orbiting with "far"
view orbit left far: user.blender_orbit_left(45)
view orbit right far: user.blender_orbit_right(45)
view orbit up far: user.blender_orbit_up(45)
view orbit down far: user.blender_orbit_down(45)

# Slower orbiting with "slow"
view orbit left slow: user.blender_orbit_left(5)
view orbit right slow: user.blender_orbit_right(5)
view orbit up slow: user.blender_orbit_up(5)
view orbit down slow: user.blender_orbit_down(5)

# Numbered orbit commands for precise control
view orbit left <number_small>: user.blender_orbit_left(number_small)
view orbit right <number_small>: user.blender_orbit_right(number_small)
view orbit up <number_small>: user.blender_orbit_up(number_small)
view orbit down <number_small>: user.blender_orbit_down(number_small)
