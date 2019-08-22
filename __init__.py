bl_info = {
    "name": "Workplane",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "category": "3D View",
    "author": "Benjamin Sauder",
    "description": "Allows for quicker workflow using move/rotate/scale on a user defined workplane",
    "version": (0, 2),
    "location": "View3D > Tool Shelf",
}


if "bpy" in locals():
    import importlib
    importlib.reload(main)
    importlib.reload(data)
    importlib.reload(draw)
    importlib.reload(operator)
    importlib.reload(ui)
    importlib.reload(update)
    importlib.reload(util)
    
else:
    from . import (
        main,
        data,
        draw,
        operator,
        ui,
        update,
        util
        )
  

import bpy

classes = [
    data.WP_OT_WorkplaneProperties, 
    update.WP_OT_Updater,
    operator.WP_OT_SetWorkPlane,   
    operator.WP_OT_WorkplaneTranslate,
    operator.WP_OT_WorkplaneRotate,
    operator.WP_OT_WorkplaneScale,
    operator.WP_OT_WorkplaneExtrude,
    ui.VIEW3D_PT_WORKINGPLANE,  
    # ui.VIEW3D_PT_WorkplanePanelTransform,
    # ui.VIEW3D_PT_WorkplanePanelMeshEdit,
]

def register():   

    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.workplane = bpy.props.PointerProperty(type=data.WP_OT_WorkplaneProperties)    


def unregister():
    update.WP_OT_Updater.Running = False
    main.draw.disable()

    del bpy.types.Scene.workplane
     
    for c in classes:
        bpy.utils.unregister_class(c)
            

