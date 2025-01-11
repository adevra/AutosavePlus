import maya.cmds as cmds
import os

def start_autosave_plus():
    try:
        #Replace this path, notice UNIX style forward slashes /
        autosave_script_path = "C:/Users/yourUserName/Documents/maya/2022/scripts/autosavePlus.py"
        if os.path.exists(autosave_script_path):
            with open(autosave_script_path, "r") as script_file:
                exec(script_file.read(), globals())  
            if "start_autosave_job" in globals():
                start_autosave_job()
            else:
                cmds.warning("Autosave+ script did not define 'start_autosave_job'.")
        else:
            cmds.warning("Autosave+ script not found!")
    except Exception as e:
        cmds.warning(f"Failed to start Autosave+: {e}")

cmds.evalDeferred(start_autosave_plus)
