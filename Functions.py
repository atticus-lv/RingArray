import bpy
import math,re

from mathutils import Vector
from bpy.types import Object, Scene, Panel, Operator,PropertyGroup
from bpy.props import *


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
    blf.position(font_id, 30, 160, 0)
    blf.draw(font_id, str(obj.RA.use_instance))


def clear_meshes():
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


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