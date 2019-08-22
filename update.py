import bpy
import bgl

import time

import math
import mathutils
from mathutils import Matrix, Vector

from workplane.operator import working_in_workplane

import workplane.data
from workplane.data import work_plane

from . import util
from . import main

X = Vector((1,0,0))
Y = Vector((0,1,0))
Z = Vector((0,0,1))            

active_plane = "XY"

_updater = None

class WP_OT_Updater(bpy.types.Operator):
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
        WP_OT_Updater.Running = False 
        
    def invoke(self, context, event):        
        print("STARTED UPDATER")
        WP_OT_Updater.Running = True   

        self.grid_overlay_enabled = True   
        self.view_rotation = None
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0/16.0, window=context.window)
        wm.modal_handler_add(self)
            
        global _updater
        _updater = self
        return {"RUNNING_MODAL"}    

    def modal(self, context, event):        

        if not WP_OT_Updater.Running:
            main.draw.disable()
            return {'CANCELLED'}
        
                  
        if event.type == 'TIMER':
            # print("Timer Update:" , time.time())
            # return {"PASS_THROUGH"}

            #collect the correct view to update the workplane..
            space, view = util.get_space_and_view(context, event.mouse_x, event.mouse_y)           
            if not space or not view:
                return {"PASS_THROUGH"}    

            workplane_exists = work_plane in bpy.context.scene.transform_orientation_slots[0].type           
            if workplane_exists:

                if self.grid_overlay_enabled:
                    self.grid_overlay_enabled = False
                    self.hide_grid_overlay()
               
                if self.view_rotation != view.view_rotation:
                    self.view_rotation = view.view_rotation.copy()
                    self.set_orientation(space, view) 
            else:                                                          
                #stop drawing & restore the grid in sceneview
                main.draw.disable()

                if not self.grid_overlay_enabled:                    
                    self.grid_overlay_enabled = True
                    self.show_grid_overlay()             
      
        return {"PASS_THROUGH"}
    
    def execute(self, context): 
        return self.invoke(context, None)    
         
    @classmethod     
    def get_orientation_constraints_and_matrix(cls, rv3d):
        view_rotation = rv3d.view_rotation.to_matrix()
        view_dir = view_rotation @ Z
        
        M = workplane.data.get_matrix().to_3x3()
                        
        x = math.fabs((M @ X).dot(view_dir))
        y = math.fabs((M @ Y).dot(view_dir))
        z = math.fabs((M @ Z).dot(view_dir))
        
        #print("-------------")
        #print("x: " + str(x))
        #print("y: " + str(y))
        #print("z: " + str(z))
        #print("-------------")
        
        enable_x = x < y or x < z
        enable_y = y < x or y < z
        enable_z = z < x or z < y
        constraints = (enable_x,enable_y,enable_z)    
        
        return constraints
         
    def set_orientation(self, v3d, rv3d):         
       
        constraints = WP_OT_Updater.get_orientation_constraints_and_matrix(rv3d)    
        workplane_matrix = workplane.data.get_matrix()

        global active_plane
        active_plane = "XY"

        if constraints == (True, False, True) and not workplane.data.is_simple_preview():                    
            active_plane = "XZ"
            rot = mathutils.Matrix.Rotation(math.radians(90.0), 4, X)
            workplane_matrix = workplane_matrix @ rot 
            
        if constraints == (False, True, True) and not workplane.data.is_simple_preview():                    
            active_plane = "YZ"
            rot = mathutils.Matrix.Rotation(math.radians(90.0), 4, Y )
            workplane_matrix = workplane_matrix @ rot 

        main.draw.update_grid_matrix(workplane_matrix)
        #print(active_plane)       
        main.draw.enable()
        

    def set_grid_overlay_state(self, state):        
        bpy.context.space_data.overlay.show_floor  = state[0]
        bpy.context.space_data.overlay.show_axis_x = state[1]
        bpy.context.space_data.overlay.show_axis_y = state[2]
        bpy.context.space_data.overlay.show_axis_z = state[3]

    def hide_grid_overlay(self):
        self.set_grid_overlay_state((False, False, False, False))
    
    def show_grid_overlay(self):
        self.set_grid_overlay_state(workplane.data.load_grid_overlay_prefs())

    
def enable_workplane():    
    if not working_in_workplane(bpy.context):
        workplane.data.store_grid_overlay_prefs()
        workplane.data.set_user_transform_orientation()    

    bpy.context.scene.transform_orientation_slots[0].type = work_plane      

    _updater.view_rotation = None


def disable_workplane():
    transform_orientation = workplane.data.get_user_transform_orientation()
    
    if transform_orientation == workplane.data.work_plane:
        transform_orientation = 'GLOBAL'
    
    bpy.context.scene.transform_orientation_slots[0].type = transform_orientation
    
    main.draw.disable()
    
