import bpy
from mathutils import Matrix, Vector

import workplane.util
import workplane.data
from workplane.data import work_plane
from workplane.update import *

def ensure_updater_running():     
    if not WorkPlaneUpdater.Running:        
        bpy.ops.workplane.internal_workplane_updater()

class SetWorkPlane(bpy.types.Operator):
    """Sets a new workplane orientation"""

    bl_idname = "transform.workplane_set"
    bl_label = "Set the Workplane"
    bl_options = {'REGISTER', 'UNDO'}
  
    pivot_point = bpy.props.EnumProperty(items = 
        [
        #('ACTIVE_ELEMENT','Active Element',''), 
         ('MEDIAN_POINT','Median Point',''),
         ('CURSOR','3D Cursor',''),
         #('BOUNDING_BOX_CENTER','Bounding Box Center',''),
         ],
        name = "Pivot Point",
        default = 'MEDIAN_POINT')
    
    transform_orientation = bpy.props.EnumProperty(items = 
        [('VIEW','View',''), 
         #('GIMBAL','Gimbal',''),
         ('NORMAL','Normal',''),
         ('LOCAL','Local',''),
         ('GLOBAL','Global',''),
         ],
        name = "Transform Orientation",
        default = 'LOCAL')

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "pivot_point")
        box = layout.box()
        box.prop(self, "transform_orientation")
        

    def modal(self, context, event):       
        if event.type == 'LEFTMOUSE':
           return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:            
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        if active_object != None:
            if active_object.mode == "EDIT":
                return active_object.type == 'MESH'
            else:
                return True
        else:
            return False
            
    def execute(self, context):
        
        #print("--- execute ---")
        #print(self.transform_orientation)
        #print(self.pivot_point)

        
        center = self.find_center(context)
        matrix = self.set_transform_orientation(context, self.transform_orientation)
        self.set_workplane_matrix(matrix, center)
        
        bpy.context.workplane.active = True        
        return {'FINISHED'}
    

    def invoke(self, context, event):

        ensure_updater_running()

        bpy.context.scene.workplane.active = True
        workplane.data.set_grid_view3d()        
        workplane.data.set_user_transform_orientation()
        #print( workplane.data.get_user_transform_orientation() )
        #print (bpy.ops.transform.set_workplane.poll())
        #print("--- invoke ---")
                   
        center = self.find_center(context)
        orientation = self.find_orientation(context)
        self.transform_orientation = orientation.split("_EMPTY")[0]    
        
        matrix = self.set_transform_orientation(context, orientation)
        
        #print(self.transform_orientation)
       
        self.set_workplane_matrix(matrix, center)
        
        context.window_manager.modal_handler_add(self)
        
        
        #bpy.ops.workplane.show()
        return {'RUNNING_MODAL'}    
    
    
    def set_workplane_matrix(self, matrix, center):
        matrix = matrix.to_4x4()
        matrix.translation = center
        workplane.data.set_matrix(matrix) 
        
    
    def set_transform_orientation(self, context, transform_orientation):
        #print("catching space: " + transform_orientation) 
        
        #op.create_orientation doesn't work if nothing is selected, so I missuse the view orientation a bit to cicumvent
        use_view = transform_orientation == "VIEW" or transform_orientation.endswith("_EMPTY")
        bpy.ops.transform.create_orientation(name=work_plane, use=True, use_view=use_view, overwrite=True)
        
        current = context.space_data.current_orientation
       
        if transform_orientation.startswith("GLOBAL"):
            current.matrix = Matrix().to_3x3()
    
        if transform_orientation.startswith("LOCAL"):
            active_object = context.active_object
            current.matrix = active_object.matrix_world.to_3x3()   
    
        return current.matrix
    
    
    def has_component_selections(self, context):
        active_object = context.active_object        
        active_object.update_from_editmode()
        
        if active_object.type == 'MESH':
            vert_mode, edge_mode, face_mode = bpy.context.tool_settings.mesh_select_mode
                
            if vert_mode:
                for v in active_object.data.vertices:
                    if v.select:
                        return True#(True, False, False)
                
            elif edge_mode:
                for e in active_object.data.edges:
                    if e.select:
                        return True#(False, True, False)
                
            elif face_mode:
                for f in active_object.data.polygons:
                    if f.select:
                        return True#(False, False, True)
            
        return False#(False, False, False)
    
    
    def find_orientation(self, context):
        
        current = bpy.context.space_data.transform_orientation
        
        no_selection = self.has_component_selections(context) == False
        
        if context.active_object.mode != 'EDIT':
            mode = current
            if current != work_plane:
                #dont know how to calc this
                if current != "GLOBAL":
                    mode = "LOCAL"
                       
            else:
                mode = "GLOBAL"
            
            if no_selection:
                mode = mode + "_EMPTY"
                
            return mode
        
        else:
            if no_selection:
                return "LOCAL_EMPTY"
            else:
                return "NORMAL"


    def find_center(self, context):

        if self.pivot_point == "CURSOR":
            return bpy.context.scene.cursor_location
            
        if len(context.selected_objects) > 1:
            locations = [o.matrix_world.translation for o in context.selected_objects]
            center = sum(locations, Vector()) / len(locations) 
            return center
        else:
            active_object = context.active_object 
            if active_object.mode != 'EDIT':
                return active_object.matrix_world.translation
            
            active_object.update_from_editmode()
            
            if active_object.type == 'MESH':
                locations = []
                vert_mode, edge_mode, face_mode = bpy.context.tool_settings.mesh_select_mode
                                    
                if vert_mode:
                    locations.extend([v.co for v in active_object.data.vertices if v.select])
                if edge_mode:
                    edges = [e.vertices for e in active_object.data.edges if e.select]                    
                    for e in edges:
                        center = (active_object.data.vertices[e[0]].co + active_object.data.vertices[e[1]].co ) * 0.5
                        locations.append(center)   
                if face_mode:
                     locations.extend([f.center for f in active_object.data.polygons if f.select])
                     
                selection_center = sum(locations, Vector()) / len(locations)                    
                pivot_location =  active_object.matrix_world * selection_center       
                return  pivot_location
            else:
                return active_object.matrix_world.translation



def working_in_workplane(context):
    if (context.space_data.current_orientation is not None and
        WorkPlaneUpdater.current_view is not None):
        return context.space_data.current_orientation.name == workplane.data.work_plane
    return False

def has_workplane(context):
    if (WorkPlaneUpdater.current_view is not None):
        return context.scene.orientations.get(workplane.data.work_plane) != None

    return False


class WorkplaneTranslate(bpy.types.Operator):
    bl_idname = "transform.workplane_translate"
    bl_label = "Translate on the Workplane"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return bpy.ops.transform.translate.poll()
        
    def invoke(self, context, event):    
        ensure_updater_running()

        #space, view = workplane.util.get_space_and_view(context, event.mouse_x, event.mouse_y)
        if working_in_workplane(context):
            constraints, workplane_matrix = WorkPlaneUpdater.get_orientation_constraints_and_matrix(WorkPlaneUpdater.current_view)
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=constraints, constraint_orientation=work_plane)       
            return {"FINISHED"}
       
        #use regular translate for everything else
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        return {"FINISHED"}



class WorkplaneRotate(bpy.types.Operator):
    bl_idname = "transform.workplane_rotate"
    bl_label = "Rotates on the Workplane"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return bpy.ops.transform.rotate.poll()
        
    def invoke(self, context, event):    
        ensure_updater_running()

        if working_in_workplane(context):
            constraints, workplane_matrix = WorkPlaneUpdater.get_orientation_constraints_and_matrix(WorkPlaneUpdater.current_view)
            bpy.ops.transform.rotate('INVOKE_DEFAULT', constraint_axis=constraints, constraint_orientation=work_plane)
            return {"FINISHED"}
        
        #use regular translate for everything else
        bpy.ops.transform.rotate('INVOKE_DEFAULT')
        return {"FINISHED"}


            
class WorkplaneScale(bpy.types.Operator):
    bl_idname = "transform.workplane_scale"
    bl_label = "Scales on the Workplane"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        result = bpy.ops.transform.resize.poll()
        return result
        
    def invoke(self, context, event):    
        ensure_updater_running()

        if working_in_workplane(context):
            constraints, workplane_matrix = WorkPlaneUpdater.get_orientation_constraints_and_matrix(WorkPlaneUpdater.current_view)
            bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=constraints, constraint_orientation=work_plane)
            return {"FINISHED"}
        
        #use regular translate for everything else
        bpy.ops.transform.resize('INVOKE_DEFAULT')
        return {"FINISHED"}

class WorkplaneExtrude(bpy.types.Operator):
    bl_idname = "transform.workplane_extrude"
    bl_label = "Extudes on the Workplane"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        result = bpy.ops.view3d.edit_mesh_extrude_move_normal.poll()
        return result
        
    def invoke(self, context, event):    
        ensure_updater_running()

        if working_in_workplane(context):
            print("foooo")
            constraints, workplane_matrix = WorkPlaneUpdater.get_orientation_constraints_and_matrix(WorkPlaneUpdater.current_view)
            bpy.ops.mesh.extrude_region()
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=constraints, constraint_orientation=work_plane)    
            return {"FINISHED"}
                
        bpy.ops.view3d.edit_mesh_extrude_move_normal('INVOKE_DEFAULT')
        return {"FINISHED"}

#bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(-4.13928, -5.01428, -0.726659), "constraint_axis":(False, False, False), "constraint_orientation":'NORMAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})


class WorkplaneShow(bpy.types.Operator):
    bl_idname = "workplane.show"
    bl_label = "Show Workplane"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return workplane.util.has_valid_workplane(context)
    
    def execute(self, context):
        ensure_updater_running()

        workplane.data.set_visibility(True)
        #context.scene.workplane_visible = True
        return {"FINISHED"}

    
    
class WorkplaneHide(bpy.types.Operator):
    bl_idname = "workplane.hide"
    bl_label = "Hide Workplane"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return workplane.util.has_valid_workplane(context)

    def execute(self, context):
        ensure_updater_running()

        workplane.data.set_visibility(False)
        #context.scene.workplane_visible = False

        return {"FINISHED"}

class WorkplaneDisable(bpy.types.Operator):
    bl_idname = "transform.workplane_disable"
    bl_label = "Disables the Workplane"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return working_in_workplane(context)
        
    def invoke(self, context, event):    
        ensure_updater_running()

        t_o = workplane.data.get_user_transform_orientation()
        
        if t_o == workplane.data.work_plane:
            t_o = 'GLOBAL'

        try:
            bpy.context.space_data.transform_orientation = t_o
        except Exception as e:
            bpy.context.space_data.transform_orientation = 'GLOBAL'
       
        return {"FINISHED"}
