import bpy

from workplane.data import *

def all_view3d(func):
    context = bpy.context

    # Py cant access notifers
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        func(region)


def has_valid_workplane(context):
    if work_plane in context.scene.orientations:
        M = Matrix()
        M.zero()
        return M != WorkPlaneData.get_matrix()
        
    return False


def get_space_and_view(context, mouse_x, mouse_y):
    space, view = None, None
    if has_valid_workplane(context):
        space, i = get_quadview_index(context, mouse_x, mouse_y)
        if space is not None:                
            if i is None:
                view = space.region_3d
            else:
                view = space.region_quadviews[i]
    return (space, view)


#https://blender.stackexchange.com/questions/19744/getting-the-active-region
def get_quadview_index(context, x, y):
    for area in context.screen.areas:
        if area.type != 'VIEW_3D':
            continue
        is_quadview = len(area.spaces.active.region_quadviews) == 0
        i = -1
        for region in area.regions:
            if region.type == 'WINDOW':
                i += 1
                if (x >= region.x and
                    y >= region.y and
                    x < region.width + region.x and
                    y < region.height + region.y):

                    return (area.spaces.active, None if is_quadview else i)
    return (None, None)
