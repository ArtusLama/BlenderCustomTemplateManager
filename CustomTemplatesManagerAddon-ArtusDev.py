import bpy
import re
import os

bl_info = {
    "name": "Custom Template Manager",
    "description": "Create and delete custom startup templates with one click",
    "author": "ArtusDev",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "File > Templates",
    "doc_url": "https://artuslama.github.io",
    "category": "User Interface"
}


# - - - - - - - Utils - - - - - - -
user_config_dir = bpy.utils.user_resource("SCRIPTS")
templates_folder = os.path.join(user_config_dir, "startup", "bl_app_templates_user")

def get_templates_folder() -> str:
    if not os.path.exists(templates_folder):
        os.makedirs(templates_folder)
    return templates_folder

get_templates_folder()


def validate_template_name(name: str) -> str:
    if not name:
        return "Template name cannot be empty"
    if re.fullmatch(r'[a-zA-Z0-9_\- ]*', name) is None:
        return "Invalid name characters!"
    if name in get_all_templates():
        return "Template already exists!"
    return None

def get_all_templates() -> list[str]:
    return os.listdir(get_templates_folder())
    
def save_current_file_as_template(name: str) -> None:
    target_dir = os.path.join(get_templates_folder(), name)
    os.mkdir(target_dir)
    target_dir = os.path.join(target_dir, "startup.blend")
    bpy.ops.wm.save_as_mainfile(filepath=target_dir, copy=True)

def delete_template(name: str) -> None:
    target_dir = os.path.join(get_templates_folder(), name)
    os.remove(os.path.join(target_dir, "startup.blend"))
    os.rmdir(target_dir)

# - - - - - - - - - - - - - - - - -



# - - - - - - Classes - - - - - - -
class CTM_MT_TemplatesMenu(bpy.types.Menu):
    icon = "FILE_BLEND"
    bl_label = "Templates"
    bl_idname = "ctm_MT_templates"

    def draw(self, context):
        layout = self.layout
        layout.operator(CTM_OT_SaveAsTemplate.bl_idname, text=CTM_OT_SaveAsTemplate.bl_label, icon=CTM_OT_SaveAsTemplate.icon)
        layout.menu(CTM_MT_DeleteTemplate.bl_idname, text=CTM_MT_DeleteTemplate.bl_label, icon=CTM_MT_DeleteTemplate.icon)

class CTM_MT_DeleteTemplate(bpy.types.Menu):
    icon = "CANCEL"
    bl_label = "Remove Template"
    bl_idname = "ctm_MT_removetemplates"

    def draw(self, context):
        layout = self.layout
        templates = get_all_templates()
        for template in templates:
            op = layout.operator(CTM_OT_DeleteTemplateItem.bl_idname, text=template, icon="X")
            op.template_name = template
            
        
        
        
        
class CTM_OT_SaveAsTemplate(bpy.types.Operator):
    icon = "FILE_NEW"
    bl_idname = "wm.save_as_template"
    bl_label = "Save As Template"
    bl_description = "Saves the current file as a new startup template"
    
    template_name: bpy.props.StringProperty(
        name="Template Name", 
        description="Name of the new template",
        default="New Template",
    ) # type: ignore
    
    def execute(self, context):
        validation_error = validate_template_name(self.template_name)
        if validation_error:
            self.report({ "ERROR" }, validation_error)
            return { "CANCELLED" }
            
        save_current_file_as_template(self.template_name)
     
        self.report({ "INFO" }, "Saved Template: " + self.template_name)
        return { "FINISHED" }
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "template_name", text="Name")
        
        validation_error =  validate_template_name(self.template_name)
        if validation_error:
            layout.label(text=validation_error, icon="ERROR")
            layout.alert = True

    

class CTM_OT_DeleteTemplateItem(bpy.types.Operator):
    bl_idname = "wm.delete_template"
    bl_label = ""
    bl_description = "Click to delete this template"
    
    template_name: bpy.props.StringProperty(
        name="template_name",
        default="",
    ) # type: ignore
    
    def execute(self, context):

        delete_template(self.template_name)
     
        self.report({ "INFO" }, "Removed Template")
        return { "FINISHED" }
# - - - - - - - - - - - - - - - - -



# - - - - - Registration - - - - - -
def draw_file_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(CTM_MT_TemplatesMenu.bl_idname, text=CTM_MT_TemplatesMenu.bl_label, icon=CTM_MT_TemplatesMenu.icon)



classes = [CTM_MT_TemplatesMenu, CTM_OT_SaveAsTemplate, CTM_MT_DeleteTemplate, CTM_OT_DeleteTemplateItem]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    if not bpy.app.background:
        bpy.types.TOPBAR_MT_file.append(draw_file_menu)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    if not bpy.app.background:
        bpy.types.TOPBAR_MT_file.remove(draw_file_menu)
    
    
# - - - - - - - - - - - - - - - - -



# - - - - - Entry Point - - - - - -
if __name__ == "__main__":
    register()
# - - - - - - - - - - - - - - - - -