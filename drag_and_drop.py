import os
import maya.cmds as cmds

def onMayaDroppedPythonFile(*args):
    source_script = cmds.fileDialog2(
        dialogStyle=2, fileMode=1, caption="Select autosavePlus.py"
    )
    if not source_script:
        cmds.warning("No file selected. Operation canceled.")
        return
    source_script = source_script[0]
    if not source_script.endswith("autosavePlus.py"):
        cmds.warning("Invalid file selected. Please select autosavePlus.py.")
        return
    scripts_dir = cmds.internalVar(userScriptDir=True)
    destination_script = os.path.join(scripts_dir, "autosavePlus.py")
    try:
        with open(source_script, 'r') as src, open(destination_script, 'w') as dst:
            dst.write(src.read())
        cmds.inViewMessage(amg="autosavePlus.py installed successfully!", pos="midCenter", fade=True)
    except Exception as e:
        cmds.warning(f"Failed to copy autosavePlus.py: {e}")
        return
    try:
        active_shelf = cmds.tabLayout("ShelfLayout", query=True, selectTab=True)
        if not active_shelf:
            cmds.warning("No active shelf found!")
            return
        cmds.shelfButton(
            parent=active_shelf,
            command="import autosavePlus; autosavePlus.show_incremental_save_ui()",
            annotation="Open Autosave+ UI",
            label="ASV+",
            imageOverlayLabel="ASV+",
            image1="save.png",  
            enableBackground=False,
            backgroundColor=(0, 0, 0),
            highlightColor=(0.321569, 0.521569, 0.65098),
            align="center",
            labelOffset=0,
            rotation=0,
            flipX=False,
            flipY=False,
            useAlpha=True,
            overlayLabelColor=(1, 1, 1),
            overlayLabelBackColor=(0, 0, 0, 1),
            marginWidth=1,
            marginHeight=1,
        )
        cmds.inViewMessage(amg="Autosave+ button added to active shelf!", pos="midCenter", fade=True)
    except Exception as e:
        cmds.warning(f"Error adding shelf button: {e}")
