import os
import unreal
import re


def _unreal_import_fbx_asset(input_path, destination_path, destination_name):
    """
    Import an FBX into Unreal Content Browser
    :param input_path: The fbx file to import
    :param destination_path: The Content Browser path where the asset will be placed
    :param destination_name: The asset name to use; if None, will use the filename without extension
    """
    tasks = []
    tasks.append(_generate_fbx_import_task(input_path, destination_path, destination_name))

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

    first_imported_object = None

    for task in tasks:
        unreal.log("Import Task for: {}".format(task.filename))
        for object_path in task.imported_object_paths:
            unreal.log("Imported object: {}".format(object_path))
            if not first_imported_object:
                first_imported_object = object_path

    return first_imported_object


def _generate_fbx_import_task(
    filename,
    destination_path,
    replace_existing=True,
    as_skeletal=True
    ):
    """
    Create and configure an Unreal AssetImportTask
    :param filename: The fbx file to import
    :param destination_path: The Content Browser path where the asset will be placed
    :return the configured AssetImportTask
    """
    task = unreal.AssetImportTask()
    task.filename = filename
    task.destination_path = destination_path
    # By default, destination_name is the filename without the extension
    task.replace_existing = True
    task.automated = False
    task.save = True
    task.options = unreal.FbxImportUI()
    task.options.import_materials = True
    task.options.import_textures = False
    #task.options.automated_import_should_detect_type = True
    #task.options.import_as_skeletal = as_skeletal
    # task.options.static_mesh_import_data.combine_meshes = True

    #task.options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    #if as_skeletal:
    task.options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH

    return task

def main():

    root_directory = "C:/ValorantMapExport/test/" # put your paths here
    unreal_path = "/Game/ShooterGame/"

    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            # Check if the file is an .psk file              
            if filename.endswith(".fbx"):
                # Construct the full file path
                import_path = os.path.join(dirpath, filename)
                content_path = dirpath.replace(root_directory, unreal_path)
                print(content_path)
                _unreal_import_fbx_asset(import_path, content_path, None)

if __name__ == "__main__":
    main()  
