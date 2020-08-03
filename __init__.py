# -*- coding =utf-8 -*-
# 灵感来源 卯月的小插件
# https://space.bilibili.com/29298335
# 最后调用实例的方法来实现
# 生成文字画: http://www.network-science.de/ascii/

bl_info = {
    "name": "Ring Array",
    "author": "Atticus",
    "description": "",
    "blender": (2, 83, 2),
    "version": (0, 0, 1),
    "location": "Side Menu",
    "warning": "",
    "wiki_url": "",
    "category": "Object"
}

import bpy
from bpy.types import Object,Scene, Panel, Operator
from bpy.props import *

#
# ____ _    ____ ____ ____
# |    |    |__| [__  [__
# |___ |___ |  | ___] ___]
#
#

class RA_Panel(Panel):
    bl_label = "Ring Array"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        # layout.operator('script.reload')
        if not obj:
            layout.label(text='Select An Object')
        else:
            col = layout.column()
            col.scale_y = 1.5
            col.prop_search(obj, "Ct", context.scene, "objects")
            if context.object.RAobj:
                col.prop(obj, "V_num")
                col.prop(obj, "Rad")
                row = col.row(align = True)
                row.operator('object.apply_ring_array')
                row.operator('object.del_ring_array')

            else:
                if len(context.object.data.polygons) == 0 :
                    try:
                        col.label(text='active object have no faces')
                    except AttributeError:
                        pass
                else:
                    row = col.row(align = True)
                    row.operator("object.add_ring_array")


def creat_RA(context):
    # copy
    obj = context.object
    obj.RAobj = True

    try:
        CTobject = context.scene.objects[obj.Ct]
    except Exception:
        CTobject = ''

    bpy.ops.object.select_all(action='DESELECT')

    for o in context.visible_objects:
        if o.name.startswith("RA_"):
            bpy.data.objects.remove(o)

    # add circle
    bpy.ops.mesh.primitive_circle_add(
        vertices=obj.V_num, radius=obj.Rad, enter_editmode=False, align='WORLD')
    Cieclename = context.object.name
    circle = bpy.data.objects[Cieclename]
    circle.name = 'RA_' + f'{obj.name}'

    # trans circle
    if CTobject != '':
        circle.location = CTobject.location
    else:
        circle.location = obj.location
        obj.location = (0,0,0)

    # parent and set instance
    obj.parent = circle
    circle.instance_type = 'VERTS'
    circle.show_instancer_for_viewport = True
    circle.show_instancer_for_render = True
    circle.use_instance_vertices_rotation = True
    # restore active
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = obj
    obj.select_set(True)

    obj.RAobj = True


class CreatRA(Operator):
    bl_idname = "object.add_ring_array"
    bl_label = "Add Ring Array"
    bl_options = {'REGISTER', 'UNDO'}

    def update(self, context):
        obj = context.object
        if obj.RAobj:
            creat_RA(context)
        return {'FINISHED'}

    def execute(self, context):
        creat_RA(context)
        return {'FINISHED'}


class ApplyRA(Operator):
    bl_idname = "object.apply_ring_array"
    bl_label = "Apply"

    def execute(self, context):
        obj = context.object
        obj.RAobj = False
        for o in context.visible_objects:
            if o.name.startswith("RA_") and o.name.endswith("_"+ obj.name):
                context.view_layer.objects.active = o
                o.select_set(True)
                bpy.ops.object.duplicates_make_real(use_base_parent = True)
                break
        #clear parents
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.parent_clear(type='CLEAR')
        return {'FINISHED'}


class DeleteRA(Operator):
    bl_idname = "object.del_ring_array"
    bl_label = "Delete"

    def execute(self, context):
        obj = context.object
        obj.RAobj = False
        for o in context.visible_objects:
            if o.name.startswith("RA_") and o.name.endswith("_"+ obj.name):
                bpy.data.objects.remove(o)

        return {'FINISHED'}


#
# ___  ____ ____ ____
# |__] |__/ |___ |___
# |    |  \ |___ |
#
#

panels = (
        RA_Panel,
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
    bl_idname = __name__
    category: StringProperty(name="Tab Category",
        description="Choose a name for the category of the panel",
        default="Edit",
        update=update_categort
    )

    def draw(self, context):
        layout = self.layout
        col = layout.box()
        row = col.row(align=True)
        row.prop(self, "category", text="Tab Category")

#
# ___  ____ ____ ___  ____
# |__] |__/ |  | |__] [__
# |    |  \ |__| |    ___]
#
#

Object.RAobj = BoolProperty(name="Use RA", default=False, )
Object.Ct = StringProperty(name="Center", default='', update=CreatRA.update)
Object.V_num = IntProperty(name='Count', default=6, min=3, soft_max=24, update=CreatRA.update)
Object.Rad = FloatProperty(name='Radius', default=1, min=0, soft_max=12, update=CreatRA.update)


#
# ____ ____ ____ _ ____ ___ ____ ____
# |__/ |___ | __ | [__   |  |___ |__/
# |  \ |___ |__] | ___]  |  |___ |  \
#
#

classes = (
    RA_Panel,CreatRA,DeleteRA,ApplyRA,Preferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
