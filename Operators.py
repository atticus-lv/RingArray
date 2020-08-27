import bpy,bgl,blf
import math,re

from mathutils import Vector
from bpy.types import Object, Scene, Panel, Operator,PropertyGroup
from bpy.props import *
from .Functions import *


class OBJECT_OT_CreatRA(Operator):
    bl_idname = "object.add_ring_array"
    bl_label = "Add Ring Array"
    bl_options = {'REGISTER', 'GRAB_CURSOR', 'BLOCKING', 'UNDO'} # GRAB_CURSOR + BLOCKING enables wrap-around mouse feature.

    number: IntProperty()
    radius: FloatProperty()
    angle : FloatProperty()
    enable: BoolProperty()

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
            if self.enable == False:
                bpy.ops.object.del_ring_array()
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
        self.enable = obj.RA.enable
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
                o.name ="sub_"+ self.newname
            o.hide_select = False
        obj.RA.enable = False
        return {'FINISHED'}

    def invoke(self, context, event):
        self.newname = "Fill your new name"
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
        except:pass

        return {'FINISHED'}


class RA_Props(PropertyGroup):
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