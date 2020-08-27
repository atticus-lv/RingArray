import bpy
import math,re

from mathutils import Vector
from bpy.types import Object, Scene, Panel, Operator,PropertyGroup
from bpy.props import *

class RA_PT_Panel(Panel):
    bl_label = "Ring Array"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"

    def draw(self, context):
        layout = self.layout.box()
        obj = context.object
        if context.preferences.addons[__package__].preferences.debug:
            layout.operator('script.reload')

        if not obj:
            layout.label(text='Select An Object')
        else:
            col = layout.column()
            col.scale_y = 1.15

            if context.object.RA.enable  :
                row = col.row(align=False)
                row.prop(obj.RA, 'use_instance', expand=True)

                col1 = layout.box().column()
                row = col1.row(align=False)
                row.prop_search(obj.RA, "center", context.scene, "objects", text="")
                row.scale_x = 1.25
                row.prop(obj.RA, "apply_rotate", text='', icon="ORIENTATION_GIMBAL")

                row = col1.row(align=True)
                row.prop(obj.RA, "num",text = "Count")
                row.prop(obj.RA, "layer", text="Layer")

                row = col1.row(align=True)
                row.prop(obj.RA, "rad",text = "Radius", slider=True)
                row.prop(obj.RA, "angle", text="Radians", slider=True)


                row = col1.row(align=True)
                row.prop(obj.RA, "offset_rad", text="Offset Y", slider=True)
                row.prop(obj.RA, "offset_angle", text="Offset X", slider=True)

                col = layout.column()
                col.scale_y = 1.15
                row = col.row(align=True)
                row.operator('object.apply_ring_array',text = 'Apply')
                row.operator('object.del_ring_array')
                col.operator('object.add_ring_array', text='Adjust RA')

            else:
                col.operator('object.add_ring_array', text='Creat RA')