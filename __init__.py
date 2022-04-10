bl_info = {
    "name": "Crop Circles",
    "author": "Tim Dobbert (Analog Sketchbook), Jeremy Behreandt",
    "version": (0, 0, 1),
    "blender": (2, 93, 0),
    "location": "View3D > Add",
    "description": ("Creates a circular patterns as a grease pencil objects."),
    "doc_url": "",
    "category": "Add Grease Pencil",
}

if "bpy" in locals():
    import importlib
    importlib.reload(utils)
else:
    from . import utils

import bpy
import time, random

from bpy.types import (
        Operator,
        Menu
        )
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        IntVectorProperty,
        StringProperty,
        )

settings = {
    'num_shapes': 24,
    'num_segments': 64,
    'orbit_radius': [1.0,0.5],
    'orbit_offset': 0.875,
    'arc_length': 3.0,
    'orientation': 180,
    'line_thickness': [0.5, 5.0],
    'line_taper': [0.5, 0.5],
    'color': [0.0, 0.0, 0.0, 1.0],
    'show_pivots': False,
    'pivot_size': 25.0,
    'pivot_color': [1.0, 0.0, 0.0, 1.0]  
    }

default_settings = {
    'num_shapes': 24,
    'num_segments': 64,
    'orbit_radius': [1.0,0.5],
    'orbit_offset': 0.875,
    'arc_length': 3.0,
    'orientation': 180,
    'line_thickness': [0.5, 5.0],
    'line_taper': [0.5, 0.5],
    'color': [0.0, 0.0, 0.0, 1.0],
    'show_pivots': False,
    'pivot_size': 25.0,
    'pivot_color': [1.0, 0.0, 0.0, 1.0] 
    }

reset = False
surprise = False

# use these lists to exempt any settings when use Reset or SurpriseMe buttons
reset_exempt = ['show_pivots'] # ['show_pivots','color', 'pivot_color']
surprise_exempt = ['show_pivots', 'color', 'pivot_color']

class Reset(Operator):
    """This operator resets the settings to default."""
    bl_idname = 'crop_circle.reset'
    bl_label = 'Reset'

    def execute(self, context):
        global reset

        reset = True 

        return {'FINISHED'}


class SurpriseMe(Operator):
    """This operator generates random settings."""
    bl_idname = 'crop_circle.surprise_me'
    bl_label = 'Surprise Me'

    def execute(self, context):
        global surprise, settings

        settings['num_shapes'] = random.randrange(2, 128)
        settings['num_segments'] = random.randrange(2, 72)
        settings['orbit_radius'] = [random.random() + 0.001, random.random() + 0.001]
        settings['orbit_offset'] = random.random()
        settings['arc_length'] = random.random() * 8.0
        settings['orientation'] = random.randrange(0, 360)
        settings['line_thickness'] = [random.random() * 5.0, random.random() * 5.0]
        settings['line_taper'] = [random.random() * 5.0, random.random() * 5.0]
        #settings['color'] = [random.random(), random.random(),random.random(), random.random()]

        surprise = True

        return {'FINISHED'}


class AddCropCircle(Operator):
    bl_idname = "gpencil.crop_circle_add"
    bl_label = "Crop Circle"
    bl_options = {'REGISTER', 'UNDO'}

    # Keep the strings in memory, see T83360.
    _objectList_static_strings = []

    def objectList(self, context):
        objects = AddCropCircle._objectList_static_strings
        objects.clear()

        for obj in bpy.data.objects:
            if (obj.type in {'GPENCIL'}) and (obj.name not in {'crop_circle'}):
                objects.append((obj.name, obj.name, ""))

        if not objects:
            objects.append(('NONE', "No objects", "No appropriate objects in the Scene"))

        return objects

    def update_crop_circle(self, context):
        self.do_update = True

    def no_update_crop_circle(self, context):
        self.do_update = False

    do_update: BoolProperty(
        name='Do Update',
        default=True, options={'HIDDEN'}
        )
    num_shapes: IntProperty(
        name='No. Shapes',
        description='Number of shapes to generate',
        min=1,
        default=settings['num_shapes'], update=update_crop_circle
        )
    num_segments: IntProperty(
        name='No. Segments',
        description='The number of segments in circles/spheres',
        min=2,
        max=72,
        default=settings['num_segments'], update=update_crop_circle
        )
    orbit_radius: FloatVectorProperty(
        name='Orbit Radius',
        description='Offset from center point',
        min=0.1,
        default=settings['orbit_radius'],
        size=2, update=update_crop_circle
        )
    orbit_offset: FloatProperty(
        name="Offset",
        description='Offsets half the arcs',
        min=.01,
        default=settings['orbit_offset'], update=update_crop_circle
        )
    arc_length: FloatProperty(
        name=" Arc Length  ",
        description='Length of arc on smaller circles',
        min=.001,
        default=settings['arc_length'], update=update_crop_circle
        )
    orientation: IntProperty(
        name=" Orientation",
        description='Orientation of smaller circles',
        min = 0,
        max = 360,
        default=settings['orientation'], update=update_crop_circle
        )
    line_thickness: FloatVectorProperty(
        name='Line Thickness',
        description='Min/Max line thickness',
        min=0.01,
        default=settings['line_thickness'],
        size=2, update=update_crop_circle
        )
    line_taper: FloatVectorProperty(
        name='Line Taper',
        description='Line Taper',
        default=settings['line_taper'],
        size=2, update=update_crop_circle
        )
    color: FloatVectorProperty(
        name = "Color",
        subtype = "COLOR",
        default = settings['color'],
        min = 0.0, max = 1.0,
        size=4, update=update_crop_circle
        )
    show_pivots: BoolProperty(
        name='Show Pivots',
        description='Generates pivot object',
        default=settings['show_pivots'], update=update_crop_circle
        )
    pivot_size: FloatProperty(
        name=" Pivot Size  ",
        description='Diameter of pivots',
        min=1.0,
        default=settings['pivot_size'], update=update_crop_circle
        )
    pivot_color: FloatVectorProperty(
        name = "Pivot Color",
        subtype = "COLOR",
        default = settings['pivot_color'],
        min = 0.0, max = 1.0,
        size=4, update=update_crop_circle
        )


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        row = box.row()
        row.prop(self, 'num_shapes') 
        row.prop(self, 'num_segments')

        row = box.row()
        row.prop(self, 'orbit_radius')

        row = box.row()
        row.prop(self, 'orbit_offset')

        row = box.row()
        row.prop(self, 'arc_length')

        row = box.row()
        row.prop(self, 'orientation')

        row = box.row()
        row.prop(self, 'line_thickness')

        row = box.row()
        row.prop(self, 'line_taper')

        row = box.row()
        row.prop(self, 'color')

        row = box.row()
        row.operator('crop_circle.reset')
        row.operator('crop_circle.surprise_me')

        row = box.row()
        row.label(text="Pivots")

        row = box.row()
        row.prop(self, 'show_pivots')

        row = box.row()
        row.prop(self, 'pivot_size')

        row = box.row()
        row.prop(self, 'pivot_color')


    def execute(self, context):
        # Ensure the use of the global variables
        global shapes, reset, surprise, settings
        start_time = time.time()
        
        if reset:
            for a, b in default_settings.items():
                if a not in reset_exempt:
                    setattr(self, a, b)
            reset = False
        if surprise:
            for a, b in settings.items():
                if a not in surprise_exempt:
                    setattr(self, a, b)
            surprise = False    

        # If we need to set the properties from a preset then do it here
        if not self.do_update:
            return {'PASS_THROUGH'}
        utils.add_crop_circle(self)
        
        print("CropCircle creation in %0.1fs" % (time.time() - start_time))

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


def menu_func(self, context):
    self.layout.operator(AddCropCircle.bl_idname, text="CropCircle", icon='OUTLINER_OB_GREASEPENCIL')

classes = (
    AddCropCircle,
    Reset,
    SurpriseMe    
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_add.append(menu_func)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.VIEW3D_MT_add.remove(menu_func)


if __name__ == "__main__":
    register()
