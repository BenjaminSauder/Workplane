import bpy
import bgl
import math

from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d
from mathutils import Matrix, Vector
from mathutils.geometry import intersect_line_plane

import workplane.update
import workplane.util
import workplane.data

init = False
handle_view = None
matrix = Matrix()



#some code here is from space_view3d_math_vis
def tag_redraw_all_view3d():
    workplane.util.all_view3d( lambda region: region.tag_redraw() )


def setup():
    global init
    if init:
        return
    init = True

    view_matrix = workplane.data.get_view_matrix()

    zero = Matrix()
    zero.zero()
    
    #print(view_matrix)

    if view_matrix != zero:
        #print("found matrix display")        
        global matrix
        matrix = view_matrix 

        enable()
        

    #print ("setup done")


def enable():
    global handle_view
    global matrix

    if handle_view:
        return

    #handle_pixel = SpaceView3D.draw_handler_add(draw_callback_px, (), 'WINDOW', 'POST_PIXEL')
    handle_view = bpy.types.SpaceView3D.draw_handler_add(draw_callback_view, (), 'WINDOW', 'POST_VIEW')
   
    tag_redraw_all_view3d()


def disable():
    global handle_view

    if not handle_view:
        return

    #SpaceView3D.draw_handler_remove(handle_pixel, 'WINDOW')
    bpy.types.SpaceView3D.draw_handler_remove(handle_view, 'WINDOW')
   
    handle_view = None

    tag_redraw_all_view3d()


def maprange(a, b, s):
    (a1, a2), (b1, b2) = a, b
    v = b1 + ((s - a1) * (b2 - b1) / (a2 - a1))
    return max(b1, min(b2, v))

def screen_coord_to_workplane_intersection(region, rv3d, co):
    vec = region_2d_to_vector_3d(region, rv3d, co)
    loc = region_2d_to_location_3d(region, rv3d, co, vec)        
    x = intersect_line_plane(loc, loc+vec, matrix.translation, matrix.col[2] )
    return x

def draw_callback_view():

    if not workplane.data.get_visibility():
        return

    if not workplane.update.WorkPlaneUpdater.Running:
        bpy.ops.workplane.internal_workplane_updater()

     # colors
    #gray  = (1.0, 1.0, 1.0, 0.05)
   
    magenta = (1, 0, 1, 1)

    context = bpy.context

    bgl.glEnable(bgl.GL_BLEND)

    region = context.region
    rv3d = context.space_data.region_3d
    
    left   = (0, int(region.height * 0.5))
    right  = (region.width, int(region.height * 0.5))
    top    = (int(region.width * 0.5), region.height)
    bottom = (int(region.width * 0.5), 0)
    center = (int(region.width * 0.5), int(region.height * 0.5))

    coords = (top, right, bottom, left)

    #grab intersection of workplane and screen center, and round to neares even
    middle = screen_coord_to_workplane_intersection(region, rv3d, center)
    v = matrix.inverted_safe() * middle
    middle = matrix * Vector((round(v.x), round(v.y), 0))
    
    #matrix.translation = middle
    #draw_point_3d(magenta, middle)

    dist = 500
    for co in coords:
        intersection = screen_coord_to_workplane_intersection(region, rv3d, co)
        #vec = region_2d_to_vector_3d(region, rv3d, co)
        #loc = region_2d_to_location_3d(region, rv3d, co, vec)        
        #x = intersect_line_plane(loc, loc+vec, matrix.translation, matrix.col[2] )
        if intersection and middle:
            d = (middle - intersection).length            
            dist = min(d, dist)
            #dist += d
            #draw_point_3d(magenta, x)
    
    #dist /= 4
    
    amount = int(dist) * 2 
    amount = min(amount, 1000) #cap this...
    amount += 20 - (amount % 20) #round to next even 10
   
    step = 1
    if amount >= 1024:
        step = 10
    elif amount >= 512:
        step = 5
    elif amount >= 256:
        step = 2
    
    if workplane.data.is_simple_preview():
        amount = 20

    half = int((amount - (amount % step)) * 0.5)  
    offset = Vector((-half, -half, 0))
   
    gridmatrix = matrix.copy()

    if not workplane.data.is_simple_preview():
        gridmatrix.translation = middle

    for i in range(0, amount):
    
        #bell like graph shape for the alpha to get nice fading
        scale = 0.5
        x = i / float(amount)
        alpha = math.pow(4, scale) * math.pow(x *(1-x), scale)        
        

        gray = (1.0, 1.0, 1.0, alpha * 0.2 )

        if i % step != 0:
            continue
        '''                
        if i % 5 == 0:
            gray  = (1.0, 1.0, 1.0, 0.1 )
        '''

        a1 = gridmatrix * (Vector((0, i, 0)) + offset)
        a2 = gridmatrix * (Vector((amount, i, 0)) + offset)
        
        b1 = gridmatrix * (Vector((i, 0, 0)) + offset)
        b2 = gridmatrix * (Vector((i, amount, 0)) + offset)
        
        draw_line_3d(gray, a1, a2)
        draw_line_3d(gray, b1, b2)
    
        if i == amount-1:

            a1 = gridmatrix * (Vector((0, i+1, 0)) + offset)
            a2 = gridmatrix * (Vector((amount, i+1, 0)) + offset)
            
            b1 = gridmatrix * (Vector((i+1, 0, 0)) + offset)
            b2 = gridmatrix * (Vector((i+1, amount, 0)) + offset)
            
            draw_line_3d(gray, a1, a2)
            draw_line_3d(gray, b1, b2)
            
    #draw_line_3d()

    #draw_basis_colors(half*1.1)
   
    
    bgl.glEnd()
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


red   = (1.0, 0, 0, 0.2)
green = (0, 1.0, 0, 0.2)
blue  = (0, 0, 1.0, 0.2)

def draw_basis_colors(length):
    thickness = 1.5
    if workplane.update.active_plane == "XY":
        a1 = matrix * Vector((-length, 0, 0))
        a2 = matrix * Vector((length, 0, 0))
        b1 = matrix * Vector((0,-length, 0))
        b2 = matrix * Vector((0,length, 0))
        draw_line_3d(red, a1, a2,thickness)
        draw_line_3d(green, b1, b2, thickness)

    elif workplane.update.active_plane == "XZ":
        a1 = matrix * Vector((-length, 0, 0))
        a2 = matrix * Vector((length, 0, 0))
        b1 = matrix * Vector((0,-length, 0))
        b2 = matrix * Vector((0, length, 0))
        draw_line_3d(red, a1, a2, thickness)
        draw_line_3d(blue, b1, b2, thickness)

    elif workplane.update.active_plane == "YZ":
        a1 = matrix * Vector((-length,0, 0))
        a2 = matrix * Vector((length,0, 0))
        b1 = matrix * Vector((0,-length, 0))
        b2 = matrix * Vector((0, length, 0))
        draw_line_3d(blue, a1, a2, thickness)
        draw_line_3d(green, b1, b2, thickness)
                 
def draw_line_3d(color, start, end, width = 1.0):

    transparent = (color[0], color[1], color[2], 0)
    center = (start + end) * 0.5
    
    bgl.glLineWidth(width)

    bgl.glBegin(bgl.GL_LINES)
    bgl.glColor4f(*transparent)
    bgl.glVertex3f(*start) 

    bgl.glColor4f(*color)
    bgl.glVertex3f( *center )
    bgl.glEnd()

    bgl.glBegin(bgl.GL_LINES)
    bgl.glColor4f(*color)
    bgl.glVertex3f(*center)

    bgl.glColor4f(*transparent)
    bgl.glVertex3f(*end)
    bgl.glEnd()



def draw_point_3d(color, pos, size = 1.0):
    x = Vector((0.3, 0, 0))
    y = Vector((0, 0.3, 0))
    z = Vector((0, 0, 0.3))
    draw_line_3d(color, pos - x, pos + x, size) 
    draw_line_3d(color, pos - y, pos + y, size) 
    draw_line_3d(color, pos - z, pos + z, size)
