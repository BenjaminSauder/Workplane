bl_info = {
    "name": "Workplane",
    "category": "3D View",
    "author": "Benjamin Sauder",
    "description": "Allows for quicker workflow using move/rotate/scale on a user defined workplane",
    "version": (0, 2),
    "location": "View3D > Tool Shelf",
    "blender": (2, 78, 0),
}


if "bpy" in locals():
    import importlib
    importlib.reload(data)
    importlib.reload(draw)
    importlib.reload(operator)
    importlib.reload(ui)
    importlib.reload(update)
    importlib.reload(util)    
else:
    from . import (
        data,
        draw,
        operator,
        ui,
        update,
        util
        )
  
import bpy
from bpy.app.handlers import persistent

classes = [
    data.WorkplaneProperties, 
    update.WorkPlaneUpdater,
    operator.SetWorkPlane,   
    operator.WorkplaneTranslate,
    operator.WorkplaneRotate,
    operator.WorkplaneScale,
    operator.WorkplaneExtrude,  
    ui.WorkplanePanelMenu,
    ui.WorkplanePanelTransform,
    ui.WorkplanePanelMeshEdit,
]

def register():

    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.workplane = bpy.props.PointerProperty(type=data.WorkplaneProperties)    

    bpy.types.VIEW3D_MT_edit_mesh_specials.append(ui.menu_func)

    bpy.app.handlers.load_post.append(load_handler)
    

@persistent
def load_handler(dummy):
    print("Workplane Init")
    draw.setup()
    operator.ensure_updater_running()
    bpy.context.scene.workplane.active = False

def unregister():

    update.WorkPlaneUpdater.Running = False
    update.WorkPlaneUpdater.show_grid()            
    draw.disable()

    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(ui.menu_func)

    del bpy.types.Scene.workplane
     
    for c in classes:
        bpy.utils.unregister_class(c)
            

