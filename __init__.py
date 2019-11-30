# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "IES for Cycles +.ldt",
    "author": "u3dreal (Gregor Quade , Q3Dde 2019)",
    "version": (0, 7),
    "blender": (2, 80, 0),
    "description": "Create IES light from ies and ldt files",
    "warning": "",
    "wiki_url": "http://www.q3de.com",
    "tracker_url": "",
    "category": "Add Light"
}

import bpy
from bpy.types import Operator, VIEW3D_MT_light_add, Gizmo, GizmoGroup
from bpy.props import StringProperty, FloatProperty, EnumProperty, IntProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
import os

temp_default = 'T4000'

ctemp_items = (
    ('T1700', "1700K: Match flame", "Match flame"),
    ('T1850', "1850K: Candle light", "Candle light or sunlight at sunrise or sunset"),
    ('T2700', "2700K: Very Warm White", "Similar light to \"normal\" incandescent bulbs, giving a warm \"cosy\" feel"),
    ('T3000', "3000K: Warm White", "The colour of most halogen lamps. Appears slightly \"whiter\" than ordinary incandescent lamps"),
    ('T3200', "3200K: Studio Lamp", "Studio Lamps/Photofloods"),
    ('T3500', "3500K: White", "The standard colour for many fluorescent and compact fluorescent tubes"),
    ('T4000', "4000K: Cool White", "Gives a more clinical or \"high tech\" feel"),
    ('T4100', "4100K: Moonlight", "Moonlight, xenon arc lamp"),
    ('T5000', "5000K: Horizon daylight", "Horizon daylight, tubular fluorescent lamps or Cool White/Daylight compact fluorescent lamps (CFL)"),
    ('T5600', "5600K: Nominal Sunlight", "Nominal Sunlight, mid day during mid summer"),
    ('T6000', "6000K: Daylight", "Fluorescent or compact fluorescent lamps simulating natural daylight"),
    ('T6500', "6500K: Cool Daylight", "Extremely \"white\" light used in specialist daylight lamps"),
    ('T7000', "7000K: LCD/CRT screen", "LCD or CRT screen"),
    ('T8000', "8000K: LCD/CRT screen", "LCD or CRT screen"),
    ('T9000', "9000K: LCD/CRT screen", "LCD or CRT screen"),
    ('T20000', "20000K: Open Sky", "Clear blue poleward sky")
)


def read_ldt(filepath):
    ldt_data = [x.rstrip() for x in open(filepath, 'r', encoding="utf8", errors='ignore')] 
    
    ldt_data = [w.replace(',', '.') for w in ldt_data]  
    ldt_data = [w.replace('"', "") for w in ldt_data] 
    
    return ldt_data


def create_ies(filename, name, ldt_data):
    
    ies = bpy.data.texts.new(name + ".ies")
#header
    ies.write("IESNA:LM-63-2002\n")
    ies.write("[TEST]\t\t\t" + ldt_data[7] + "\n")
    ies.write("[MANUFAC]\t\t" + ldt_data[0] + "\n")
    ies.write("[LUMCAT]\t\t" + ldt_data[9] + "\n")
    ies.write("[LUMINAIRE]\t\t" + ldt_data[8] + "\n")
    ies.write("[LAMP]\t\t\t" + ldt_data[27] + "\n")
    ies.write("[DATE]\t\t\t" + ldt_data[11] + "\n")
    ies.write("[OTHER]\t\t\t" + "EULUMDAT file: " + filename + "\n")
    ies.write("TILT=NONE\n")
    
    if int(ldt_data[26]) == -1:
        d = 25
    else:
        d = 26 
        
    lumens = float(ldt_data[28])
    
    multi = lumens / 1000

#symetry in vertical axis Symetry Type = 1 omit other loops since they are identical
    if ldt_data[2] == "1":
        loops = 1
    else:
        loops = ldt_data[3]
    
#params
    ies.write(ldt_data[d] + " " + ldt_data[28] + " " + str(multi) + "\n" + ldt_data[5] + " " + str(loops) + "\n" + "1" + " 2\n" + str(int(ldt_data[16])/1000) + " " + str(int(ldt_data[15])/1000) + " " + str(int(ldt_data[17])/1000) + "\n1 1 " + ldt_data[31] + "\n")
    
    v_ang = int(ldt_data[3]) 
    h_ang = int(ldt_data[5])
    
    num_lights = ldt_data[25]
    lights_offset = (6*int(num_lights))+10
    
    watts = 0.0
    getw = 31
    i = 1
    while i <= int(num_lights):
        watts += float(ldt_data[getw])
        getw += 6
        i+=1
    try:
        coltemp = int(ldt_data[29])
    except:
        coltemp = 4000
    
    
    
#h_angles
    s = 26+lights_offset
    l = s + v_ang - 1
    s = l + 1
    l = s + h_ang - 1
    
    while s <= l:
        ies.write(ldt_data[s] + " ")
        s += 1
        
    ies.write("\n")
    
#v_angles
    s = 26+lights_offset
    if ldt_data[2] == "1":
        l = s
        while s <= l:
            ies.write(ldt_data[s] + " ")
            s += v_ang
    else:
        l = s + v_ang - 1
        while s <= l:
            ies.write(ldt_data[s] + " ")
            s += 1
        
    ies.write("\n")
    
#lum_data
    num_index = len(ldt_data)
    s = l + 1
    rl = num_index - s
    anz = rl / h_ang
    
#nosymetry Type = 0, 1
    
    if ldt_data[2] == "1":
        s = s + h_ang + (v_ang-1)
    else:
        s = s + h_ang
    
    for i in range(1 , int(anz)):
        
        for hl in range(s , s + h_ang):
            ies.write(ldt_data[hl] + " ")
            s += 1
        ies.write("\n")
        
#symetry in C90-C270 Plane Type = 3 and #symetry in C0-C180 Plane Type = 2  
    symtypes = ["3", "4", "2"]
    
    if ldt_data[2] in symtypes:
        
        s = num_index - h_ang*2
        
        for i in range(1 , int(anz) - 2): 
            for hl in range(s , s + h_ang):
                ies.write(ldt_data[hl] + " ")
                s += 1
            ies.write("\n")
            
            s = s - h_ang*2
        
#symetry in C0-C180 and C90-C270 Type = 4
    if ldt_data[2] == "4":
        
        s = l + h_ang + 1
        
        for i in range(1 , int(anz)): 
            for hl in range(s , s + h_ang):
                ies.write(ldt_data[hl] + " ")
                s += 1
            ies.write("\n")
            
    
        s = num_index - h_ang*2
    
        for i in range(1 , int(anz) - 2):
        
            for hl in range(s , s + h_ang):
                ies.write(ldt_data[hl] + " ")
                s += 1
            ies.write("\n")
            
            s = s - h_ang*2
        
    return ies, watts, coltemp


def add_ies_nodes(filepath, col_temp, lname):
    
    filename = os.path.split(filepath)[1]
    name = os.path.splitext(filename)[0]
    
# create Light
    lightdata = bpy.data.lights.new(lname, 'POINT')
    lightdata.shadow_soft_size = 0.01
    lightdata.use_nodes = True
    lightdata['is_ies'] = True
    lightdata['show_widget'] = True
    
    lname += " " + name
    
    light = bpy.data.objects.new(lname, lightdata)
    light.location = bpy.context.scene.cursor.location
    bpy.context.view_layer.active_layer_collection.collection.objects.link(light)
    bpy.ops.object.select_all(action='DESELECT')
    light.select_set(True)
    light.show_name = True
    bpy.context.view_layer.objects.active = light

    
    
# create Nodes
    lnt = lightdata.node_tree
    
    for node in lnt.nodes:
        if node.bl_idname == 'ShaderNodeEmission':
            lnt_emission = node
            break
        
    lnt_emission.inputs[0].show_expanded = True
    lnt_emission.inputs[1].show_expanded = True
    
    lnt_texies = lnt.nodes.new('ShaderNodeTexIES')
    #lnt_texies.inputs[1].default_value = 0.01
    
    lnt_texies.mode = ('INTERNAL')
    
    filetypes = [".ldt", ".LDT"]
    
    if os.path.splitext(filepath)[1] in filetypes :
        
        iestext,watts,coltemp = create_ies(filename, name, read_ldt(filepath))
        light.data.energy = float(watts)
        color_temp = int(coltemp)
        
    else:
        iestext = bpy.data.texts.load(filepath)
        color_temp = int(col_temp[1:])
        
    lnt_texies.ies = iestext
    
    lnt.links.new(lnt_emission.inputs[1], lnt_texies.outputs[0])
    
    lnt_blackbody = lnt.nodes.new('ShaderNodeBlackbody')
    
    lnt_blackbody.inputs[0].default_value = color_temp
    
    lnt.links.new(lnt_emission.inputs[0], lnt_blackbody.outputs[0])
        
    return {'FINISHED'}
    
    
    
    
custom_arrow_verts = (
(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0),(0.0, -1.0, 0.0), (0.0, 1.0, 0.0),(0.0, 0.0, -1.0),(0.0, 0.0, 1.0),(0.0, 0.0, 1.8), (0.0, 0.0, 5.0)
)

custom_lightshape_verts = (
(-1.0, -1.0, 0.0), (-1.0, 1.0, 0.0),(1.0, -1.0, 0.0), (1.0, 1.0, 0.0)
)

class CrossArrowWidget(Gizmo):
    bl_idname = "VIEW3D_GT_auto_gizmo"
    bl_target_properties = (
        {"id": "offset", "type": 'FLOAT', "array_length": 1},
    )
    __slots__ = (
        "custom_shape_arrow",
        "init_mouse_y",
        "init_value",
    )

    def _update_offset_matrix(self):
        # offset behind the light
        self.matrix_offset.col[3][2] = (self.target_get_value("offset") / -20.0)-1.6

    def draw(self, context):
        self._update_offset_matrix()
        self.draw_custom_shape(self.custom_shape_arrow)
        
    def draw_select(self, context, select_id):
        self._update_offset_matrix()
        self.draw_custom_shape(self.custom_shape_arrow, select_id=select_id)

    def setup(self):
        if not hasattr(self, "custom_shape_arrow"):
            self.custom_shape_arrow = self.new_custom_shape('LINES', custom_arrow_verts)
            
    def invoke(self, context, event):
        self.init_mouse_y = event.mouse_y
        self.init_value = self.target_get_value("offset")
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        context.area.header_text_set(None)
        if cancel:
            self.target_set_value("offset", self.init_value)

    def modal(self, context, event, tweak):
        delta = (event.mouse_y - self.init_mouse_y) / -20.0
        if 'SNAP' in tweak:
            delta = round(delta)
        if 'PRECISE' in tweak:
            delta /= 10.0
        value = self.init_value + delta
        if value >= 0:
            self.target_set_value("offset", value)
            context.area.header_text_set("Power: %.1f Watt" % value)
        return {'RUNNING_MODAL'}
    
            
class IESLIGHTWidgetGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_light_test"
    bl_label = "IES Light Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and ob.type == 'LIGHT' and 'is_ies' in ob.data and ob.data['show_widget'] == True)

    def setup(self, context):
        ob = context.object
        mpr = self.gizmos.new(CrossArrowWidget.bl_idname)
        mpr.target_set_prop("offset", ob.data, "energy")

        mpr.color = 1.0, 0.9, 0.0
        mpr.scale_basis = 0.1
        mpr.color_highlight = 1.0, 1.0, 1.0
        mpr.use_draw_modal = True

        self.energy_widget = mpr

    def refresh(self, context):
        ob = context.object
        mpr = self.energy_widget
        mpr.matrix_basis = ob.matrix_world.normalized()

#importHelper
class ImportIES_OT_ies(Operator, ImportHelper):
    """Import IES light data and generate a node group for cycles"""
    bl_idname = "import_ies.ies"
    bl_label = "Create IES / LDT Light"

    filter_glob : StringProperty(default="*.ies;*.ldt;*.LDT", options={'HIDDEN'})
    lightname : StringProperty(name = "Name", description = "Name of the IES Light", default = "IES")   
    color_temperature : EnumProperty(name="Color Temperature", description="Color temperature of light", items=ctemp_items, default=temp_default)

    def execute(self, context):
        return add_ies_nodes(self.filepath, self.color_temperature, self.lightname)
    
    
#add to add menu
def add_menu(self,context):
    self.layout.operator("import_ies.ies", text="IES/LDT", icon = 'LIGHT_SPOT')
    
classes = (ImportIES_OT_ies,CrossArrowWidget,IESLIGHTWidgetGroup)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    VIEW3D_MT_light_add.append(add_menu)
    
    
def unregister():
    VIEW3D_MT_light_add.remove(add_menu)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    
    
if __name__ == "__main__":
    register()

    
   