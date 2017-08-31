import bpy
import bgl

import math
import mathutils
from mathutils import Matrix, Vector

import workplane.draw
import workplane.data
from workplane.data import work_plane
from . import util

X = Vector((1,0,0))
Y = Vector((0,1,0))
Z = Vector((0,0,1))            

active_plane = "XY"

class WorkPlaneUpdater(bpy.types.Operator):
    bl_idname = "workplane.internal_workplane_updater"
    bl_label = "internal"
    bl_options = {"REGISTER", "INTERNAL"}
   
    context = None
    scene = None
    current_view = None
    Running = False
    space = None
   
    def cancel(self, context):
        WorkPlaneUpdater.Running = False 
        
    def invoke(self, context, event):        
        if WorkPlaneUpdater.Running:
            return {"FINISHED"}
        WorkPlaneUpdater.Running = True   
        #print("STARTED UPDATER")

        self.grid_enabled = True
        self.space = None
        WorkPlaneUpdater.current_view = None
      
        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0/16.0, context.window)
        wm.modal_handler_add(self)
        
        self.scene = context.scene

        if self.scene.workplane.active:
            WorkPlaneUpdater.enable_workplane()
        
        return {"RUNNING_MODAL"}
    

    def modal(self, context, event):
        if not WorkPlaneUpdater.Running:
            WorkPlaneUpdater.show_grid()            
            return {'CANCELLED'}
         
        if context.scene != self.scene or self.scene == None:
            #self.work_plane_drawer.hide()
            workplane.draw.disable()
            self.scene = context.scene
                  
        if event.type == 'TIMER':
            #collect the correct view to update the workplane..
            space, view = util.get_space_and_view(context, event.mouse_x, event.mouse_y)
            if space is not None:
                WorkPlaneUpdater.space = space
            if view is not None:
                WorkPlaneUpdater.current_view = view     

            workplane_exists = work_plane in bpy.context.scene.orientations            
            if (workplane_exists == False or 
                WorkPlaneUpdater.space is None or WorkPlaneUpdater.space.current_orientation is None or 
                WorkPlaneUpdater.space.current_orientation.name != work_plane or 
                WorkPlaneUpdater.current_view is None):             
                               
                workplane.draw.disable()

                #take care to restore the grid in sceneview
                if not self.grid_enabled:                    
                    self.grid_enabled = True
                    WorkPlaneUpdater.show_grid()                                     
                                
            else:
                if self.grid_enabled:
                    self.grid_enabled = False
                    WorkPlaneUpdater.hide_grid()

                self.set_orientation(WorkPlaneUpdater.space, WorkPlaneUpdater.current_view)
      
        return {"PASS_THROUGH"}
    
    def execute(self, context): 
        return self.invoke(context, None)    
         
    @classmethod     
    def get_orientation_constraints_and_matrix(cls, rv3d):
        view_rotation = rv3d.view_rotation.to_matrix()
        view_dir = view_rotation * Z
        
        M = workplane.data.get_matrix().to_3x3()
                        
        x = math.fabs((M*X).dot(view_dir))
        y = math.fabs((M*Y).dot(view_dir))
        z = math.fabs((M*Z).dot(view_dir))
        
        #print("-------------")
        #print("x: " + str(x))
        #print("y: " + str(y))
        #print("z: " + str(z))
        #print("-------------")
        
        enable_x = x < y or x < z
        enable_y = y < x or y < z
        enable_z = z < x or z < y
        constraints = (enable_x,enable_y,enable_z)    
        
        return (constraints, M.to_4x4())
         
    def set_orientation(self, v3d, rv3d):         
       
        constraints, workplane_matrix = WorkPlaneUpdater.get_orientation_constraints_and_matrix(rv3d)
        
        workplane.draw.matrix = workplane_matrix
        workplane.draw.matrix.translation = workplane.data.get_matrix().translation
        
        global active_plane
        active_plane = "XY"

        if constraints == (True, False, True) and not workplane.data.is_simple_preview():                    
            active_plane = "XZ"
            rot = mathutils.Matrix.Rotation(math.radians(90.0), 4, X)
            workplane.draw.matrix = workplane_matrix * rot
            
        if constraints == (False, True, True) and not workplane.data.is_simple_preview():                    
            active_plane = "YZ"
            rot = mathutils.Matrix.Rotation(math.radians(90.0), 4, Y )
            workplane.draw.matrix = workplane_matrix * rot
        
        
        workplane.data.set_view_matrix(workplane.draw.matrix)
        workplane.draw.enable()
        bpy.context.scene.update()


    @staticmethod     
    def set_grid_state(state):        
        WorkPlaneUpdater.space.show_floor  = state[0]
        WorkPlaneUpdater.space.show_axis_x = state[1]
        WorkPlaneUpdater.space.show_axis_y = state[2]
        WorkPlaneUpdater.space.show_axis_z = state[3]

    @staticmethod     
    def hide_grid():
        WorkPlaneUpdater.set_grid_state((False, False, False, False))
    
    @staticmethod     
    def show_grid():
        WorkPlaneUpdater.set_grid_state(workplane.data.get_grid_view3d())

    @staticmethod     
    def enable_workplane():
        try:
            from workplane.operator import working_in_workplane
            if not working_in_workplane(bpy.context):
                workplane.data.set_grid_view3d()
                workplane.data.set_user_transform_orientation()
            
            bpy.context.space_data.transform_orientation = work_plane
        except Exception as e:
            #print(e)
            pass

    @staticmethod
    def disable_workplane():
        transform_orientation = workplane.data.get_user_transform_orientation()
        
        if transform_orientation == workplane.data.work_plane:
            transform_orientation = 'GLOBAL'

        try:
            bpy.context.space_data.transform_orientation = transform_orientation
        except Exception as e:
            if bpy.context.space_data != None:
                bpy.context.space_data.transform_orientation = 'GLOBAL'
        
