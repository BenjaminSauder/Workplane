import bpy

import workplane.operator      
import workplane.draw

class VIEW3D_PT_WORKINGPLANE(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Work Plane'    
    bl_label = "Working Plane"

    def draw(self, context):
        layout = self.layout       
        scn = bpy.context.scene    

        #this is a little hacky, i dont know where to properly autostart this..
        #in the UI the restricted_context seems to be not an issue        
        # workplane.draw.setup()

        col = layout.column(align=True)        
        col.operator("transform.workplane_set", text="Set workplane")
        #col.operator("transform.workplane_disable", text="Disable workplane")
                
        col = layout.column(align=True)      
        row = col.row(align=True)
        row.prop_enum(context.scene.workplane, "preview_mode", 'FULL')
        row.prop_enum(context.scene.workplane, "preview_mode", 'SIMPLE')
        col.enabled = workplane.operator.working_in_workplane(context) 
        
        col = layout.column(align=True) 
        col.prop(context.scene.workplane, "active", toggle=False, text="Use Workplane") 
        #col.enabled = workplane.operator.has_workplane(context) 

        col = layout.column(align=True) 
        col.prop(context.scene.workplane, "visible", toggle=False, text="Display Workplane") 
        col.enabled = workplane.operator.working_in_workplane(context) 

        col = layout.column(align=True)        
        col.operator("transform.workplane_translate", text="Translate")
        col.operator("transform.workplane_rotate", text="Rotate")
        col.operator("transform.workplane_scale", text="Scale") 
        col.operator("transform.workplane_extrude", text="Extrude")

# class WorkplanePanel():
    
#     def __init__(self):
#         self.init = False

#     def draw(self, context):
#         #this is a little hacky, i dont know where to properly autostart this..
#         #in the UI the restricted_context seems to be not an issue        
#         workplane.draw.setup()

#         layout = self.layout            

#         col = layout.column(align=True)        
#         col.operator("transform.workplane_set", text="Set workplane")
#         #col.operator("transform.workplane_disable", text="Disable workplane")
                
#         col = layout.column(align=True)      
#         row = col.row(align=True)
#         row.prop_enum(context.scene.workplane, "preview_mode", 'FULL')
#         row.prop_enum(context.scene.workplane, "preview_mode", 'SIMPLE')
#         col.enabled = workplane.operator.working_in_workplane(context) 
        
#         col = layout.column(align=True) 
#         col.prop(context.scene.workplane, "active", toggle=False, text="Use Workplane") 
#         col.enabled = workplane.operator.has_workplane(context) 

#         col = layout.column(align=True) 
#         col.prop(context.scene.workplane, "visible", toggle=False, text="Display Workplane") 
#         col.enabled = workplane.operator.working_in_workplane(context) 

#         col = layout.column(align=True)        
#         col.operator("transform.workplane_translate", text="Translate")
#         col.operator("transform.workplane_rotate", text="Rotate")
#         col.operator("transform.workplane_scale", text="Scale") 
#         col.operator("transform.workplane_extrude", text="Extrude")

              
              
# class VIEW3D_PT_WorkplanePanelTransform(WorkplanePanel, bpy.types.Panel):
#     """Workplane Tools Panel"""
#     bl_label = "Workplane "
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = "Tools"
#     bl_context = "objectmode"
    
        
# class VIEW3D_PT_WorkplanePanelMeshEdit(WorkplanePanel, bpy.types.Panel):
#     """Workplane Tools Panel"""
#     bl_label = "Workplane "
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = "Tools"
#     bl_context = "mesh_edit"    
#     bl_label = "Workplane"
