import math
import numpy as np

import bpy
import bgl
import gpu
from gpu_extras.batch import batch_for_shader

from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d
from mathutils import Matrix, Vector
from mathutils.geometry import intersect_line_plane

import workplane.update
import workplane.util
import workplane.data

red   = (1.0, 0, 0, 0.2)
green = (0, 1.0, 0, 0.2)
blue  = (0, 0, 1.0, 0.2)
magenta = (1, 0, 1, 1)

class Render():

    def __init__(self):        
        self.view_handler = None
        self._matrix = Matrix()
        self.gridmatrix = None
        self.amount = 0

        self.shader = gpu.shader.from_builtin('3D_SMOOTH_COLOR')
        self.batch = None

    def enable(self):
        if self.view_handler:
            return

        self.disable()

        self.view_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, (), 'WINDOW', 'POST_VIEW')
        self.tag_redraw_all()

    def disable(self):
        if self.view_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self.view_handler, 'WINDOW')
        self.view_handler = None
        self.tag_redraw_all()

    def tag_redraw_all(self):
        workplane.util.all_view3d( lambda region: region.tag_redraw() )

    def screen_coord_to_workplane_intersection(self, region, rv3d, co):
        vec = region_2d_to_vector_3d(region, rv3d, co)
        loc = region_2d_to_location_3d(region, rv3d, co, vec)        
        x = intersect_line_plane(loc, loc+vec, self._matrix.translation, self._matrix.col[2] )
        return x

    def update_grid_matrix(self, matrix):
        self._matrix = matrix

        # translation = Matrix()
        # if self.gridmatrix and not workplane.data.is_simple_preview():
        #     translation = Matrix.Translation(self.gridmatrix.translation)

        self.gridmatrix = self._matrix.copy()
        # self.gridmatrix @= translation

        #print(self.gridmatrix)
        
    def calc_grid_size(self, region, rv3d):        
        left   = (0, int(region.height * 0.5))
        right  = (region.width, int(region.height * 0.5))
        top    = (int(region.width * 0.5), region.height)
        bottom = (int(region.width * 0.5), 0)
        center = (int(region.width * 0.5), int(region.height * 0.5))

        coords = (top, right, bottom, left)

        #grab intersection of workplane and screen center, and round to nearest even
        middle = self.screen_coord_to_workplane_intersection(region, rv3d, center)
        v = self._matrix.inverted_safe() @ middle
        middle = self._matrix @ Vector((round(v.x), round(v.y), 0))
    
        dist = 500
        for co in coords:
            intersection = self.screen_coord_to_workplane_intersection(region, rv3d, co)

            if intersection and middle:
                d = (middle - intersection).length            
                dist = min(d, dist)
    
        amount = int(dist) * 2 
        amount = min(amount, 1000) #cap this...
        amount += 20 - (amount % 20) #round to next even 10

        return amount, middle

    def create_grid_buffers(self, amount, middle):
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
    
        lines = []
        colors = []
        
        for i in range(0, amount):
        
            scale = 0.5
            x = i / float(amount)
            
            #bell like graph shape for the alpha to get nice fading:
            #alpha = math.pow(4, scale) * math.pow(x *(1-x), scale) 

            #triang graph: 
            alpha = self.tri(0.5, x * 2 * 3.141) * 0.5 + 0.5

            #gray = bpy.context.user_preferences.themes[0].view_3d.grid
            #gray = (gray.r, gray.g, gray.b, alpha)
            gray = (1.0, 1.0, 1.0, alpha * 0.1)

            # gray = 1.0, 1.0, 1.0, 1.0

            if i % step != 0:
                continue
            '''                
            if i % 5 == 0:
                gray  = (1.0, 1.0, 1.0, 0.1 )
            '''

            a1 = Vector((0, i, 0)) + offset
            a2 = Vector((amount, i, 0)) + offset            
            b1 = Vector((i, 0, 0)) + offset
            b2 = Vector((i, amount, 0)) + offset
            
            lines.append((a1, a2, b1, b2))
            colors.append((gray, gray, gray, gray))
                
            if i == amount-1:
                a1 = Vector((0, i+1, 0)) + offset
                a2 = Vector((amount, i+1, 0)) + offset
                b1 = Vector((i+1, 0, 0)) + offset
                b2 = Vector((i+1, amount, 0)) + offset
                
                lines.append((a1, a2, b1, b2))
                colors.append((gray, gray, gray, gray))

        lines = np.array(lines)
        lines = lines.ravel()
        lines = lines.reshape(-1, 3)
        lines = lines.tolist()
        # print(lines)

        colors = np.array(colors)
        colors = colors.ravel()
        colors = colors.reshape(-1, 4)
        colors = colors.tolist()
                    
        self.batch = batch_for_shader(self.shader, 'LINES', {"pos": lines, "color": colors})

    def draw(self):
       
        if not workplane.data.get_visibility():
            return

        # if not workplane.update.WorkPlaneUpdater.Running:
        #     bpy.ops.workplane.internal_workplane_updater()
       
        context = bpy.context
        region = context.region
        rv3d = context.space_data.region_3d
      
        amount, middle = self.calc_grid_size(region, rv3d)
        
        if not workplane.data.is_simple_preview():
            self.gridmatrix.translation = middle

        if self.amount != amount:
            self.amount = amount
            self.create_grid_buffers(amount, middle)
    

        # print(self.lines)

        if self.batch:
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glEnable(bgl.GL_DEPTH_TEST)
            bgl.glEnable(bgl.GL_LINE_SMOOTH)
            bgl.glLineWidth(2)       
           
            view_matrix = bpy.context.region_data.perspective_matrix
            
            gpu.matrix.push()
            gpu.matrix.load_matrix(self.gridmatrix)
            
            gpu.matrix.push_projection()    
            gpu.matrix.load_projection_matrix(view_matrix)
            
            self.shader.bind()
            self.batch.draw(self.shader)

            # restore opengl defaults
            gpu.matrix.pop()
            gpu.matrix.pop_projection()

            bgl.glDisable(bgl.GL_BLEND)
            bgl.glDisable(bgl.GL_DEPTH_TEST)
            bgl.glDisable(bgl.GL_LINE_SMOOTH)
            bgl.glLineWidth(1)

    #merci: http://www.iquilezles.org/apps/graphtoy/utils.js?v=1
    def tri(self, a,x):
        x = x / (2.0 * 3.141)
        x = x % 1.0
        if x < 0.0:
            x += 1.0

        if x<a:
            x=x/a
        else:
            x = 1.0-(x-a)/(1.0-a)
        return -1.0+2.0*x
