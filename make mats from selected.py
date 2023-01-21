import unreal

def set_mi_texture(mi_asset, param_name, tex_path):
    if not unreal.EditorAssetLibrary.does_asset_exist(tex_path):
        unreal.log_warning("Can't find texture: " + tex_path)
        return False
    tex_asset = unreal.EditorAssetLibrary.find_asset_data( tex_path ).get_asset()
    return unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi_asset, param_name, tex_asset)


def main():
    unreal.log("-------------------CREATING MATERIAL INSTANCE--------------------------------")
    AssetTools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    MaterialEditingLibrary = unreal.MaterialEditingLibrary
    EditorAssetLibrary = unreal.EditorAssetLibrary

    base_mtl = unreal.EditorAssetLibrary.find_asset_data("/Game/Valorant/Characters/_Core/MasterMaterials/3P_Character_Mat_V5")
    sel_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    for texture in sel_assets:
        base_path = unreal.Paths.get_path(texture.get_path_name())
        tex_name = texture.get_name()
        mi_name = tex_name.replace('_DF', '_MI')
        mi_full_path = base_path + mi_name
        #Check if material instance already exists
        if EditorAssetLibrary.does_asset_exist(mi_full_path):
            mi_asset = EditorAssetLibrary.find_asset_data(mi_full_path).get_asset()
            unreal.log("Asset already exists")
        else:
            mi_asset = AssetTools.create_asset(mi_name, base_path, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        MaterialEditingLibrary.set_material_instance_parent( mi_asset, base_mtl.get_asset() )  # set parent material
        mrae_path = texture.get_path_name().replace('_DF', '_MRAE')
        normal_path = texture.get_path_name().replace('_DF', '_NM')
        set_mi_texture(mi_asset, 'Diffuse', texture.get_path_name())
        set_mi_texture(mi_asset, 'MRAE', mrae_path)       
        set_mi_texture(mi_asset, 'Normal', normal_path)

if __name__ == "__main__":
    main()  
