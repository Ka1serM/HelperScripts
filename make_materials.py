import unreal
def set_mi_texture(mi_asset, param_name, tex_path):
    if not unreal.EditorAssetLibrary.does_asset_exist(tex_path):
        unreal.log_warning("Can't find texture: " + tex_path)
        return False
    tex_asset = unreal.EditorAssetLibrary.find_asset_data( tex_path ).get_asset()
    return unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi_asset, param_name, tex_asset)

def main():
    unreal.log("---------------------------------------------------")
    AssetTools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    MaterialEditingLibrary = unreal.MaterialEditingLibrary
    EditorAssetLibrary = unreal.EditorAssetLibrary


    base_material_path = "/Game/Valorant/Characters/_Core/MasterMaterials/3P_Character_Mat_V5"

    base_mtl = unreal.EditorAssetLibrary.find_asset_data(base_material_path)
    #Iterate over selected meshes
    sel_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    mesh_list = []
    texture_list = []
    for asset in sel_assets:
        if asset.get_class().get_name() == "SkeletalMesh":
            mesh_list.append(asset)
        else:
            continue #skip non-sm
    for mesh in mesh_list:
        asset_name = mesh.get_name()    
        asset_folder = unreal.Paths.get_path(mesh.get_path_name()) 
        base_folder = asset_folder[:-7] #get base folder (subtract "Meshes" from base path)
        tex_folder = ("".join (base_folder + '/Materials/'))
        assets_in_folder = asset_registry.get_assets_by_path(tex_folder)
        for a in assets_in_folder:
            if a.get_class().get_name() == "Texture2D":
                texture_list.append(a)

        #name of material instance for this mesh
        if (texture_list[0] != None):
            tex_name = texture_list[0].get_asset().get_name()
            mi_name = ( tex_name.rsplit('_', 1)[0] + "_MI")
            mi_full_path = tex_folder + mi_name
            #Check if material instance already exists
            if EditorAssetLibrary.does_asset_exist(mi_full_path):
                mi_asset = EditorAssetLibrary.find_asset_data(mi_full_path).get_asset()
                unreal.log("Asset already exists")
            else:
                mi_asset = AssetTools.create_asset(mi_name, tex_folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())        
            #set material instance parameters!
            MaterialEditingLibrary.set_material_instance_parent( mi_asset, base_mtl.get_asset() )  # set parent material
            #MaterialEditingLibrary.set_material_instance_scalar_parameter_value( mi_asset, "Desaturation", 0.3) # set scalar parameter 
            #find textures for this mesh
            for texture in texture_list:
                asset = texture.get_asset()
                if asset.get_name().endswith('_DF'):
                    set_mi_texture(mi_asset, 'Diffuse', asset.get_path_name())
                if asset.get_name().endswith('_MRAE'):
                    set_mi_texture(mi_asset, 'MRAE', asset.get_path_name())       
                if asset.get_name().endswith('_NM'):
                    set_mi_texture(mi_asset, 'Normal', asset.get_path_name())
            #set new material instance on static mesh
            #index = mesh.get_material_index()
            #mesh.set_material(0, mi_asset)

if __name__ == "__main__":
    main()  
