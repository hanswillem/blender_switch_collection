bl_info = {
    "name": "Collection Visibility Switch",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Tool Shelf > My Panel",
    "description": "Switches the visibility of two collections",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
}

import bpy

def frame_change_handler(scene):
    for item in scene.visibility_switch_collection:
        if item.collection1 and item.collection2:
            for obj in item.collection1.objects:
                obj.hide_viewport = item.switch
                obj.hide_render = item.switch
            for obj in item.collection2.objects:
                obj.hide_viewport = not item.switch
                obj.hide_render = not item.switch

def update_switch(self, context):
    if self.collection1 and self.collection2:
        for obj in self.collection1.objects:
            obj.hide_viewport = self.switch
            obj.hide_render = self.switch
        for obj in self.collection2.objects:
            obj.hide_viewport = not self.switch
            obj.hide_render = not self.switch
    context.view_layer.update()

class VisibilitySwitchItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
        default="My Switch",
    )
    collection1: bpy.props.PointerProperty(
        name="A",
        type=bpy.types.Collection,
    )
    collection2: bpy.props.PointerProperty(
        name="B",
        type=bpy.types.Collection,
    )
    switch: bpy.props.BoolProperty(
        name="Switch",
        default=False,
        update=update_switch,
    )

class VIEW3D_PT_visibility_switch_panel(bpy.types.Panel):
    bl_label = "Visibility Switch"
    bl_idname = "VIEW3D_PT_visibility_switch"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Visibility Switch'  # Tab name changed here

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        for idx, item in enumerate(scene.visibility_switch_collection):
            box = layout.box()
            row = box.row()
            row.prop(item, "name", text="")
            row = box.row()
            row.prop(item, "collection1", text="")
            row = box.row()
            row.prop(item, "collection2", text="")
            row = box.row()
            row.prop(item, "switch")
            remove_operator = box.operator('scene.remove_visibility_switch', text="Remove")
            remove_operator.idx = idx

        layout.operator('scene.add_visibility_switch')


class SCENE_OT_add_visibility_switch(bpy.types.Operator):
    bl_idname = "scene.add_visibility_switch"
    bl_label = "+"

    def execute(self, context):
        context.scene.visibility_switch_collection.add()
        return {'FINISHED'}

class SCENE_OT_remove_visibility_switch(bpy.types.Operator):
    bl_idname = "scene.remove_visibility_switch"
    bl_label = "Remove Visibility Switch"
    idx: bpy.props.IntProperty()

    def execute(self, context):
        item = context.scene.visibility_switch_collection[self.idx]
        if item.collection1 and item.collection2:
            for obj in item.collection1.objects:
                obj.hide_viewport = False
                obj.hide_render = False
            for obj in item.collection2.objects:
                obj.hide_viewport = False
                obj.hide_render = False
            context.view_layer.update()
        # Check if there are any keyframes on the switch property
        if context.scene.animation_data is not None and context.scene.animation_data.action is not None:
            for fcurve in context.scene.animation_data.action.fcurves:
                if fcurve.data_path == 'visibility_switch_collection[{}].switch'.format(self.idx):
                    fcurve.keyframe_points.clear()
        context.scene.visibility_switch_collection.remove(self.idx)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(VisibilitySwitchItem)
    bpy.types.Scene.visibility_switch_collection = bpy.props.CollectionProperty(type=VisibilitySwitchItem)

    bpy.utils.register_class(SCENE_OT_add_visibility_switch)
    bpy.utils.register_class(SCENE_OT_remove_visibility_switch)
    bpy.utils.register_class(VIEW3D_PT_visibility_switch_panel)

    bpy.app.handlers.frame_change_pre.append(frame_change_handler)

    # Add one switch setup on load
    bpy.context.scene.visibility_switch_collection.add()

def unregister():
    bpy.app.handlers.frame_change_pre.remove(frame_change_handler)

    bpy.utils.unregister_class(VIEW3D_PT_visibility_switch_panel)
    bpy.utils.unregister_class(SCENE_OT_remove_visibility_switch)
    bpy.utils.unregister_class(SCENE_OT_add_visibility_switch)

    del bpy.types.Scene.visibility_switch_collection
    bpy.utils.unregister_class(VisibilitySwitchItem)

if __name__ == "__main__":
    register()
