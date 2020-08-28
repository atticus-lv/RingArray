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
    offset_angle:FloatProperty()
    offset_rad:FloatProperty()


    @classmethod
    def poll(self,context):
        return context.object is not None


    def update(self, context):
        obj = bpy.context.object
        if obj.RA.enable:
            CreatArray(context)

    def modal(self, context, event):
        obj = bpy.context.object
        CreatArray(context)
        # allow navigation
        if event.type in {'MIDDLEMOUSE',}:
            return {'PASS_THROUGH'}
        # number
        elif event.type == "WHEELUPMOUSE":
            if not event.ctrl:
                obj.RA.num += 1
            else:
                obj.RA.layer += 1
        elif event.type == "WHEELDOWNMOUSE":
            if not event.ctrl:
                obj.RA.num -= 1
            else:
                obj.RA.layer -= 1

        #radius
        elif event.type == 'MOUSEMOVE':
            self.mouseDX = self.mouseDX - event.mouse_x
            self.mouseDY = self.mouseDY - event.mouse_y

            # multi offset
            offsetx = self.mouseDX
            offsety = self.mouseDY

            if event.ctrl:
                multiplier = 0.0005 if event.shift else 0.002
                obj.RA.offset_angle -= offsetx * multiplier
            elif event.alt:
                multiplier = 0.0005 if event.shift else 0.002
                obj.RA.offset_rad -=  offsetx * multiplier

            else:
                multiplier = 0.005 if event.shift else 0.02
                obj.RA.rad -= offsetx * multiplier

            # reset
            self.mouseDX = event.mouse_x
            self.mouseDY = event.mouse_y


        # confirm / cancel
        elif event.type == 'LEFTMOUSE':
            # clean draw
            for ob in bpy.data.objects:
                if ob.name.startswith(f"RA_{context.object.name}"):
                    ob.select_set(False)

            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            set_init(self,context)

            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        # sitch
        elif event.type == 'A' and event.value == 'PRESS':
            obj.RA.use_instance = "INSTANCE" if obj.RA.use_instance == "COPY" else "COPY"

        elif event.type == 'R' and event.value == 'PRESS':
            obj.RA.apply_rotate = False if obj.RA.apply_rotate == True else True

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        obj = bpy.context.object
        init(self,context)
        # mouse
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
                children = get_children(o)
                for child in children:
                    child.name =child.name[3+len(obj.name):]
                    child.name =  self.newname + "_"+ child.name
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

    layer: IntProperty(
        name='Layer', default=1, min=1, soft_max=10,
        update=OBJECT_OT_CreatRA.update
    )

    rad : FloatProperty(
        name='Radius', default=2,
        min=0, soft_max=12,
        update=OBJECT_OT_CreatRA.update,
        precision=2,
    )

    offset_rad: FloatProperty(
        name='Offset', default=0,
        min=-1, max=1,
        update=OBJECT_OT_CreatRA.update,
    )

    angle: FloatProperty(
        name='Angle', default=1,
        min = -1 ,max = 1,
        update=OBJECT_OT_CreatRA.update,
    )

    offset_angle: FloatProperty(
        name='Offset', default=0.5,
        min=0, max=1,
        update=OBJECT_OT_CreatRA.update,
    )

    use_instance: EnumProperty(
        items=[('INSTANCE', 'Instancing', ''), ('COPY', 'Copy', '')],
        default='INSTANCE',
        update = OBJECT_OT_CreatRA.update
    )