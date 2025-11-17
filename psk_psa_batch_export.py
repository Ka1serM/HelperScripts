bl_info = {
  "name": "ActorX to FBX for Unreal",
  "description": "Bulk convert ActorX to FBX for UE",
  "author": "Zain/Buckminsterfullerene",
  "version": (0, 1, 0),
  "blender": (4, 5, 0),
  "support": "COMMUNITY",
  "category": "Import",
}

import os
import json
import bpy
from bpy.types import Scene
from bpy.props import (BoolProperty,
                        StringProperty,
                        EnumProperty,
                        PointerProperty )
try:
    from io_scene_psk_psa.psk.reader import read_psk
    from io_scene_psk_psa.psk.importer import import_psk, PskImportOptions
    from io_scene_psk_psa.psa.reader import read_psa
    from io_scene_psk_psa.psa.importer import import_psa
    MODERN_ADDON = True
except ImportError:
    try:
        from io_scene_psk_psa.psk_import import psk_import
        from io_scene_psk_psa.psa_import import psa_import
        MODERN_ADDON = True
    except ImportError:
        from io_import_scene_unreal_psa_psk_280 import pskimport
        from io_import_scene_unreal_psa_psk_280 import psaimport
        MODERN_ADDON = False

def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.console.scrollback_append(override, text=str(data), type="OUTPUT")    


def show_msg(msg):
    bpy.ops.Pskfbx.message('INVOKE_DEFAULT', message = msg)


def cleanup_uv_layers():
    try:
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                mesh = obj.data
                for uv_layer in mesh.uv_layers:
                    for loop_index, loop in enumerate(mesh.loops):
                        uv = uv_layer.data[loop_index].uv
                        # check for NaN values and replace with (0,0)
                        if not (uv.x == uv.x) or not (uv.y == uv.y):  # NaN check
                            print(f"Found NaN UV in layer {uv_layer.name}, replacing with (0,0)")
                            uv_layer.data[loop_index].uv = (0.0, 0.0)
                        # also clamp extreme values that might cause issues
                        elif abs(uv.x) > 1000 or abs(uv.y) > 1000:
                            print(f"Found extreme UV value in layer {uv_layer.name}, clamping")
                            uv_layer.data[loop_index].uv = (max(-1000, min(1000, uv.x)), max(-1000, min(1000, uv.y)))
    except Exception as e:
        print(f"Error cleaning UV layers: {str(e)}")


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
                                description='If the animation should include the mesh',
                                default=False,
                                subtype='NONE')
    replace_fbx_psk : bpy.props.BoolProperty(name='Replace existing FBX file',
                                description='If it should replace existing FBX files',
                                default=True,
                                subtype='NONE')
    replace_fbx_psa : bpy.props.BoolProperty(name='Replace existing FBX file',
                                description='If it should replace existing FBX files',
                                default=True,
                                subtype='NONE')

######################## PSK RUN ######################################
class IMPORTEXPORT(bpy.types.Operator):
    bl_idname = "object.importexport"
    bl_label = "import export"
    bl_options = {'REGISTER', 'UNDO'}
       
    def importpsk(path, bmesh, is_static_mesh=False):
        try:
            if MODERN_ADDON:
                psk_data = read_psk(path)
                options = PskImportOptions()
                options.name = os.path.splitext(os.path.basename(path))[0]
                options.should_import_mesh = bmesh
                options.should_import_skeleton = not is_static_mesh
                options.should_import_materials = True
                options.should_import_vertex_colors = True
                options.should_import_vertex_normals = True
                options.should_import_extra_uvs = True
                options.should_import_shape_keys = True
                options.scale = 1.0 
                
                result = import_psk(psk_data, bpy.context, options)
                cleanup_uv_layers()
                
            else:
                pskimport(
                    filepath = path,
                    context = None,
                    bImportmesh = bmesh,
                    bImportbone = not is_static_mesh, 
                    bSpltiUVdata = False,
                    fBonesize = 5.0,
                    fBonesizeRatio = 0.6,
                    bDontInvertRoot = True,
                    bReorientBones = False,
                    bReorientDirectly = False,
                    bScaleDown = False,
                    bToSRGB = False,
                    error_callback = None)
                cleanup_uv_layers()
                
        except Exception as e:
            print(f"Error importing PSK file {path}: {str(e)}")
            raise e
        
    def importpsa(path):
        try:
            if MODERN_ADDON:
                psa_data = read_psa(path)
                result = import_psa(psa_data, bpy.context)
            else:
                psaimport(path,
                    context = None,
                    oArmature = None,
                    bFilenameAsPrefix = False,
                    bActionsToTrack = False,
                    first_frames = 0,
                    bDontInvertRoot = True,
                    bUpdateTimelineRange = True,
                    bRotationOnly = False,
                    bScaleDown = False,
                    fcurve_interpolation = 'LINEAR',
                    bBoneNameCaseSensitiveCmp = True,
                    error_callback = print
                    )
        except Exception as e:
            print(f"Error importing PSA file {path}: {str(e)}")
            raise e
            
    def exportfbx(path, is_static_mesh=False):
        try:
            cleanup_uv_layers()
            
            if is_static_mesh:
                bpy.ops.export_scene.fbx(
                filepath=path,
                use_selection = False,
                global_scale = 0.01, 
                apply_unit_scale = True,
                apply_scale_options = 'FBX_SCALE_NONE',
                use_space_transform = True,
                bake_space_transform = True,
                object_types = {'MESH'}, 
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
                bake_anim = False, 
                bake_anim_use_all_bones = False,
                bake_anim_use_nla_strips = False,
                bake_anim_use_all_actions = False,
                bake_anim_force_startend_keying = False,
                bake_anim_step = 1.0,
                bake_anim_simplify_factor = 0.0,
                path_mode = 'AUTO',
                embed_textures = False,
                batch_mode = 'OFF',
                use_batch_own_dir = True,
                axis_forward = '-Z',
                axis_up = 'Y',
                )
            else:
                bpy.ops.export_scene.fbx(
                filepath=path,
                use_selection = False,
                global_scale = 0.01, 
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
        except Exception as e:
            print(f"Error exporting FBX file {path}: {str(e)}")
            raise e        

class PSKFBX_Run(bpy.types.Operator):
    bl_idname = "object.pskrun"
    bl_label = "Convert PSK to FBX Recursive"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        args = scene.my_properties
        
        root_directory = bpy.path.abspath(args.psk_folder_path)
        
        success_count = 0
        error_count = 0
        
        for dirpath, dirnames, filenames in os.walk(root_directory):
            for filename in filenames:
                if args.file_enum == 'PSK':
                    format = '.psk'
                elif args.file_enum == 'PSKX':
                    format = '.pskx'
                else:
                    format = '.psk' 
                    
                if filename.endswith(format):
                    path = os.path.join(dirpath, filename)
                    fbx_path = path.replace(format, '.fbx')
                    
                    if os.path.exists(fbx_path) and not args.replace_fbx_psk:
                        print(f'FBX file already exists: {fbx_path}')
                        continue
                    try:
                        print(f'Processing: {path}')
                        is_static_mesh = format == '.pskx'
                        IMPORTEXPORT.importpsk(path, True, is_static_mesh)
                        if not bpy.context.selected_objects:
                            print(f'Warning: No objects imported from {path}')
                            continue
                        if not is_static_mesh:
                            for obj in bpy.context.selected_objects:
                                if obj.type == 'ARMATURE':
                                    obj.name = "Armature"
                                    obj.data.name = "Root"
                                    break        
                        IMPORTEXPORT.exportfbx(fbx_path, is_static_mesh)
                        try:
                            for material in bpy.data.materials:
                                material.user_clear()
                                bpy.data.materials.remove(material)
                        except:
                            pass
                            
                        try:
                            for armature in bpy.data.armatures:
                                armature.user_clear()
                                bpy.data.armatures.remove(armature)
                        except:
                            pass
                            
                        try:
                            for mesh in bpy.data.meshes:
                                mesh.user_clear()
                                bpy.data.meshes.remove(mesh)
                        except:
                            pass
                            
                        try:
                            purge_data = set(o.data for o in context.scene.objects if o.data)
                            bpy.data.batch_remove(context.scene.objects)
                            bpy.data.batch_remove([o for o in purge_data if not o.users])
                        except:
                            pass
                        
                        print(f'Successfully exported: {fbx_path}')
                        success_count += 1
                        
                    except Exception as e:
                        error_msg = f'Error processing {path}: {str(e)}'
                        print(error_msg)
                        self.report({'ERROR'}, error_msg)
                        error_count += 1
                        try:
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
                        except:
                            pass
                        
                        continue
                        
        final_msg = f'Batch conversion complete. Success: {success_count}, Errors: {error_count}'
        print(final_msg)
        self.report({'INFO'}, final_msg)
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

        props_pattern = 'Skeleton = Skeleton'
        
        success_count = 0
        error_count = 0
        
        if args.skeleton_enum == 'FOLDER':
            root_directory = bpy.path.abspath(args.psa_folder)
            for dirpath, dirnames, filenames in os.walk(root_directory):
                for filename in filenames:        
                    if filename.endswith('.psa'):
                        psa_path = os.path.join(dirpath, filename)
                        props_path = (psa_path[:-3] + 'props.txt')
                        fbx_path = (psa_path[:-3] + 'fbx')
                        
                        if os.path.exists(fbx_path) and not args.replace_fbx_psa:
                            print(f'FBX file already exists: {fbx_path}')
                            continue
                        try:
                            print(f'Processing PSA: {psa_path}')
                            if not os.path.exists(props_path):
                                props_path = (psa_path[:-3] + 'json')
                                if not os.path.exists(props_path):
                                    print(f'Props file not found for {psa_path}')
                                    continue
                                with open(props_path) as file:
                                    skeleton_info = json.load(file)
                                skeleton_name = skeleton_info["Properties"]["Skeleton"]["ObjectName"][8:].replace("'", "")
                                
                                root_directory = bpy.path.abspath(args.skeleton_folder)
                                for dir, names, files in os.walk(root_directory):
                                    for file in files:
                                        if file == (skeleton_name + '.psk'):
                                            skeleton_path = os.path.join(dir, file)                                 
                                            IMPORTEXPORT.importpsk(skeleton_path, False)                   
                                            selected = bpy.context.selected_objects[0]
                                            selected.name = "Armature"
                                            selected.data.name = "Root"
                                            IMPORTEXPORT.importpsa(psa_path)       
                                            IMPORTEXPORT.exportfbx(fbx_path, False)  # False = skeletal mesh (PSA has animations)
                                            try:
                                                for action in bpy.data.actions:
                                                    action.user_clear()
                                                    bpy.data.actions.remove(action)
                                                for armature in bpy.data.armatures:
                                                    armature.user_clear()
                                                    bpy.data.armatures.remove(armature)
                                            except:
                                                pass
                                                
                                            print(f'Successfully exported: {fbx_path}')
                                            success_count += 1
                                            break
                            else: 
                                with open(props_path, 'r') as file:
                                    found = False
                                    for line in file:
                                        if found:
                                            break
                                        if (props_pattern in line):
                                            skeleton_asset_path = line.rsplit("'")
                                            skeleton_name = skeleton_asset_path[1].split(".")[1]
                                            print(f'Found skeleton: {skeleton_name}')
                                            
                                            root_directory = bpy.path.abspath(args.skeleton_folder)
                                            for dir, names, files in os.walk(root_directory):
                                                for file in files:
                                                    if file == (skeleton_name + '.psk'):
                                                        skeleton_path = os.path.join(dir, file)
                                                        IMPORTEXPORT.importpsk(skeleton_path, False)
                                                        selected = bpy.context.selected_objects[0]
                                                        selected.name = "Armature"
                                                        selected.data.name = "Root"
                                                        IMPORTEXPORT.importpsa(psa_path)
                                                        IMPORTEXPORT.exportfbx(fbx_path, False)  # False = skeletal mesh (PSA has animations)
                                                        try:
                                                            for action in bpy.data.actions:
                                                                action.user_clear()
                                                                bpy.data.actions.remove(action)
                                                            for armature in bpy.data.armatures:
                                                                armature.user_clear()
                                                                bpy.data.armatures.remove(armature)
                                                        except:
                                                            pass
                                                        print(f'Successfully exported: {fbx_path}')
                                                        success_count += 1
                                                        found = True
                                                        break

                        except Exception as e:
                            error_msg = f'Error processing PSA {psa_path}: {str(e)}'
                            print(error_msg)
                            self.report({'ERROR'}, error_msg)
                            error_count += 1
                            try:
                                for action in bpy.data.actions:
                                    action.user_clear()
                                    bpy.data.actions.remove(action)
                                for armature in bpy.data.armatures:
                                    armature.user_clear()
                                    bpy.data.armatures.remove(armature)
                            except:
                                pass

        if args.skeleton_enum == 'PSK':
            psk_path = args.psk_file
            root_directory = bpy.path.abspath(args.psa_folder)
            for dirpath, dirnames, filenames in os.walk(root_directory):
                for filename in filenames:
                    if filename.endswith('.psa'):
                        psa_path = os.path.join(dirpath, filename)    
                        fbx_path = psa_path.replace('.psa', '.fbx')
                        if os.path.exists(fbx_path) and not args.replace_fbx_psa:
                            print(f'FBX file already exists: {fbx_path}')
                            continue
                        try:
                            print(f'Processing PSA with selected PSK: {psa_path}')     
                            IMPORTEXPORT.importpsk(psk_path, args.mesh_bool)
                            selected = bpy.context.selected_objects[0]
                            selected.name = "Armature"
                            selected.data.name = "Root"
                            IMPORTEXPORT.importpsa(psa_path) 
                            IMPORTEXPORT.exportfbx(fbx_path, False)  # False = skeletal mesh (PSA has animations)
                            try:
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
                            except:
                                pass
                            print(f'Successfully exported: {fbx_path}')
                            success_count += 1
                        except Exception as e:
                            error_msg = f'Error processing PSA {psa_path}: {str(e)}'
                            print(error_msg)
                            self.report({'ERROR'}, error_msg)
                            error_count += 1
                            try:
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
                            except:
                                pass
                        
        final_msg = f'PSA batch conversion complete. Success: {success_count}, Errors: {error_count}'
        print(final_msg)
        self.report({'INFO'}, final_msg)
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
        layout.prop(props, "replace_fbx_psk")
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
        layout.prop(props, "replace_fbx_psa")
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
