import bpy
from mathutils import Matrix, Vector

work_plane = "WorkPlane"

class WorkplaneProperties(bpy.types.PropertyGroup):
    workplane_matrix = bpy.props.FloatVectorProperty(
            name="workplane_matrix",
            size=16,
            subtype="MATRIX")
                      
    workplane_visible = bpy.props.BoolProperty(name="workplane_visible", default=False)


class WorkPlaneData:
    
    @staticmethod                      
    def set_matrix(matrix):
        bpy.context.scene.workplane_matrix = WorkPlaneData.flatten(matrix)
         
         
    @staticmethod
    def get_matrix():
        return bpy.context.scene.workplane_matrix

    @staticmethod                      
    def set_view_matrix(view_matrix):
        bpy.context.scene.workplane_viewmatrix = WorkPlaneData.flatten(view_matrix)
         
         
    @staticmethod
    def get_view_matrix():
        return bpy.context.scene.workplane_viewmatrix

         
    @staticmethod
    def flatten(mat):
        dim = len(mat)
        return [mat[j][i] for i in range(dim) 
                          for j in range(dim)]
                          
    @staticmethod
    def set_visibility(state):
        bpy.context.scene.workplane_visible = state
        
    @staticmethod
    def get_visibility():
        return bpy.context.scene.workplane_visible