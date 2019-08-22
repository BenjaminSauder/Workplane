import bpy
from mathutils import Matrix, Vector

from . import main

work_plane = "WorkPlane"

DRAW_MODE = [
    ("SIMPLE", "Simple", "", 1),
    ("FULL", "Full", "", 2)
    ]


class WP_OT_WorkplaneProperties(bpy.types.PropertyGroup):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    matrix : bpy.props.FloatVectorProperty(
            name="matrix",
            size=16,
            subtype="MATRIX")            
                     
    viewmatrix : bpy.props.FloatVectorProperty(
            name="viewmatrix",
            size=16,
            subtype="MATRIX")        

    grid_prefs : bpy.props.BoolVectorProperty(
            name="grid_prefs",
            size=4)

    def active_get(self):
        if "active" in self:        
            return self["active"]
        return False

    def active_set(self, value):
        from . import update

        if value:
            update.enable_workplane()
        else:
            update.disable_workplane()

        self["active"] = value

    
    active : bpy.props.BoolProperty(default=True, get=active_get, set=active_set)                     
    visible : bpy.props.BoolProperty(default=True)    
    user_transform_orientation : bpy.props.StringProperty(default="GLOBAL")  
    preview_mode : bpy.props.EnumProperty(items=DRAW_MODE)
   
        
def set_matrix(matrix):
    bpy.context.scene.workplane.matrix = flatten(matrix)     
     
def get_matrix():
    return bpy.context.scene.workplane.matrix                      

     
def flatten(mat):
    dim = len(mat)
    return [mat[j][i] for i in range(dim) 
                      for j in range(dim)]

def set_visibility(state):
    bpy.context.scene.workplane.visible = state

def get_visibility():
    return bpy.context.scene.workplane.visible

def store_grid_overlay_prefs():   
    bpy.context.scene.workplane.grid_prefs = (
        bpy.context.space_data.overlay.show_floor,  
        bpy.context.space_data.overlay.show_axis_x,
        bpy.context.space_data.overlay.show_axis_y,
        bpy.context.space_data.overlay.show_axis_z
    )

def load_grid_overlay_prefs():
    return (
        bpy.context.scene.workplane.grid_prefs[0],
        bpy.context.scene.workplane.grid_prefs[1],
        bpy.context.scene.workplane.grid_prefs[2],
        bpy.context.scene.workplane.grid_prefs[3]
    )

   
def get_user_transform_orientation():
    return bpy.context.scene.workplane.user_transform_orientation

def set_user_transform_orientation():
    transform_orientation = bpy.context.scene.transform_orientation_slots[0].type

    if transform_orientation != work_plane:
        bpy.context.scene.workplane.user_transform_orientation = transform_orientation

def is_simple_preview():
    return bpy.context.scene.workplane.preview_mode == "SIMPLE"
   
   
   
   
   
   
   