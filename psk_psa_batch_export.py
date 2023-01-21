bl_info = {
  "name": "Psk to Fbx for Unreal",
  "description": "Description :)",
  "author": "Zain",
  "version": (0, 0, 2),
  "blender": (3, 4, 0),
  "support": "COMMUNITY",
  "category": "Import",
}

import re
import os
import bpy
from bpy.types import Scene
from bpy.props import (BoolProperty,
                        StringProperty,
                        EnumProperty,
                        PointerProperty )
from io_import_scene_unreal_psa_psk_280 import pskimport
from io_import_scene_unreal_psa_psk_280 import psaimport

def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.console.scrollback_append(override, text=str(data), type="OUTPUT")    


def show_msg(msg):
    bpy.ops.Pskfbx.message('INVOKE_DEFAULT', message = msg)


class PSKFBX_AddonProperties(bpy.types.PropertyGroup):
    psk_folder_path: bpy.props.StringProperty(name="PSK Folder Path",
                                    description="Select Folder",
                                    default="",
                                    maxlen=1024,
                                    subtype="DIR_PATH")    
    file_enum : bpy.props.EnumProperty(
        name = "File Type",
        description = "choose file type",
        items= [('PSK',"PSK", ""),
                ('PSKX',"PSKX", "")
        ]
        
    )
    psa_folder : bpy.props.StringProperty(name="PSA Folder",
                                    description="Select Folder",
                                    default="",
                                    maxlen=1024,
                                    subtype="DIR_PATH")
    skeleton_folder : bpy.props.StringProperty(name="Skeleton Folder",
                                    description="Select Folder",
                                    default="",
                                    maxlen=1024,
                                    subtype="DIR_PATH")
    psk_file : bpy.props.StringProperty(name="Select PSK",
                                description="Select PSK to use for PSA",
                                default="",
                                maxlen=1024,
                                subtype="FILE_PATH")
    skeleton_enum : bpy.props.EnumProperty(
        name = "File Type",
        description = "use Folder or select PSK",
        items= [('PSK',"SELECT PSK", ""),
                ('FOLDER',"USE FOLDER", "")
        ]
    )
    mesh_bool : bpy.props.BoolProperty(name='Include mesh',
                                 description='if the animation should include the mesh',
                                 default=False,
                                 subtype='NONE')
    
    
    
    

######################## PSK RUN ######################################
class IMPORTEXPORT(bpy.types.Operator):
    bl_idname = "object.importexport"
    bl_label = "import export"
    bl_options = {'REGISTER', 'UNDO'}
       
    def importpsk(path, bmesh):   
        pskimport(
        filepath = path,
        context = None,
        bImportmesh = bmesh,
        bImportbone = True,
        bSpltiUVdata = False,
        fBonesize = 5.0,
        fBonesizeRatio = 0.6,
        bDontInvertRoot = True,
        bReorientBones = False,
        bReorientDirectly = False,
        bScaleDown = False,
        bToSRGB = False,
        error_callback = None)
        
    def importpsa(path):
            psaimport(path,
            context = None,
            oArmature = None,
            bFilenameAsPrefix = False,
            bActionsToTrack = False,
            first_frames = 0,
            bDontInvertRoot = True,
            bUpdateTimelineRange = False,
            bRotationOnly = False,
            bScaleDown = False,
            fcurve_interpolation = 'LINEAR',
            bBoneNameCaseSensitiveCmp = True,
            error_callback = print
            )
    def exportfbx(path):
        bpy.ops.export_scene.fbx(
        filepath=path,
        use_selection = False,
        global_scale = 1.0,
        apply_unit_scale = True,
        apply_scale_options = 'FBX_SCALE_NONE',
        use_space_transform = True,
        bake_space_transform = True,
        object_types = {'ARMATURE', 'MESH'},
        use_mesh_modifiers = True,
        mesh_smooth_type = 'EDGE',
        use_mesh_edges = False,
        use_tspace = False,
        use_custom_props = False,
        add_leaf_bones = False,
        primary_bone_axis = 'Y',
        secondary_bone_axis = 'X',
        use_armature_deform_only = False,
        armature_nodetype = 'NULL',
        bake_anim = True,
        bake_anim_use_all_bones = True,
        bake_anim_use_nla_strips = False,
        bake_anim_use_all_actions = False,
        bake_anim_force_startend_keying = True,
        bake_anim_step = 1.0,
        bake_anim_simplify_factor = 0.0,
        path_mode = 'AUTO',
        embed_textures = False,
        batch_mode = 'OFF',
        use_batch_own_dir = True,
        axis_forward = '-Z',
        axis_up = 'Y',
        )        



class PSKFBX_Run(bpy.types.Operator):
    bl_idname = "object.pskrun"
    bl_label = "Convert PSK to FBX Recursive"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        args = scene.my_properties
        
        root_directory = bpy.path.abspath(args.psk_folder_path)
        # Recursively process all files in the root directory and subdirectories
        for dirpath, dirnames, filenames in os.walk(root_directory):
            for filename in filenames:
                # Check if the file is an .psk file
                if args.file_enum == 'PSK':
                    format = '.psk'
                if args.file_enum == 'PSKX':
                    format = '.pskx'                
                if filename.endswith(format):
                    # Construct the full file path
                    path = os.path.join(dirpath, filename)
                    fbx_path = path.replace(format, '.fbx')
                    # Import the .psk file                  
                    IMPORTEXPORT.importpsk(path, True)
                    #Rename Armature to "Armature"
                    selected = bpy.context.selected_objects[0]
                    selected.name = "Armature"
                    selected.data.name = "Root"
                    # Export the object to .fbx                   
                    IMPORTEXPORT.exportfbx(fbx_path)
                     
                    for material in bpy.data.materials:
                        material.user_clear()
                        bpy.data.materials.remove(material)
                    for armature in bpy.data.armatures:
                        armature.user_clear()
                        bpy.data.armatures.remove(armature)
                    for mesh in bpy.data.meshes:
                        mesh.user_clear()
                        bpy.data.meshes.remove(mesh)                    
                    purge_data = set(o.data for o in context.scene.objects if o.data)
                    bpy.data.batch_remove(context.scene.objects)
                    bpy.data.batch_remove([o for o in purge_data if not o.users])
                    
                    #print('exported ' + path + ' successfully')                        
        return {'FINISHED'}
    
######################### PSA RUN ################################

class PSAFBX_Run(bpy.types.Operator):
    bl_idname = "object.psarun"
    bl_label = "Convert PSA to FBX Recursive"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context = context
        scene = context.scene
        args = scene.my_properties
        
        if args.skeleton_enum == 'FOLDER':
            root_directory = bpy.path.abspath(args.psa_folder)
            # Recursively process all files in the root directory and subdirectories
            for dirpath, dirnames, filenames in os.walk(root_directory):
                for filename in filenames:
                    # Check if the file is an .props.txt file            
                    if filename.endswith('.psa'):
                        # Construct the full file path
                        psa_path = os.path.join(dirpath, filename)
                        print(psa_path)
                        props_path = psa_path.replace('.psa','.props.txt')
                        fbx_path = psa_path.replace('.psa', '.fbx')
                        with open(props_path, 'r') as file:
                            for line in file:
                                if re.search('"Skeleton":', line):
                                    skeleton_asset_path = line.split("'")
                                    skeleton_name = skeleton_asset_path[1].split(".")[1]
                                    print(skeleton_name)      
                                    root_directory = bpy.path.abspath(args.skeleton_folder)
                                    # Recursively process all files in the root directory and subdirectories
                                    for dir, names, files in os.walk(root_directory):
                                        for file in files:
                                            # Check if the file is an .psk file            
                                            if file == (skeleton_name + '.psk'):
                                                # Construct the full file path
                                                skeleton_path = os.path.join(dir, file)                                 
                                                #Import Skeleton as PSK  
                                                IMPORTEXPORT.importpsk(skeleton_path, False)                   
                                                #Rename Armature to "Armature"
                                                selected = bpy.context.selected_objects[0]
                                                selected.name = "Armature"
                                                selected.data.name = "Root"
                                                # Construct PSA path and import
                                                IMPORTEXPORT.importpsa(psa_path)       
                                                # Construct FBX path and export
                                                IMPORTEXPORT.exportfbx(fbx_path)
                                                
                                                #Clear scene
                                                for action in bpy.data.actions:
                                                    action.user_clear()
                                                    bpy.data.actions.remove(action)
                                                for armature in bpy.data.armatures:
                                                    armature.user_clear()
                                                    bpy.data.armatures.remove(armature)
                                                for mesh in bpy.data.meshes:
                                                    mesh.user_clear()
                                                    bpy.data.meshes.remove(mesh)                    
                                                purge_data = set(o.data for o in context.scene.objects if o.data)
                                                bpy.data.batch_remove(context.scene.objects)
                                                bpy.data.batch_remove([o for o in purge_data if not o.users])
                                                
                                                #print('exported ' + psa_path + ' successfully')

        if args.skeleton_enum == 'PSK':
            psk_path = args.psk_file
            root_directory = bpy.path.abspath(args.psa_folder)
            # Recursively process all files in the root directory and subdirectories
            for dirpath, dirnames, filenames in os.walk(root_directory):
                for filename in filenames:
                    # Check if the file is an .props.txt file            
                    if filename.endswith('.psa'):
                        psa_path = os.path.join(dirpath, filename)    
                        fbx_path = psa_path.replace('.psa', '.fbx')
                        
                        #Import Skeleton as PSK        
                        IMPORTEXPORT.importpsk(psk_path, args.mesh_bool)
                        #Rename Armature to "Armature"
                        selected = bpy.context.selected_objects[0]
                        selected.name = "Armature"
                        selected.data.name = "Root"
                        # Construct PSA path and import
                        IMPORTEXPORT.importpsa(psa_path)       
                        # Construct FBX path and export
                        IMPORTEXPORT.exportfbx(fbx_path)
                        #Clear scene
                        scene = context.scene
                        for action in bpy.data.actions:
                            action.user_clear()
                            bpy.data.actions.remove(action)     
                        for material in bpy.data.materials:
                            material.user_clear()
                            bpy.data.materials.remove(material)
                        for armature in bpy.data.armatures:
                            armature.user_clear()
                            bpy.data.armatures.remove(armature)
                        for mesh in bpy.data.meshes:
                            mesh.user_clear()
                            bpy.data.meshes.remove(mesh)                    
                        purge_data = set(o.data for o in context.scene.objects if o.data)
                        bpy.data.batch_remove(context.scene.objects)
                        bpy.data.batch_remove([o for o in purge_data if not o.users])
  
                        print('exported ' + psa_path + ' successfully')
                        
        return {'FINISHED'}  

########## PANELS ###################

class PSKFBX_AddonPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PSK2FBX"
    bl_label = "PSK TO FBX"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = context.scene.my_properties      
        layout.prop(props, "psk_folder_path")
        layout.prop(props, "file_enum")
        layout.operator("object.pskrun", text = "Convert PSK to UE FBX Recursive") 
        
class PSAFBX_AddonPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PSK2FBX"
    bl_label = "PSA TO FBX"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = context.scene.my_properties      
        layout.prop(props, "psa_folder")
        if props.skeleton_enum == 'FOLDER':
            layout.prop(props, "skeleton_folder")
            layout.prop(props, "skeleton_enum") 
        else:
             layout.prop(props, "psk_file")
             layout.prop(props, "skeleton_enum") 
             layout.prop(props, "mesh_bool") 
        layout.operator("object.psarun", text = "Convert PSA to UE FBX Recursive") 
        
          

class PSKFBX_OT_show_message(bpy.types.Operator):
    bl_idname = "pskfbx.message"
    bl_label = "PSK2FBX"
    bl_options = {'REGISTER', 'INTERNAL'}

    message : StringProperty(default = 'Message')

    lines = []
    line0 = None
    def execute(self, context):
        self.lines = self.message.split("\n")
        maxlen = 0
        for line in self.lines:
            if len(line) > maxlen:
                maxlen = len(line)
                
        print(self.message)
            
        self.report({'WARNING'}, self.message)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        self.lines = self.message.split("\n")
        maxlen = 0
        for line in self.lines:
            if len(line) > maxlen:
                maxlen = len(line)
                
        self.line0 = self.lines.pop(0)
        
        return context.window_manager.invoke_props_dialog(self, width = 100 + 6*maxlen)
      
    def cancel(self, context):
        # print('cancel')
        self.execute(self)
        
    def draw(self, context):
        layout = self.layout
        sub = layout.column()
        sub.label(text = self.line0, icon = 'ERROR')

        for line in self.lines:
            sub.label(text = line)

classes = (
    PSKFBX_AddonProperties,
    IMPORTEXPORT,
    PSKFBX_Run,
    PSAFBX_Run,
    PSKFBX_AddonPanel,
    PSAFBX_AddonPanel,    
    PSKFBX_OT_show_message
  
)
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_properties = bpy.props.PointerProperty(type=PSKFBX_AddonProperties)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_properties


if __name__ == "__main__":
    register()
    
bpy.app.handlers.load_post.append(register)