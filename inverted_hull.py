#// BEGIN MIT LICENSE BLOCK //
#//
#// Copyright (c) 2019 dskjal
#// This software is released under the MIT License.
#// http://opensource.org/licenses/mit-license.php
#//
#// END MIT LICENSE BLOCK   //
import bpy
bl_info = {
    "name" : "Inverted Hull Setup Tool",
    "author" : "dskjal",
    "version" : (1, 1),
    "blender" : (2, 83, 0),
    "location" : "View3D > Sidebar > Inverted Hull",
    "description" : "Setup inverted hull.",
    "warning" : "",
    "wiki_url" : "https://github.com/dskjal/Inverted-Hull-Setup-Tool",
    "tracker_url" : "",
    "category" : "Object"
}

# inverted hull
ih_name = 'IH_RIM'

def get_solidify(o):
    for m in o.modifiers:
        if m.name == ih_name:
            return m
    return None

def get_solidify_force(o):
    m = get_solidify(o)
    if m == None:
        m = o.modifiers.new(name=ih_name, type='SOLIDIFY')
        m.use_flip_normals = True
        m.thickness = -0.05

    return m

def get_material_rna(o):
    for m in o.data.materials:
        if ih_name in m.name:
            return m.node_tree.nodes['Emission'].inputs[0]
    return None

def get_material_idx(o):
    idx = -1
    num_slots = len(o.material_slots)
    mat_name = ih_name + o.name
    for i in range(num_slots):
        if o.material_slots[i].name == mat_name:
            return i
        
    if num_slots == 0:
        o.data.materials.append(bpy.data.materials['Material'])
        num_slots = 1

    try:
        m = bpy.data.materials[mat_name]
    except:
        m = bpy.data.materials.new(name=mat_name)
        
    m.use_nodes = True
    m.use_backface_culling = True
    m.shadow_method = 'NONE'

    nodes = m.node_tree.nodes
    # init nodes
    for n in nodes:
        nodes.remove(n)

    # gen nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.label = 'Material Output'
    output.location = (300, 0)

    emission = nodes.new(type='ShaderNodeEmission')
    emission.label = 'Emission'
    emission.location = (0, 0)
    emission.inputs[0].default_value = (0, 0, 0, 1)

    #link
    links = m.node_tree.links
    links.new(emission.outputs[0], output.inputs[0])
    

    o.data.materials.append(m)
    
    return num_slots

class DSKJAL_OT_GenButton(bpy.types.Operator):
    bl_idname = 'dskjal.invertedhullgen'
    bl_label = 'Setup Inverted Hull'

    @classmethod
    def poll(self, context):
        o = context.active_object
        return o and o.type == 'MESH'

    def execute(self, context):
        meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        for m in meshes:
            solidify = get_solidify_force(m)
            solidify.material_offset = get_material_idx(m)
        return {'FINISHED'}


def remove_inverted_hull(o):
    solidifies = [m for m in o.modifiers if m.name == ih_name]
    for s in solidifies:
        o.modifiers.remove(s)
    
    for i in range(len(o.data.materials)):
        if ih_name in o.data.materials[i].name:
            o.data.materials.pop(index=i)

class DSKJAL_OT_RemoveButton(bpy.types.Operator):
    bl_idname = 'dskjal.invertedhullremove'
    bl_label = 'Remove Inverted Hull'

    @classmethod
    def poll(self, context):
        o = context.active_object
        return o and o.type == 'MESH'

    def execute(self, context):
        meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        for m in meshes:
            remove_inverted_hull(m)

        return {'FINISHED'}
        
class DSKJAL_PT_InvertedHullUI(bpy.types.Panel):
    bl_label = 'Inverted Hull Setup Tool'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Inverted Hull'

    def draw(self, context):
        scn = context.scene
        col = self.layout.column()
        col.operator('dskjal.invertedhullgen')
        col.operator('dskjal.invertedhullremove')
        col.separator()
        col.separator()
        try:
            o = bpy.context.active_object
            col.prop(get_solidify(o), 'thickness')
            col.prop(get_material_rna(o), 'default_value', text='Outline Color')
        except:
            pass

classes = (
    DSKJAL_PT_InvertedHullUI,
    DSKJAL_OT_GenButton,
    DSKJAL_OT_RemoveButton
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()