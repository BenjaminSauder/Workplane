import bpy
from mathutils import Matrix, Vector

work_plane = "WorkPlane"

class WorkplaneProperties(bpy.types.PropertyGroup):
    workplane_matrix = bpy.props.FloatVectorProperty(
            name="workplane_matrix",
            size=16,
            subtype="MATRIX")
                      
    workplane_visible = bpy.props.BoolProperty(name="workplane_visible", default=False)

        
def set_matrix(matrix):
    bpy.context.scene.workplane_matrix = flatten(matrix)
     
     
def get_matrix():
    return bpy.context.scene.workplane_matrix
                      
def set_view_matrix(view_matrix):
    bpy.context.scene.workplane_viewmatrix = flatten(view_matrix)
     
def get_view_matrix():
    return bpy.context.scene.workplane_viewmatrix
     
def flatten(mat):
    dim = len(mat)
    return [mat[j][i] for i in range(dim) 
                      for j in range(dim)]
                      
def set_visibility(state):
    bpy.context.scene.workplane_visible = state
    
def get_visibility():
    return bpy.context.scene.workplane_visible


def set_grid_view3d():
    bpy.types.Scene.workplane_grid_prefs = (
        bpy.context.space_data.show_floor,  
        bpy.context.space_data.show_axis_x,
        bpy.context.space_data.show_axis_y,
        bpy.context.space_data.show_axis_z
    )

def get_grid_view3d():
    return (
        bpy.types.Scene.workplane_grid_prefs[0],
        bpy.types.Scene.workplane_grid_prefs[1],
        bpy.types.Scene.workplane_grid_prefs[2],
        bpy.types.Scene.workplane_grid_prefs[3]
    )

   
def get_user_transform_orientation():
    return bpy.context.scene.workplane_user_transform_orientation
   
def set_user_transform_orientation():
    bpy.types.Scene.workplane_user_transform_orientation = bpy.context.space_data.transform_orientation      
   
   
def is_simple_preview():
    return bpy.context.scene.workplane_preview_mode == "SIMPLE"
   
   
   
   
   
   
   