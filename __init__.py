# -*- coding =utf-8 -*-
# 灵感来源 卯月的小插件
# url: https://space.bilibili.com/29298335
# 此插件使用实例的方法来实现
# 文字画: http://www.network-science.de/ascii/

bl_info = {
    "name": "Ring Array",
    "author": "Atticus",
    "description": "",
    "blender": (2, 83, 2),
    "version": (0, 0, 3),
    "location": "Side Menu -> Edit",
    "warning": "",
    "wiki_url": "",
    "category": "Object"
}

import bpy
import bgl
import blf

from bpy.types import Object, Scene, Panel, Operator
from bpy.props import *


#
# ____ _    ____ ____ ____
# |    |    |__| [__  [__
# |___ |___ |  | ___] ___]
#
#


def CN_ON(context):
    if context.preferences.view.use_translate_interface == True:
        return bpy.app.translations.locale == 'zh_CN'


def draw_callback_px(obj, context):
    text = [["Wheel Scroll OR Move mouse (shift to slow speed)","滑动滚轮或者移动鼠标（按shift微调）"],
            ["'A' to apply instance, Ctrl 'A' to apply mesh","按 A 应用实例，Ctrl A 应用网格"],
            [ "Radius: ",'半径：'],
            ["Number: ",'数量：'],]
    # check CN
    if CN_ON(context):
        index = 1
    else:
        index = 0
    # tips
    font_id = 0
    blf.size(font_id, 12, 100)
    blf.position(font_id, 30,1020, 0)
    blf.draw(font_id,text[0][index] )
    blf.position(font_id, 30, 1000, 0)
    blf.draw(font_id,text[1][index] )
    # parameter
    blf.size(font_id, 12, 175)
    blf.position(font_id, 30, 100, 0)
    blf.draw(font_id,text[2][index] + str(round(obj.Rad,2)))
    blf.position(font_id, 30, 130, 0)
    blf.draw(font_id,text[3][index] + str(obj.V_num))


def clear_meshes():
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


def remove_objects(context):
    for o in context.scene.objects:
        if o.name.startswith("RA_"):
            objs = bpy.data.objects
            objs.remove(objs[o.name], do_unlink=True)


def get_children(myObject):
    children = []
    for ob in bpy.data.objects:
        if ob.parent == myObject:
            children.append(ob)

    return children


def get_center_obj(context):
    try:
        CTobject = context.scene.objects[context.object.Ct]
    except Exception:
        CTobject = ''
    return CTobject


def add_circle(context,obj):
    bpy.ops.mesh.primitive_circle_add(
        vertices=obj.V_num, radius=obj.Rad, enter_editmode=False, align='WORLD')
    Cieclename = context.object.name
    circle = bpy.data.objects[Cieclename]
    circle.name = 'RA_' + f'{obj.name}'
    return circle


def set_instance(circle,instance):
    circle.instance_type = 'VERTS'
    circle.show_instancer_for_viewport = True
    circle.show_instancer_for_render = True
    circle.use_instance_vertices_rotation = instance.Copy_rotate
    return circle


def make_mesh(source,self):
    new = source.copy()
    new.name =self.post_name + source.name
    new.data = new.data.copy()
    bpy.context.collection.objects.link(new)
    bpy.data.objects.remove(bpy.data.objects[source.name], do_unlink=True)


def creat_RA(context):
    obj = context.object
    bpy.ops.object.select_all(action='DESELECT')

    remove_objects(context)
    clear_meshes()

    circle = add_circle(context,obj)

    if get_center_obj(context) != '':
        circle.location = CTobject.location
        obj.parent = circle
        obj.location = (0,0,0)
    else:
        circle.location = obj.location
        obj.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

    set_instance(circle,obj)
    # restore active
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = obj
    obj.select_set(True)
    # set RA
    obj.RAobj = True


def get_3dview_size(context):
    for area in context.screen.areas:
        if area.type=='VIEW_3D':
            WIDTH=area.width
            HEIGHT=area.height
            return  WIDTH,HEIGHT


class CreatRA(Operator):
    bl_idname = "object.add_ring_array"
    bl_label = "Add Ring Array"
    bl_options = {'REGISTER', 'GRAB_CURSOR', 'BLOCKING'} # GRAB_CURSOR + BLOCKING enables wrap-around mouse feature.

    number: bpy.props.IntProperty()
    radius: bpy.props.FloatProperty()

    def update(self, context):
        obj = context.object
        if obj.RAobj:
            creat_RA(context)

    def modal(self, context, event):
        obj = context.object
        self.execute(context)
        # allow navigation
        if event.type in {'MIDDLEMOUSE',}:
            return {'PASS_THROUGH'}
        # number
        elif event.type == "WHEELUPMOUSE":
            obj.V_num += 1
            self.execute(context)
        elif event.type == "WHEELDOWNMOUSE":
            obj.V_num -= 1
            self.execute(context)
        #radius
        elif event.type == 'MOUSEMOVE':
            self.mouseDX = self.mouseDX - event.mouse_x
            self.mouseDY = self.mouseDY - event.mouse_y
            multiplier = 0.005 if event.shift else 0.02
            # multi offset
            offset = self.mouseDX
            obj.Rad -=  offset * multiplier
            # reset
            self.mouseDX = event.mouse_x
            self.mouseDY = event.mouse_y
        # confirem/cancel
        elif event.type == 'LEFTMOUSE':
            # clean draw
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            obj.V_num = self.number
            obj.Rad = self.radius
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'A' and event.value == 'PRESS':
            if event.ctrl:
                bpy.ops.object.apply_ring_array(apply_mesh = True)
            else:
                bpy.ops.object.apply_ring_array(apply_mesh=False)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def execute(self, context):
        creat_RA(context)

    def invoke(self, context, event):
        obj = context.object
        self.number = obj.V_num
        self.mouseDX = event.mouse_x
        self.mouseDY = event.mouse_y
        self.radius = obj.Rad
        #draw
        if context.area.type == 'VIEW_3D':
            args = (obj, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


class ApplyRA(Operator):
    bl_idname = "object.apply_ring_array"
    bl_label = "Apply"
    bl_options = {'REGISTER', 'UNDO'}

    post_name = StringProperty(name="Suffix", default='new_', )
    apply_mesh = BoolProperty(name= 'Apply Instance Mesh ',default = False)

    def execute(self, context):
        obj = context.object
        obj_name = obj.name
        obj.RAobj = False

        for o in context.scene.objects:
            if o.name.startswith("RA_") and o.name.endswith("_" + obj.name):
                # apply instance
                context.view_layer.objects.active = o
                o.select_set(True)
                bpy.ops.object.duplicates_make_real(use_base_parent=True)

                children = get_children(o)
                for child in children:
                    if self.apply_mesh:
                        # apply mesh
                        make_mesh(child,self)
                        obj = bpy.data.objects[self.post_name + obj_name]
                    else:
                        child.name = self.post_name + obj_name
        # restore
        obj.name = obj_name
        obj.Copy_rotate = True
        obj.Ct = ''
        obj.V_num = 8
        obj.Rad = 2
        obj.Copy_apply = False
        #clear parent
        obj.parent = None

        return {'FINISHED'}

    def invoke(self, context, event):
        obj = context.object
        self.post_name = 'new_'
        self.apply_mesh = obj.Copy_apply
        return self.execute(context)


class DeleteRA(Operator):
    bl_idname = "object.del_ring_array"
    bl_label = "Delete"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        obj.RAobj = False
        for o in context.visible_objects:
            if o.name.startswith("RA_") and o.name.endswith("_" + obj.name):
                bpy.data.objects.remove(o)

        return {'FINISHED'}


class RA_Panel(Panel):
    bl_label = "Ring Array"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if context.preferences.addons[__name__].preferences.debug:
            layout.operator('script.reload')
        if not obj:
            layout.label(text='Select An Object')
        else:
            col = layout.column()
            col.scale_y = 1.5
            row = col.row(align=False)
            row.prop_search(obj, "Ct", context.scene, "objects")
            row.scale_x = 1.25
            row.prop(obj, "Copy_rotate", text='', icon="ORIENTATION_GIMBAL")
            if context.object.RAobj:
                row = col.row(align=True)
                row.prop(obj, "V_num")
                row.prop(obj, "Rad")

                col.operator('object.add_ring_array',text='Adjust RA')

                row = col.row(align=True)
                row.operator('object.apply_ring_array')
                sub = row.row(align=True)
                sub.prop(obj, 'Copy_apply', text='', icon='MESH_DATA')
                row.separator()
                row.operator('object.del_ring_array')

            else:
                if len(context.object.data.polygons) == 0:
                    try:
                        col.label(text='active object have no faces')
                    except AttributeError:
                        pass
                else:
                    row = col.row(align=True)
                    row.operator("object.add_ring_array")


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
        if CN_ON(context):
            row.label(text='Tips: 如果没有中心物体, 则以自己为中心')
        else:
            row.label(text="Tips: If no center object, RingArray active object itself")
        row.separator()
        row = layout.row(align=True)

        row.separator()
        row.prop(self, "category", text="", icon="ALIGN_JUSTIFY")
        row.label(text="")
        row.separator()
        row.prop(self,'debug')


#
# ___  ____ ____ ___  ____
# |__] |__/ |  | |__] [__
# |    |  \ |__| |    ___]
#
#

def props():
    Object.RAobj = BoolProperty(
        name="Use RA", default=False,
    )

    Object.Copy_rotate = BoolProperty(
        name="Rotate", default=True,
        update=CreatRA.update
    )

    Object.Ct = StringProperty(
        name="Center", default='',
        update=CreatRA.update
    )

    Object.V_num = IntProperty(
        name='Count', default=8, min=3, soft_max=24,
        update=CreatRA.update
    )

    Object.Rad = FloatProperty(
        name='Radius', default=2,
        min=0, soft_max=12,
        update=CreatRA.update,
        precision = 2,
    )

    Object.Copy_apply = BoolProperty(
        name="Mesh", default=False
    )


#
# ____ ____ ____ _ ____ ___ ____ ____
# |__/ |___ | __ | [__   |  |___ |__/
# |  \ |___ |__] | ___]  |  |___ |  \
#
#

classes = (
    RA_Panel, CreatRA, DeleteRA, ApplyRA, Preferences,
)


def register():
    props()
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
