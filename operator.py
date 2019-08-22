import bpy
from mathutils import Matrix, Vector

import workplane.util
import workplane.data
import workplane.update 

from workplane.data import work_plane

def ensure_updater_running():     
    if not workplane.update.WP_OT_Updater.Running:        
        bpy.ops.workplane.internal_workplane_updater()

class WP_OT_SetWorkPlane(bpy.types.Operator):
    """Sets a new workplane orientation"""
    bl_description = "Sets the workplane to the current selection"
    bl_idname = "transform.workplane_set"
    bl_label = "Set the Workplane"
    bl_options = {'REGISTER', 'UNDO'}
  
    pivot_point : bpy.props.EnumProperty(items = 
        [
        #('ACTIVE_ELEMENT','Active Element',''), 
         ('MEDIAN_POINT','Median Point',''),
         ('CURSOR','3D Cursor',''),
         #('BOUNDING_BOX_CENTER','Bounding Box Center',''),
         ],
        name = "Pivot Point",
        default = 'MEDIAN_POINT')
    
    transform_orientation : bpy.props.EnumProperty(items = 
        [('VIEW','View',''), 
         #('GIMBAL','Gimbal',''),
         ('NORMAL','Normal',''),
         ('LOCAL','Local',''),
         ('GLOBAL','Global',''),
         ],
        name = "Transform Orientation",
        default = 'LOCAL')
    
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
       
        center = self.find_center(context)
        matrix = self.set_transform_orientation(context, self.transform_orientation)
        self.set_workplane_matrix(matrix, center)
        
        #print(matrix)

        bpy.context.scene.workplane.active = True        
        return {'FINISHED'}
    

    def invoke(self, context, event):
        ensure_updater_running()

        if not working_in_workplane(context):
            workplane.data.store_grid_overlay_prefs()        
            workplane.data.set_user_transform_orientation()       
                    
        active_object = context.active_object
        center = self.find_center(context)
        orientation = self.find_orientation(context)
        self.transform_orientation = orientation.split("_EMPTY")[0]    
        
        matrix = self.set_transform_orientation(context, orientation)
             
        self.set_workplane_matrix(matrix, center)       

        #active_object might get changed to get a correct transform orientation     
        context.view_layer.objects.active = active_object

        bpy.context.scene.workplane.active = True
        return {'FINISHED'}
    
    
    def set_workplane_matrix(self, matrix, center):
        matrix = matrix.to_4x4()
        matrix.translation = center
        workplane.data.set_matrix(matrix) 
        
    
    def set_transform_orientation(self, context, transform_orientation):
        #op.create_orientation doesn't work if nothing is selected, so I missuse the view orientation a bit to cicumvent
        use_view = transform_orientation == "VIEW" or transform_orientation.endswith("_EMPTY")
        bpy.ops.transform.create_orientation(name=work_plane, use=True, use_view=use_view, overwrite=True)
                
        current = bpy.context.scene.transform_orientation_slots[0].custom_orientation
              
        if transform_orientation.startswith("GLOBAL"):
            current.matrix = Matrix().to_3x3()
    
        if transform_orientation.startswith("LOCAL"):
            active_object = context.active_object
            current.matrix = active_object.matrix_world.to_3x3()   
    
        return current.matrix
    
    
    def has_component_selection(self, context):
        result = False, None

        for obj in context.selected_objects:
            if obj.mode != 'EDIT':
                continue

            obj.update_from_editmode()            

            if obj.type == 'MESH':
                vert_mode, edge_mode, face_mode = bpy.context.tool_settings.mesh_select_mode
                    
                if vert_mode:
                    if 0 < obj.data.total_vert_sel and obj.data.total_vert_sel < len(obj.data.vertices):
                        result = True, obj
                        break
                    
                elif edge_mode:
                    if 0 < obj.data.total_edge_sel and obj.data.total_edge_sel < len(obj.data.edges):
                        result = True, obj
                        break
                    
                elif face_mode:
                    if 0 < obj.data.total_face_sel and obj.data.total_face_sel < len(obj.data.polygons):
                        result = True, obj  
                        break                         
               
        return result
    

    def find_orientation(self, context):        
        current = bpy.context.scene.transform_orientation_slots[0].type
        has_selection, obj = self.has_component_selection(context)
                
        if obj:
            print(obj)
            context.view_layer.objects.active = obj

        if context.active_object.mode == 'EDIT':            
            if has_selection:
                return "NORMAL"
            else:
                return "LOCAL_EMPTY"        
        else:
            mode = current
            if current != work_plane:
                #dont know how to calc this
                if current != "GLOBAL":
                    mode = "LOCAL"                       
            else:
                mode = "GLOBAL"
            
            if not has_selection:
                mode = mode + "_EMPTY"
                
            return mode


    def find_center(self, context):

        if self.pivot_point == "CURSOR":
            return bpy.context.scene.cursor.location
            
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
                     
                count = len(locations)
                if count > 0:
                    selection_center = sum(locations, Vector()) / count                  
                    pivot_location = active_object.matrix_world @ selection_center       
                    return pivot_location
            else:
                return active_object.matrix_world.translation


def working_in_workplane(context):
    slot = bpy.context.scene.transform_orientation_slots[0]
    return slot.type == workplane.data.work_plane

def has_workplane(context):
    return workplane.data.work_plane in context.scene.transform_orientation_slots[0].type



#############################################################################################
# Transform Operators
#############################################################################################


class WP_OT_WorkplaneTranslate(bpy.types.Operator):
    bl_description = "Translates (move) selected items with workplane constraints"
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
            constraints, workplane_matrix = WP_OT_Updater.get_orientation_constraints_and_matrix(WorkPlaneUpdater.current_view)
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=constraints, constraint_orientation=work_plane)       
            return {"FINISHED"}
       
        #use regular translate for everything else
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        return {"FINISHED"}



class WP_OT_WorkplaneRotate(bpy.types.Operator):
    bl_description = "Rotate selected items with workplane constraints"
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
            constraints, workplane_matrix = WP_OT_Updater.get_orientation_constraints_and_matrix(WorkPlaneUpdater.current_view)
            bpy.ops.transform.rotate('INVOKE_DEFAULT', constraint_axis=constraints, constraint_orientation=work_plane)
            return {"FINISHED"}
        
        #use regular translate for everything else
        bpy.ops.transform.rotate('INVOKE_DEFAULT')
        return {"FINISHED"}


            
class WP_OT_WorkplaneScale(bpy.types.Operator):
    bl_description = "Scale (resize) selected items with workplane constraints"
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
            constraints, workplane_matrix = WP_OT_Updater.get_orientation_constraints_and_matrix(WorkPlaneUpdater.current_view)
            bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=constraints, constraint_orientation=work_plane)
            return {"FINISHED"}
        
        #use regular translate for everything else
        bpy.ops.transform.resize('INVOKE_DEFAULT')
        return {"FINISHED"}

class WP_OT_WorkplaneExtrude(bpy.types.Operator):
    bl_description = "Extrude and move with workplane constraints"
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
            constraints, workplane_matrix = WP_OT_Updater.get_orientation_constraints_and_matrix(WorkPlaneUpdater.current_view)
            bpy.ops.mesh.extrude_region()
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=constraints, constraint_orientation=work_plane)    
            return {"FINISHED"}
                
        bpy.ops.view3d.edit_mesh_extrude_move_normal('INVOKE_DEFAULT')
        return {"FINISHED"}