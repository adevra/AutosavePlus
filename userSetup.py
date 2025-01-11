def start_autosave_plus():
    try:
        #Replace with your Autosave+ script path, (notice UNIX style forward slashes /)
        autosave_script_path = "C:/Users/yourUserName/Documents/maya/2022/scripts/autosavePlus.py"
        if os.path.exists(autosave_script_path):
            exec(open(autosave_script_path).read())
        else:
            cmds.warning("Autosave+ script not found!")
    except Exception as e:
        cmds.warning(f"Failed to start Autosave+: {e}")

cmds.evalDeferred(start_autosave_plus)
