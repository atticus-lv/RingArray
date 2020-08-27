# -*- coding =utf-8 -*-
# 灵感来源 卯月的小插件
# url: https://space.bilibili.com/29298335
# 此插件使用实例的方法来实现
# 文字画: http://www.network-science.de/ascii/

bl_info = {
    "name": "Ring Array",
    "author": "Atticus",
    "description": "允许阵列任意物体的插件",
    "blender": (2, 83, 2),
    "version": (0, 0, 6),
    "location": "Side Menu -> Edit",
    "warning": "",
    "wiki_url": "https://github.com/atticus-lv/RingArray",
    "category": "Object"
}


import bpy, bgl, blf
import math, re

from mathutils import Vector
from bpy.types import Object, Scene, Panel, Operator, PropertyGroup
from bpy.props import *

from .Operators import *
from .Functions import *
from .Panel import *


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


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    category: StringProperty(
        name="Tab Category",
        description="Choose a name for the category of the panel",
        default="Edit",
        update=update_categort
        )

    debug:BoolProperty(
        name = 'Debug',default = False
        )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.separator()
        row.label(text='Tips: 如果没有中心物体, 则以自己为中心'if CN_ON(context) else "Tips: If no center object, RingArray active object itself")
        row.separator()
        row = layout.row(align=True)

        row.separator()
        row.prop(self, "category", text="", icon="ALIGN_JUSTIFY")
        row.label(text="")
        row.separator()
        row.prop(self,'debug')


classes = (
    RA_PT_Panel, OBJECT_OT_CreatRA, OBJECT_OT_ApplyRA, OBJECT_OT_DeleteRA, Preferences, RA_Props
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.RA = bpy.props.PointerProperty(type=RA_Props)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
