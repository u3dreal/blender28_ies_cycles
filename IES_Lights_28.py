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
    "name": "IES for Cycles",
    "author": "u3dreal (Gregor Quade , Q3Dde 2019)",
    "version": (0, 5),
    "blender": (2, 80, 0),
    "description": "Create IES light from ies files",
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


def add_ies_nodes(filepath, col_temp, lname):
    
    filename = os.path.split(filepath)[1]
    name = os.path.splitext(filename)[0]
    
# create Light
    lightdata = bpy.data.lights.new(lname, 'POINT')
    lightdata.shadow_soft_size = 0.01
    lightdata.use_nodes = True
    lightdata['is_ies'] = True
    
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
    
    iestext = bpy.data.texts.load(filepath)
    
    color_temp = int(col_temp[1:])
        
    lnt_texies.ies = iestext
    
    lnt.links.new(lnt_emission.inputs[1], lnt_texies.outputs[0])
    
    lnt_blackbody = lnt.nodes.new('ShaderNodeBlackbody')
    
    lnt_blackbody.inputs[0].default_value = color_temp
    
    lnt.links.new(lnt_emission.inputs[0], lnt_blackbody.outputs[0])
        
    return {'FINISHED'}
    
    
#importHelper
class ImportIES_OT_ies(Operator, ImportHelper):
    """Import IES light data and generate a node group for cycles"""
    bl_idname = "import_ies.ies"
    bl_label = "Create IES Light"

    filter_glob : StringProperty(default="*.ies;*.IES", options={'HIDDEN'})
    lightname : StringProperty(name = "Name", description = "Name of the IES Light", default = "IES")   
    color_temperature : EnumProperty(name="Color Temperature", description="Color temperature of light", items=ctemp_items, default=temp_default)

    def execute(self, context):
        return add_ies_nodes(self.filepath, self.color_temperature, self.lightname)
    
    
#add to add menu
def add_menu(self,context):
    self.layout.operator("import_ies.ies", text="IES", icon = 'LIGHT_SPOT')
    
    
def register():
    bpy.utils.register_class(ImportIES_OT_ies)
    VIEW3D_MT_light_add.append(add_menu)
    
    
def unregister():
    VIEW3D_MT_light_add.remove(add_menu)
    bpy.utils.unregister_class(ImportIES_OT_ies)
    
    
if __name__ == "__main__":
    register()

    
   