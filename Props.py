import bpy
from bpy.types import PropertyGroup
from bpy.props import *
from .Operators import OBJECT_OT_CreatRA


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