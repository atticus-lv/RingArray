# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "CircleArray",
    "author" : "Utsuki",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 3),
    "location" : "View3D",
    "warning" : "",
    "wiki_url":"https://space.bilibili.com/29298335",
    "category" : "Generic"
}

import bpy


from . centerSym_op import CS_OT_Operator
from . centerSym_op import CS_OT_Update
from . centerSym_op import CS_OT_Delete
from . centerSym_op import CS_OT_Apply
from . centerSym_panel import CS_PT_Panel

classes = (CS_OT_Apply, CS_OT_Update,CS_OT_Operator, CS_OT_Delete, CS_PT_Panel)

bpy.types.Object.orgName = bpy.props.StringProperty(name = "origin name", default = "UtsukiMesh")
bpy.types.Object.csObj = bpy.props.BoolProperty(name = "Center Sym Object", default = False)
bpy.types.Object.objNum = bpy.props.IntProperty(name = "个数", default = 6, min = 1, update=CS_OT_Update.execute)
bpy.types.Object.objAgl = bpy.props.FloatProperty(name = "圆", default = 1, min = 0, max = 1, update = CS_OT_Update.execute)
bpy.types.Object.objRad = bpy.props.FloatProperty(name = "半径", default = 4, min = 0, update=CS_OT_Update.execute)
bpy.types.Object.centerObj = bpy.props.StringProperty(name = "中心", default = "", update=CS_OT_Update.execute)

register, unregister = bpy.utils.register_classes_factory(classes)


