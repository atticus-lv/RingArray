import bpy



class CS_PT_Panel(bpy.types.Panel):
    bl_idname = "CS_PT_Panel"
    bl_label = "快速环绕阵列"
    bl_category = "卯月的小插件"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.active_object


        if bpy.context.mode == 'OBJECT' and len(context.selected_objects) > 0: 
            row = layout.row()
            layout.prop_search(obj, "centerObj", scene, "objects")

            row = layout.row()
            row.prop(obj, "objAgl")

            row = layout.row()
            row.prop(obj, "objNum")
    
            row = layout.row()
            row.prop(obj, "objRad")        

            row = layout.row()
            if obj.csObj:
                row.operator("view3d.centersym", text="更新")
            else:             
                row.operator("view3d.centersym", text="创建环绕阵列")

            
            if obj.csObj:
                row = layout.row()
                row.operator("view3d.delete", text="删除")
                row.operator("view3d.apply", text="塌陷")
       
            '''row2 = layout.row()
            if obj.csObj:
                row2.label(text = "true")
            else:
                row2.label(text = "false")'''


        else:
            row = layout.row()
            row.label(text = "↖(^ω^)↗三连的人最可爱了")
            




        


