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
    "version": (0, 0, 5),
    "location": "Side Menu -> Edit",
    "warning": "",
    "wiki_url": "",
    "category": "Object"
}


import bpy,bgl,blf
import math,re

from mathutils import Vector
from bpy.types import Object, Scene, Panel, Operator,PropertyGroup
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
            ["'A' to switch instance/copy","按 A 切换实例/复制"],
            [ "Radius: ",'半径：'],
            ["Number: ",'数量：'],
            ["'R' to copy rotate",'按 R 复制旋转']]
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
    blf.draw(font_id, text[4][index])
    blf.position(font_id, 30, 980, 0)
    blf.draw(font_id, text[1][index])

    # parameter
    blf.size(font_id, 12, 175)
    blf.position(font_id, 30, 100, 0)
    blf.draw(font_id,text[2][index] + str(round(obj.RA.rad,2)))
    blf.position(font_id, 30, 130, 0)
    blf.draw(font_id,text[3][index] + str(obj.RA.num))


def fix(obj):
    obj.RA.rad =2
    obj.RA.num = 8


def clear_meshes():
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

def make_mesh(source):
    new = source.copy()
    new.name = source.name
    new.data = new.data.copy()
    bpy.context.collection.objects.link(new)
    bpy.data.objects.remove(bpy.data.objects[source.name], do_unlink=True)
    return new


def remove_objects(obj):
    for o in bpy.context.scene.objects:
        if o.name.startswith(f"RA_") or o.name.startswith(f"ra_") :
            ret = re.match(".*[0-9]\.*[0-9]\.*[0-9]$", o.name)
            if ret:
                try:bpy.data.objects.remove(o, do_unlink=True)
                except:pass
            try:bpy.data.objects.remove(o, do_unlink=True)
            except:pass

def get_children(myObject):
    children = []
    for ob in bpy.data.objects:
        if ob.parent == myObject:
            children.append(ob)

    return children


def get_center_obj(obj):
    try:
        CTobject = bpy.context.scene.objects[obj.RA.center]
        return CTobject
    except Exception:
        return None


def add_circle(context,obj):
    bpy.ops.mesh.primitive_circle_add(
        vertices=obj.RA.num, radius=obj.RA.rad, enter_editmode=False, align='WORLD')
    Circlename = context.object.name
    circle = bpy.data.objects[Circlename]
    circle.name = 'RA_' + f'{obj.name}'
    return circle


def add_cage(obj):
    if obj.type == "MESH":
        mx = obj.matrix_world
        minz = min((mx @ v.co)[2] for v in obj.data.vertices)
        maxz = max((mx @ v.co)[2] for v in obj.data.vertices)
        d = maxz - minz
    else:
        d = 0
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=obj.RA.rad, depth =d ,enter_editmode=False, align='WORLD')
    cage = bpy.context.object
    cage.display_type = 'BOUNDS'
    cage.name = 'RA_' + f'{obj.name}'
    return cage


def use_circle(obj,parent):
    ic_angle = math.pi * 2 * obj.RA.angle / obj.RA.num
    # reset active
    for i in range(obj.RA.num):
        loc_x = obj.RA.rad * math.sin(i * ic_angle)
        loc_y = obj.RA.rad * math.cos(i * ic_angle)
        #copy or instance

        new = obj.copy()
        bpy.context.collection.objects.link(new)

        if obj.RA.use_instance == "INSTANCE":
            new.data = obj.data

        # loc and rotate
        new.name = "ra_" + obj.name
        new.location[0] = loc_x
        new.location[1] = loc_y

        new.RA.enable = False
        new.hide_select = True

        new.parent = parent

        if obj.RA.apply_rotate:
            new.rotation_euler[2] = ic_angle * -i


def CreatArray(context):
    obj = context.object
    obj.RA.enable = True

    # clean data
    remove_objects(obj)
    clear_meshes()

    cage = add_cage(obj)

    use_circle(obj,cage)

    center = get_center_obj(obj)

    if center:
        cage.location = center.location
    else:
        cage.location = obj.location

    # reset active
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    cage.select_set(True)
    obj.select_set(True)
    obj.hide_select = False


class OBJECT_OT_CreatRA(Operator):
    bl_idname = "object.add_ring_array"
    bl_label = "Add Ring Array"
    bl_options = {'REGISTER', 'GRAB_CURSOR', 'BLOCKING', 'UNDO'} # GRAB_CURSOR + BLOCKING enables wrap-around mouse feature.

    number: IntProperty()
    radius: FloatProperty()
    angle : FloatProperty()

    @classmethod
    def poll(self,context):
        return context.object is not None

    def update(self, context):
        obj = context.object
        if obj.RA.enable:
            CreatArray(context)

    def modal(self, context, event):
        obj = context.object
        CreatArray(context)
        # allow navigation
        if event.type in {'MIDDLEMOUSE',}:
            return {'PASS_THROUGH'}
        # number
        elif event.type == "WHEELUPMOUSE":
            obj.RA.num += 1
            CreatArray(context)
        elif event.type == "WHEELDOWNMOUSE":
            obj.RA.num -= 1
            CreatArray(context)
        #radius
        elif event.type == 'MOUSEMOVE':
            self.mouseDX = self.mouseDX - event.mouse_x
            self.mouseDY = self.mouseDY - event.mouse_y
            multiplier = 0.005 if event.shift else 0.02
            # multi offset
            offset = self.mouseDX
            obj.RA.rad -=  offset * multiplier
            # reset
            self.mouseDX = event.mouse_x
            self.mouseDY = event.mouse_y
        # confirm / cancel
        elif event.type == 'LEFTMOUSE':
            # clean draw
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            obj.RA.num = self.number
            obj.RA.rad = self.radius
            obj.RA.angle = self.angle
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        elif event.type == 'A' and event.value == 'PRESS':
            obj.RA.use_instance = "INSTANCE" if obj.RA.use_instance == "COPY" else "COPY"


        elif event.type == 'R' and event.value == 'PRESS':
            obj.RA.apply_rotate = False if obj.RA.apply_rotate == True else True



        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        obj = context.object
        self.number = obj.RA.num
        self.radius = obj.RA.rad
        self.angle = obj.RA.angle
        self.mouseDX = event.mouse_x
        self.mouseDY = event.mouse_y
        #draw
        if context.area.type == 'VIEW_3D':
            args = (obj, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


class OBJECT_OT_ApplyRA(Operator):
    bl_idname = "object.apply_ring_array"
    bl_label = "Rename"
    bl_options = {'REGISTER', 'UNDO'}

    newname:StringProperty(
        name="Rename",
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_x = 0.5
        row.prop(self, 'newname', text='')

    def execute(self, context):
        obj = context.object
        for o in bpy.data.objects:
            if o.name.startswith(f"RA_{obj.name}"):
                o.name = self.newname
            elif o.name.startswith(f"ra_{obj.name}"):
                o.name = self.newname + obj.name
            o.hide_select = False
        obj.RA.enable = False
        return {'FINISHED'}

    def invoke(self, context, event):
        self.newname = "Give me a name"
        return context.window_manager.invoke_props_popup(self, event)


class OBJECT_OT_DeleteRA(Operator):
    bl_idname = "object.del_ring_array"
    bl_label = "Delete"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        obj.RA.enable = False
        try:
            for o in bpy.data.objects:
                if o.name.startswith(f"RA_{obj.name}"):
                    children = get_children(o)
                    for child in children:
                        bpy.data.objects.remove(child)

                    bpy.data.objects.remove(o)
        except:
            pass
        return {'FINISHED'}


class RA_PT_Panel(Panel):
    bl_label = "Ring Array"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"

    def draw(self, context):
        layout = self.layout.box()
        obj = context.object

        if context.preferences.addons[__name__].preferences.debug:
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

                col1.prop(obj.RA, "num",text = "Count")
                col1.prop(obj.RA, "rad",text = "Radius")
                col1.prop(obj.RA, "angle",text = "Radians",slider = True)

                col = layout.column()
                col.scale_y = 1.15
                row = col.row(align=True)
                row.operator('object.apply_ring_array',text = 'Apply')
                row.operator('object.del_ring_array')
                col.operator('object.add_ring_array', text='Adjust RA')

            elif context.object.name.startswith("RA_") or context.object.name.startswith("ra_"):
                col.label(text='Select a right object')
            else:
                col.operator('object.add_ring_array', text='Creat RA')

#
# ___  ____ ____ ____
# |__] |__/ |___ |___
# |    |  \ |___ |
#
#

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
# ____ ____ ____ _ ____ ___ ____ ____
# |__/ |___ | __ | [__   |  |___ |__/
# |  \ |___ |__] | ___]  |  |___ |  \
#
#

class RA_Props(bpy.types.PropertyGroup):
    enable: BoolProperty(
        name="Use RA", default=False,
    )

    apply_rotate:BoolProperty(
        name="Rotate", default=True,
        update=OBJECT_OT_CreatRA.update
    )

    center : StringProperty(
        name="Center", default='',
        update=OBJECT_OT_CreatRA.update
    )

    num :IntProperty(
        name='Count', default=8, min=2, soft_max=24,
        update=OBJECT_OT_CreatRA.update
    )

    rad : FloatProperty(
        name='Radius', default=2,
        min=0, soft_max=12,
        update=OBJECT_OT_CreatRA.update,
        precision=2,
    )

    angle: FloatProperty(
        name='Angle', default=1,
        min = 0 ,max = 1,
        update=OBJECT_OT_CreatRA.update,
    )

    use_instance: EnumProperty(
        items=[('INSTANCE', 'Instancing', ''), ('COPY', 'Copy', '')],
        default='INSTANCE',
        update = OBJECT_OT_CreatRA.update
    )


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
