import bpy 
import math

# 修复网格残余
def clear_meshes():
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


class CS_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.centersym"
    bl_label = "centerSym"
    bl_description = "选中中心物体后创建环绕阵列，否则默认中心为世界中心"
    def execute(self,context):
         createCS(context)
         return {'FINISHED'}


        
class CS_OT_Update(bpy.types.Operator):
    bl_idname = "view3d.update"
    bl_label = "Update"
    bl_description = "更新"
    
    def execute(self, context):
        obj = bpy.context.object
        if obj.csObj:
            createCS(context)   

class CS_OT_Delete(bpy.types.Operator):
    bl_idname = "view3d.delete"
    bl_label = "delete"
    bl_description = "删除"
    def execute(self, context):
        obj = bpy.context.object
        objName = obj.name
        obj.csObj = False
        for ob in bpy.context.visible_objects:
            if ob.name.startswith("cs_") and ob.name.endswith("_"+ objName):
                bpy.data.objects.remove(ob)
                
        return {'FINISHED'}

class CS_OT_Apply(bpy.types.Operator):
    bl_idname = "view3d.apply"
    bl_label = "apply"
    bl_description = "塌陷"
    def execute(self, context):
        obj = bpy.context.object
        obj.csObj = False
        for ob in bpy.context.visible_objects:
            if ob.name.startswith("cs_") and ob.name.endswith("_"+ obj.orgName):
                ob.hide_select = False
                ob.name = "cs_" + obj.name
        return {'FINISHED'}

def createCS(context):
    #创建集合
        if "CS_objects" not in bpy.data.collections:
            csCol = bpy.data.collections.new("CS_objects")
            bpy.context.scene.collection.children.link(csCol)
        obj = bpy.context.object  
        distance = obj.objRad
        angle = obj.objAgl
        angle = math.pi * 2 * angle / obj.objNum
        objlist = []
        
        #设置重命名前缀
        objName = obj.name

        #获取当前物体所在集合名称
        currentCol = obj.users_collection[0].name

        #删除前一次物体
        for ob in bpy.context.visible_objects:
            if ob.name.startswith("cs_") and ob.name.endswith("_"+ obj.orgName):
                bpy.data.objects.remove(ob)
        #修复网格残余
        clear_meshes()

        applyObj = bpy.ops.object.duplicate(linked=0,mode='TRANSLATION')
        applyObj = bpy.context.object
        bpy.ops.object.convert(target='MESH')

        #复制建物体调整位置      
        for i in range (obj.objNum):  
            objX = distance * math.sin(i * angle)
            objY = distance * math.cos(i * angle)
            newObj = bpy.ops.object.duplicate(linked=0,mode='TRANSLATION')
            bpy.context.object.location[0] = objX
            bpy.context.object.location[1] = objY
            bpy.context.object.location[2] = 0
            bpy.context.object.rotation_euler[2] = angle *-i

            if not obj.centerObj == "":
                bpy.context.object.parent = bpy.data.objects[obj.centerObj]
            
            
            objlist.append(bpy.context.object)
            bpy.context.object.name = "cs_" + str(i) + "_" + objName

        for i in objlist:
            #将复制物体移除当前物体所在集合并移入特殊集合
            if currentCol == "Master Collection":
                bpy.context.scene.collection.objects.unlink(i)
                bpy.data.collections['CS_objects'].objects.link(i)

            else:               
                bpy.data.collections[currentCol].objects.unlink(i)
                bpy.data.collections['CS_objects'].objects.link(i)
           

            i.hide_select = True
            i.csObj = False

        
        bpy.data.objects.remove(applyObj)
        obj.csObj = True
        
        #储存修改后的物体名称
        obj.orgName = objName

        bpy.data.objects[obj.name].select_set(True)
        bpy.context.view_layer.objects.active = obj
        return {'FINISHED'}
  

    
           
     

    

