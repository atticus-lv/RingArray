import bpy,blf,bgl
import math,re

from mathutils import Vector
from bpy.types import Object, Scene, Panel, Operator,PropertyGroup
from bpy.props import *


def CN_ON(context):
    if context.preferences.view.use_translate_interface == True:
        return bpy.app.translations.locale == 'zh_CN'


def draw_callback_px(obj, context):
    text = [["Wheel scroll to add count, Move mouse to add rad (shift to slow speed)","滑动滚轮增加数量或，移动鼠标增加半径（按shift微调）"],
            ["'A' to switch instance/copy,'R' to copy rotate","按 A 切换实例/复制,按 R 复制旋转"],
            [ "Radius: ",'半径：'],
            ["Number: ",'数量：'],
            ["ctrl wheel scroll to add layer，ctrl move mouse to offset x,shift move mouse to offset y",'ctrl 滚轮增加层，ctrl 移动鼠标偏移x,shift 移动鼠标偏移y']]
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


def set_init(self,context):
    obj = context.object
    if self.enable == False:
        bpy.ops.object.del_ring_array()
    obj.RA.num = self.number
    obj.RA.rad = self.radius
    obj.RA.angle = self.angle
    obj.RA.layer = self.layer
    obj.RA.offset_angle = self.offset_angle
    obj.RA.offset_rad = self.offset_rad


def init(self,context):
    obj = context.object
    self.enable = obj.RA.enable
    self.number = obj.RA.num
    self.radius = obj.RA.rad
    self.angle = obj.RA.angle
    self.layer = obj.RA.layer
    self.offset_angle = obj.RA.offset_angle
    self.offset_rad = obj.RA.offset_rad





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

    layer = obj.RA.layer
    rad = obj.RA.rad
    rad_offset = obj.RA.offset_rad

    if rad_offset < 0:
        rad_total = rad*layer
    else:
        rad_total = rad * (layer) - rad_offset * (layer) * rad

    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=rad_total, depth =d ,enter_editmode=False, align='WORLD')
    cage = bpy.context.object
    cage.display_type = 'BOUNDS'
    cage.name = 'RA_' + f'{obj.name}'
    return cage


def use_circle(obj,parent):
    ic_angle = math.pi * 2 * obj.RA.angle / obj.RA.num

    layer = obj.RA.layer
    rad = obj.RA.rad
    rad_offset = obj.RA.offset_rad
    offset = obj.RA.offset_angle

    # reset active
    for iter in range(obj.RA.layer):

        if rad_offset <0:
            rad_total = rad * (layer-iter) - rad_offset*(iter)*rad
            offset_total = offset * (layer - iter)
        else:
            rad_total = - rad * (iter+1) + rad_offset * (iter) * rad
            offset_total = offset * (iter+1)

        for i in range(obj.RA.num):
            loc_x = rad_total * math.sin((i+offset_total) * ic_angle)
            loc_y = rad_total * math.cos((i+offset_total) * ic_angle)
            #copy or instance
            new = obj.copy()
            if obj.RA.use_instance == "INSTANCE":
                new.data = obj.data
            else:
                new.data = obj.data.copy()

            bpy.context.collection.objects.link(new)
            # loc and rotate
            new.name = "ra_"+ obj.name +f"_layer{iter}"+ f"_ob{i}"
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

    cage.location = center.location if center else obj.matrix_world.translation

    # reset active
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    cage.select_set(True)
    obj.select_set(True)
    obj.hide_select = False