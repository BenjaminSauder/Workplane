import bpy

import workplane.operator      

class WorkplanePanel():
    
    def __init__(self):
        self.init = False

    def draw(self, context):
        layout = self.layout            

        col = layout.column(align=True)        
        col.operator("transform.workplane_set", text="Set workplane")
      
        col = layout.column(align=True)      
        row = col.row(align=True)
        row.prop_enum(context.scene.workplane, "preview_mode", 'FULL')
        row.prop_enum(context.scene.workplane, "preview_mode", 'SIMPLE')
        col.enabled = workplane.operator.working_in_workplane(context) 
        
        col = layout.column(align=True) 
        col.prop(context.scene.workplane, "active", toggle=False, text="Use Workplane") 
        col.enabled = workplane.operator.has_workplane(context) 

        col = layout.column(align=True) 
        col.prop(context.scene.workplane, "visible", toggle=False, text="Display Workplane") 
        col.enabled = workplane.operator.working_in_workplane(context) 

        col = layout.column(align=True)        
        col.operator("transform.workplane_translate", text="Translate")
        col.operator("transform.workplane_rotate", text="Rotate")
        col.operator("transform.workplane_scale", text="Scale") 
        col.operator("transform.workplane_extrude", text="Extrude")


class WorkplanePanelTransform(WorkplanePanel, bpy.types.Panel):
    """Workplane Tools Panel"""
    bl_label = "Workplane"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_context = "objectmode"
    
        
class WorkplanePanelMeshEdit(WorkplanePanel, bpy.types.Panel):
    """Workplane Tools Panel"""
    bl_label = "Workplane "
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_context = "mesh_edit"    
    bl_label = "Workplane"
         
class WorkplanePanelMenu(bpy.types.Menu):
    bl_label = "Workplane"
    bl_idname = "VIEW3D_MT_workplane_menu"     

    def draw(self, context):
        layout = self.layout            

        col = layout.column(align=True)        
        col.operator("transform.workplane_set", text="Set workplane")

        layout.separator() 
        col = layout.column(align=True)      
        #row = col.row(align=True)
        col.prop_enum(context.scene.workplane, "preview_mode", 'FULL')
        col.prop_enum(context.scene.workplane, "preview_mode", 'SIMPLE')
        col.enabled = workplane.operator.working_in_workplane(context) 
        
        col = layout.column(align=True) 
        col.prop(context.scene.workplane, "active", toggle=False, text="Use Workplane") 
        col.enabled = workplane.operator.has_workplane(context) 

        col = layout.column(align=True) 
        col.prop(context.scene.workplane, "visible", toggle=False, text="Display Workplane") 
        col.enabled = workplane.operator.working_in_workplane(context) 

        layout.separator()
        col = layout.column(align=True)        
        col.operator("transform.workplane_translate", text="Translate")
        col.operator("transform.workplane_rotate", text="Rotate")
        col.operator("transform.workplane_scale", text="Scale") 
        col.operator("transform.workplane_extrude", text="Extrude")


              
# draw function for integration in menus
def menu_func(self, context):
    self.layout.separator()
    self.layout.menu("VIEW3D_MT_workplane_menu")