import bpy

      
import workplane.draw

class WorkplanePanel():
    
    def __init__(self):
        self.init = False

    def draw(self, context):
        #this is a little hacky, i dont know where to properly autostart this..
        #in the UI the restricted_context seems to be not an issue        
        workplane.draw.setup()

        layout = self.layout            

        col = layout.column(align=True)        
        col.operator("workplane.set_workplane", text="Set workplane")
        layout.prop(context.scene, "workplane_visible", toggle=False, text="Display Workplane") 
           
        col = layout.column(align=True)        
        col.operator("workplane.translate", text="Translate")
        col.operator("workplane.rotate", text="Rotate")
        col.operator("workplane.scale", text="Scale") 
              
              
class WorkplanePanelTransform(WorkplanePanel, bpy.types.Panel):
    """Workplane Tools Panel"""
    bl_label = "Workplane "
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
