import bpy
import math, re

from mathutils import Vector
from bpy.types import Panel, AddonPreferences
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

            if context.object.RA.enable:
                row = col.row(align=False)
                row.prop(obj.RA, 'use_instance', expand=True)

                col1 = layout.box().column()
                row = col1.row(align=False)
                row.prop_search(obj.RA, "center", context.scene, "objects", text="")
                row.scale_x = 1.25
                row.prop(obj.RA, "apply_rotate", text='', icon="ORIENTATION_GIMBAL")

                row = col1.row(align=True)
                row.prop(obj.RA, "num", text="Count")
                row.prop(obj.RA, "layer", text="Layer")

                row = col1.row(align=True)
                row.prop(obj.RA, "rad", text="Radius", slider=True)
                row.prop(obj.RA, "angle", text="Radians", slider=True)

                row = col1.row(align=True)
                row.prop(obj.RA, "offset_rad", text="Offset Y", slider=True)
                row.prop(obj.RA, "offset_angle", text="Offset X", slider=True)

                col = layout.column()
                col.scale_y = 1.15
                row = col.row(align=True)
                row.operator('object.apply_ring_array', text='Apply')
                row.operator('object.del_ring_array')
                col.operator('object.add_ring_array', text='Adjust RA')

            else:
                col.operator('object.add_ring_array', text='Creat RA')


panels = (
    RA_PT_Panel,
)


def update_categort(self, context):
    message = "Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


class RA_Preferences(AddonPreferences):
    bl_idname = __package__

    category: StringProperty(
        name="Tab Category",
        description="Choose a name for the category of the panel",
        default="Edit",
        update=update_categort
    )

    debug: BoolProperty(
        name='Debug', default=False
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.separator()
        row.label(text='Tips: 如果没有中心物体, 则以自己为中心' if CN_ON(context)
        else "Tips: If no center object, RingArray active object itself")

        row.separator()
        row = layout.row(align=True)

        row.separator()
        row.prop(self, "category", text="", icon="ALIGN_JUSTIFY")
        row.label(text="")
        row.separator()
        row.prop(self, 'debug')


classes = (
    RA_PT_Panel, RA_Preferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
