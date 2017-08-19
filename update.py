import bpy
import bgl

import math
import mathutils
from mathutils import Matrix, Vector

import workplane.draw
from . import util
from workplane.data import *

X = Vector((1,0,0))
Y = Vector((0,1,0))
Z = Vector((0,0,1))            

active_plane = "XY"

class WorkPlaneUpdater(bpy.types.Operator):
    bl_idname = "workplane.internal_workplane_updater"
    bl_label = "internal"
    bl_options = {"REGISTER", "INTERNAL"}
   
    scene = None
    current_view = None
    Running = False
    
    #@classmethod
    #def poll(cls, context):
    #    return not WorkPlaneUpdater.Running

    def cancel(self, context):
        WorkPlaneUpdater.Running = False 
        
    def invoke(self, context, event):        
        print("STARTED UPDATER")
        WorkPlaneUpdater.Running = True   

        self.grid_enabled = True
        self.space = None
        WorkPlaneUpdater.current_view = None
      
        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0/16.0, context.window)
        wm.modal_handler_add(self)
        
        self.scene = context.scene
        
        return {"RUNNING_MODAL"}
    

    def modal(self, context, event):
        if not WorkPlaneUpdater.Running:
            #self.work_plane_drawer.hide()
            return {'CANCELLED'}
         
        if context.scene != self.scene or self.scene == None:
            #self.work_plane_drawer.hide()
            workplane.draw.disable()
            self.scene = context.scene
                  
        if event.type == 'TIMER':
            #collect the correct view to update the workplane..
            space, view = util.get_space_and_view(context, event.mouse_x, event.mouse_y)
            if space is not None:
                self.space = space
            if view is not None:
                WorkPlaneUpdater.current_view = view     

            workplane_exists = work_plane in bpy.context.scene.orientations            
            if (self.space is None or self.space.current_orientation is None or 
                self.space.current_orientation.name != work_plane or 
                WorkPlaneUpdater.current_view is None):             
                
                if workplane_exists:
                    workplane.draw.disable()

                #take care to restore the grid in sceneview
                if not self.grid_enabled:
                    self.grid_enabled = True
                    self.show_grid()                                     
                                
            else:                          
                #store the grid settings after entering workplane mode
                if self.grid_enabled:
                    self.store_grid()
                    self.grid_enabled = False
                self.hide_grid()

                self.set_orientation(self.space, WorkPlaneUpdater.current_view)
      
        return {"PASS_THROUGH"}
    
    def execute(self, context): 
        return self.invoke(context, None)    
         
    @classmethod     
    def get_orientation_constraints_and_matrix(cls, rv3d):
        view_rotation = rv3d.view_rotation.to_matrix()
        view_dir = view_rotation * Z
        
        M = WorkPlaneData.get_matrix().to_3x3()
                        
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
        workplane.draw.matrix.translation = WorkPlaneData.get_matrix().translation
        
        global active_plane
        active_plane = "XY"

        if constraints == (True, False, True):                    
            active_plane = "XZ"
            rot = mathutils.Matrix.Rotation(math.radians(90.0), 4, X)
            workplane.draw.matrix = workplane_matrix * rot
            
        if constraints == (False, True, True):                    
            active_plane = "YZ"
            rot = mathutils.Matrix.Rotation(math.radians(90.0), 4, Y )
            workplane.draw.matrix = workplane_matrix * rot
        
        
        WorkPlaneData.set_view_matrix(workplane.draw.matrix)
        workplane.draw.enable()
        bpy.context.scene.update()

    def hide_grid(self):
        bpy.context.space_data.show_floor  = False
        bpy.context.space_data.show_axis_x = False
        bpy.context.space_data.show_axis_y = False
        bpy.context.space_data.show_axis_z = False

    def store_grid(self):
        bpy.types.Scene.workplane_grid_prefs = (
            bpy.context.space_data.show_floor,  
            bpy.context.space_data.show_axis_x,
            bpy.context.space_data.show_axis_y,
            bpy.context.space_data.show_axis_z
        )
    
    def show_grid(self):
        bpy.context.space_data.show_floor  = bpy.types.Scene.workplane_grid_prefs[0]
        bpy.context.space_data.show_axis_x = bpy.types.Scene.workplane_grid_prefs[1]
        bpy.context.space_data.show_axis_y = bpy.types.Scene.workplane_grid_prefs[2]
        bpy.context.space_data.show_axis_z = bpy.types.Scene.workplane_grid_prefs[3]
