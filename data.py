import bpy
from mathutils import Matrix, Vector

work_plane = "WorkPlane"

DRAW_MODE = [
    ("FULL", "Full", "", 1),
    ("SIMPLE", "Simple", "", 2)
    ]

class WorkplaneProperties(bpy.types.PropertyGroup):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    matrix = bpy.props.FloatVectorProperty(
            name="matrix",
            size=16,
            subtype="MATRIX")            
                     
    viewmatrix = bpy.props.FloatVectorProperty(
            name="viewmatrix",
            size=16,
            subtype="MATRIX")        

    grid_prefs = bpy.props.BoolVectorProperty(
            name="grid_prefs",
            size=4)


    def active_get(self):
        if "active" in self:        
            return self["active"]
        return False

    def active_set(self, value):
        import workplane.update
        import workplane.operator

        if value:            
            workplane.operator.ensure_updater_running()
            workplane.update.WorkPlaneUpdater.enable_workplane()
        else:
            workplane.update.WorkPlaneUpdater.disable_workplane()

        self["active"] = value

    
    active = bpy.props.BoolProperty(default=True, get=active_get, set=active_set)                     
    visible = bpy.props.BoolProperty(default=True)    
   
    user_transform_orientation = bpy.props.StringProperty(default="GLOBAL")  

    preview_mode = bpy.props.EnumProperty(items=DRAW_MODE)
   
        
def set_matrix(matrix):
    bpy.context.scene.workplane.matrix = flatten(matrix)
     
     
def get_matrix():
    return bpy.context.scene.workplane.matrix
                      
def set_view_matrix(view_matrix):
    bpy.context.scene.workplane.viewmatrix = flatten(view_matrix)
     
def get_view_matrix():
    return bpy.context.scene.workplane.viewmatrix
     
def flatten(mat):
    dim = len(mat)
    return [mat[j][i] for i in range(dim) 
                      for j in range(dim)]
                      
def set_visibility(state):
    bpy.context.scene.workplane.visible = state
    
def get_visibility():
    return bpy.context.scene.workplane.visible


def set_grid_view3d():   
    bpy.context.scene.workplane.grid_prefs = (
        bpy.context.space_data.show_floor,  
        bpy.context.space_data.show_axis_x,
        bpy.context.space_data.show_axis_y,
        bpy.context.space_data.show_axis_z
    )

def get_grid_view3d():
    return (
        bpy.context.scene.workplane.grid_prefs[0],
        bpy.context.scene.workplane.grid_prefs[1],
        bpy.context.scene.workplane.grid_prefs[2],
        bpy.context.scene.workplane.grid_prefs[3]
    )

   
def get_user_transform_orientation():
    return bpy.context.scene.workplane.user_transform_orientation
   
def set_user_transform_orientation():
    bpy.context.scene.workplane.user_transform_orientation = bpy.context.space_data.transform_orientation      
   
   
def is_simple_preview():
    return bpy.context.scene.workplane.preview_mode == "SIMPLE"
   
   
   
   
   
   
   