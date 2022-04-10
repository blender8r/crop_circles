# Geometry generation code is derived from examples in Jeremy Behreandt's 
# Creative Coding in Blender 2.92 blog post. The original can be found here: 
# https://behreajj.medium.com/

import bpy
import math
from mathutils import Vector

def add_crop_circle(props):
    
    # Create grease pencil stuff
    grease_data = bpy.data.grease_pencils.new("CropCircle")
    grease_layers = grease_data.layers
    line_layer = grease_layers.new("line")  
    grease_frames = line_layer.frames   
    active_frame = grease_frames.new(
        bpy.context.scene.frame_current,
        active=True)
    frame_strokes = active_frame.strokes

    # TODO: As far as I can tell you're only allowed to assign one material per
    # grease pencil object so we need to manage two sets of grease pencil 
    # objects and two materials...boo. If I can figure out how to apply different
    # materials per layer, we could streamline this by eliminating the 2nd grease
    # pencil object and just make an extra material.
    if props.show_pivots:
        pivot_data = bpy.data.grease_pencils.new("Pivots")
        pivot_layers = pivot_data.layers
        pivot_layer = pivot_layers.new("pivots")
        pivot_frames = pivot_layer.frames
        active_pivot_frame = pivot_frames.new(bpy.context.scene.frame_current)
        pivot_frame_strokes = active_pivot_frame.strokes

    arc_count = props.num_shapes
    point_count = props.num_segments

    i_range = range(0, arc_count, 1)
    i_to_theta = math.tau / arc_count 

    j_range = range(0, point_count, 1)
    j_to_fac = 1.0 / (point_count - 1.0)

    theta_offset = math.tau / props.arc_length  #3.0

    orbit_radius = props.orbit_radius[0]  
    minor_radius = props.orbit_radius[1]  

    # Variables for controlling the line thickness via the pressure property
    min_pressure = props.line_thickness[0] 
    max_pressure = props.line_thickness[1] 

    for i in i_range:
        i_theta = i * i_to_theta

        active_stroke = frame_strokes.new()
        active_stroke.line_width = 12.0
        active_stroke.hardness = 1.0
        active_stroke.start_cap_mode = 'FLAT'
        active_stroke.end_cap_mode = 'FLAT'

        stroke_points = active_stroke.points
        stroke_points.add(point_count)

        orbit = orbit_radius
        
        if i % 2 != 0:
            orbit = orbit_radius * props.orbit_offset

        origin = Vector(
            (orbit * math.cos(i_theta),
            orbit * math.sin(i_theta),
            0.0))

        # Draw pivot stroke if user wants to
        if props.show_pivots:
            active_pivot_stroke = pivot_frame_strokes.new()
            active_pivot_stroke.line_width = props.pivot_size
            active_pivot_stroke.hardness = 1.0
            active_pivot_stroke.start_cap_mode = 'FLAT'
            active_pivot_stroke.end_cap_mode = 'FLAT'

            pivot_stroke_points = active_pivot_stroke.points
            pivot_stroke_points.add(arc_count)

            pivot_point = pivot_stroke_points[i]
            pivot_point.pressure = 1.0
            pivot_point.co = origin

        orientation = props.orientation / 180.0
        j_theta_origin = (math.pi * orientation) + (i_theta - theta_offset)
        j_theta_dest = (math.pi * orientation) + (i_theta + theta_offset)

        for j in j_range:  
            j_fac = j * j_to_fac  
            j_theta = (1.0 - j_fac) * j_theta_origin \
                + j_fac * j_theta_dest

            point = stroke_points[j]

            osc = props.line_taper[0] + props.line_taper[1] * math.cos(math.tau * j_fac - math.pi)
            point.pressure = (1.0 - osc) * min_pressure \
                + osc * max_pressure

            point_local = Vector(
                (minor_radius * math.cos(j_theta),
                minor_radius * math.sin(j_theta),
                0.0))
            point.co = origin + point_local
        
    # Populate grease pencil object with the data we generated    
    grease_obj = bpy.data.objects.new(grease_data.name, grease_data)
    bpy.context.collection.objects.link(grease_obj)

    # Create and assign material 
    mat_name = "Mat_CropCircle"
    if mat_name in bpy.data.materials.keys():
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        bpy.data.materials.create_gpencil_data(mat)

    # Do the same for the pivot grease pencil object if we're using it
    if props.show_pivots:
        pivot_obj = bpy.data.objects.new(pivot_data.name, pivot_data)
        bpy.context.collection.objects.link(pivot_obj)

        # create and assign material for pivots 
        mat_pivot_name = "Mat_CropCircle_Pivot"
        if mat_pivot_name in bpy.data.materials.keys():
            mat_pivot = bpy.data.materials[mat_pivot_name]
        else:
            mat_pivot = bpy.data.materials.new(name=mat_pivot_name)
            bpy.data.materials.create_gpencil_data(mat_pivot)

        mat_pivot.grease_pencil.color = (props.pivot_color)
        pivot_data.materials.append(mat_pivot)
        pivot_obj.active_material_index = 0
        # setting the shader on this so that we don't draw a line from
        # the pivot to the origin. (Better way to do this than in the material?)
        pivot_obj.active_material.grease_pencil.mode = 'DOTS'
        pivot_obj.rotation_euler = ((math.pi/2), 0.0, 0.0)
    
    mat.grease_pencil.color = (props.color) #black
    grease_data.materials.append(mat)
    grease_obj.active_material_index = 0

    # rotate grease pencil 90 deg to face forward to work better in 2D animation mode
    grease_obj.rotation_euler = ((math.pi/2), 0.0, 0.0)
    
