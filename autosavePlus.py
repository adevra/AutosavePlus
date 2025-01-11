import maya.cmds as cmds
import os
import json
import time
import platform
import subprocess
import sys
import random

autosave_running = False
last_save_time = 0.0
last_prompt_time = 0.0
in_prompt = False
last_countdown_msg_time = 0.0

START_BUTTON_NAME = "startAutosaveButton"
preferences_file = os.path.join(cmds.internalVar(userAppDir=True), "autosavePlus_preferences.json")

def load_preferences():
    if os.path.exists(preferences_file):
        with open(preferences_file, "r") as f:
            preferences = json.load(f)
        preferences.setdefault("interval", 15)
        preferences.setdefault("save_location", "")
        preferences.setdefault("save_next_to_scene", True)
        preferences.setdefault("prompt_before_save", False)
        preferences.setdefault("disable_in_playback", False)
        return preferences
    return {
        "interval": 15,
        "save_location": "",
        "save_next_to_scene": True,
        "prompt_before_save": False,
        "disable_in_playback": False,
    }

def save_preferences(preferences):
    with open(preferences_file, "w") as f:
        json.dump(preferences, f)
    display_message("Preferences saved successfully.")

def display_message(msg):
    cmds.inViewMessage(amg=msg, pos="botLeft", fade=True)

def display_countdown_message(msg):
    cmds.inViewMessage(
        amg=f'<span style="color:#00FF00">{msg}</span>',
        pos="botLeft",
        fade=True
    )

def get_autosave_directory():
    preferences = load_preferences()
    if preferences["save_next_to_scene"]:
        current_file_path = cmds.file(q=True, sceneName=True)
        if current_file_path:
            return os.path.dirname(current_file_path)
        return cmds.workspace(q=True, rd=True)
    else:
        return preferences["save_location"]

def incremental_save():
    current_file_path = cmds.file(q=True, sceneName=True)
    if not current_file_path:
        display_message("No scene file is currently open. Skipping save.")
        return
    save_directory = get_autosave_directory()
    if not os.path.exists(save_directory):
        display_message(f"Save location does not exist: {save_directory}")
        return
    base_name, file_extension = os.path.splitext(os.path.basename(current_file_path))
    autosave_files = [
        f for f in os.listdir(save_directory)
        if f.startswith(f"{base_name}_autosave_") and f.endswith(file_extension)
    ]
    autosave_files = sorted(autosave_files)
    next_index = len(autosave_files) + 1
    autosave_name = f"{base_name}_autosave_{next_index:03}{file_extension}"
    autosave_path = os.path.join(save_directory, autosave_name)
    original_scene_name = cmds.file(q=True, sceneName=True)
    try:
        cmds.file(rename=autosave_path)
        file_type = cmds.file(q=True, type=True)
        if file_type:
            cmds.file(save=True, type=file_type[0])
        else:
            cmds.file(save=True)
        display_message(f"Autosave created: {autosave_path}")
    finally:
        cmds.file(rename=original_scene_name)

def check_autosave():
    global last_save_time, last_prompt_time, in_prompt, last_countdown_msg_time
    if not autosave_running:
        return
    preferences = load_preferences()
    if preferences.get("disable_in_playback", False):
        if cmds.play(q=True, state=True):
            return
    interval_seconds = preferences["interval"] * 60
    now = time.time()
    time_since_last = now - last_save_time
    if time_since_last < interval_seconds:
        time_left = interval_seconds - time_since_last
        if time_left <= 5:
            if (now - last_countdown_msg_time) >= 1.0:
                display_countdown_message(f"Next Autosave in: {int(time_left)}s")
                last_countdown_msg_time = now
        return
    if (now - last_prompt_time) < 1.0:
        return
    last_prompt_time = now
    last_save_time = now
    if preferences["prompt_before_save"]:
        if in_prompt:
            return
        in_prompt = True
        result = cmds.confirmDialog(
            title="Autosave Prompt",
            message="Do you want to proceed with Autosave?",
            button=["Yes", "No"],
            defaultButton="Yes",
            cancelButton="No",
            dismissString="No"
        )
        in_prompt = False
        if result == "Yes":
            incremental_save()
    else:
        incremental_save()

def schedule_autosave():
    if not autosave_running:
        return
    check_autosave()
    cmds.evalDeferred(schedule_autosave, lowestPriority=True)

def start_autosave_job():
    global autosave_running, last_save_time, last_prompt_time, last_countdown_msg_time
    if autosave_running:
        display_message("Autosave+ is already running.")
        return
    autosave_running = True
    now = time.time()
    last_save_time = now
    last_prompt_time = now
    last_countdown_msg_time = 0.0
    display_message("Autosave+ started.")
    _disable_start_button()
    schedule_autosave()

def stop_autosave_job():
    global autosave_running
    if not autosave_running:
        display_message("Autosave+ is not running.")
        return
    autosave_running = False
    display_message("Autosave+ stopped.")
    _enable_start_button()

def _disable_start_button():
    if cmds.window("incrementalSaveUI", exists=True):
        if cmds.button(START_BUTTON_NAME, exists=True):
            cmds.button(START_BUTTON_NAME, edit=True, enable=False)

def _enable_start_button():
    def _do_enable():
        if cmds.window("incrementalSaveUI", exists=True):
            if cmds.button(START_BUTTON_NAME, exists=True):
                cmds.button(START_BUTTON_NAME, edit=True, enable=True)
    cmds.evalDeferred(_do_enable)

def display_inview_message(message_text, color="#FFFFFF", underline=False, 
                           position="botLeft", fade=True, alpha=0.3):
    message = f"<{random.random()}><span style=\"color:{color};"
    if underline:
        message += "text-decoration:underline;"
    message += f"\">{message_text}</span>"
    cmds.inViewMessage(amg=message, pos=position, fade=fade, alpha=alpha)

def get_clean_autosave_path():
    return get_autosave_directory()

def get_autosave_info():
    autosave_dir = get_clean_autosave_path()
    if not os.path.isdir(autosave_dir):
        return 0, 0.0
    files = [f for f in os.listdir(autosave_dir) 
             if os.path.isfile(os.path.join(autosave_dir, f))]
    total_size = sum(os.path.getsize(os.path.join(autosave_dir, f)) for f in files)
    return len(files), total_size / (1024 * 1024)

def update_clean_ui():
    file_count, total_size = get_autosave_info()
    cmds.text(labelCount, edit=True, label=f"Autosave Files: {file_count}")
    cmds.text(labelSize, edit=True, label=f"Total Size: {total_size:.2f} MB")

def clean_autosaves(*_):
    autosave_dir = get_clean_autosave_path()
    if not os.path.isdir(autosave_dir):
        cmds.warning("Autosave directory not found.")
        display_inview_message("Autosave directory not found.", color="#FF0000")
        return
    for f in os.listdir(autosave_dir):
        file_path = os.path.join(autosave_dir, f)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                cmds.warning(f"Error removing {file_path}: {e}")
    cmds.confirmDialog(
        title='Cleanup Complete',
        message='Autosave files have been deleted.',
        button=['OK']
    )
    display_inview_message("Autosave files deleted.", color="#00FF00")
    update_clean_ui()

def show_in_explorer(*_):
    autosave_dir = get_clean_autosave_path()
    if not os.path.exists(autosave_dir):
        cmds.warning(f"The autosave directory does not exist: {autosave_dir}")
        display_inview_message("Autosave directory not found.", color="#FF0000")
        return
    if sys.platform == "win32":
        try:
            os.startfile(autosave_dir)
            display_inview_message("Opened in Explorer.", color="#00FF00")
        except Exception as e:
            cmds.warning(f"Failed to open the directory: {e}")
            display_inview_message("Error opening directory.", color="#FF0000")
    elif sys.platform == "darwin":
        try:
            subprocess.check_call(['open', autosave_dir])
            display_inview_message("Opened in Finder.", color="#00FF00")
        except subprocess.CalledProcessError as e:
            cmds.warning(f"Failed to open the directory: {e}")
            display_inview_message("Error opening directory.", color="#FF0000")
    else:
        cmds.warning("This feature is not supported on your operating system.")
        display_inview_message("Unsupported OS for this feature.", color="#FF0000")

def close_clean_window(*_):
    if cmds.window("autosaveWindow", exists=True):
        cmds.deleteUI("autosaveWindow", window=True)
    display_inview_message("Autosave Manager closed.", color="#FFFF00")

def show_clean_autosaves_ui(*_):
    global labelCount, labelSize
    if cmds.window("autosaveWindow", exists=True):
        cmds.deleteUI("autosaveWindow", window=True)
    cmds.window("autosaveWindow", title="Autosave Manager", widthHeight=(250, 130), titleBar=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    labelCount = cmds.text(label="Calculating...")
    labelSize = cmds.text(label="Calculating...")
    cmds.button(label="Clean Autosaves", command=clean_autosaves)
    cmds.button(label="Show in Explorer", command=show_in_explorer)
    cmds.button(label="Close", command=close_clean_window)
    cmds.showWindow("autosaveWindow")
    update_clean_ui()

def open_autosave_folder():
    autosave_dir = get_autosave_directory()
    if not os.path.exists(autosave_dir):
        display_message("The specified folder does not exist.")
        return
    system = platform.system()
    if system == "Windows":
        os.startfile(autosave_dir)
    elif system == "Darwin":
        subprocess.call(["open", autosave_dir])
    elif system == "Linux":
        subprocess.call(["xdg-open", autosave_dir])
    else:
        display_message("Unsupported operating system. Cannot open folder.")

def show_about_dialog():
    cmds.confirmDialog(
        title="About Autosaave+",
        message=(
            "Usage Instructions:\n\n"
            "Please disable Maya's native autosaves in preferences"
            "1. Set the interval and other preferences.\n"
            "2. Click 'Start Autosave+' to begin.\n"
            "3. Click 'Stop Autosave+' to stop.\n"
            "4. 'Clean Autosaves' opens a tool to remove or open autosave files.\n\n"
            "Features:\n"
            "- Countdown shown only in last 5 seconds, in green\n"
            "- Disable autosaving in playback\n"
            "- Prompt before save\n\n"
            "Visit https://blog.anildevran.com for more info."
        ),
        button=["Close"],
        defaultButton="Close"
    )

def save_preferences_callback(interval, save_next_to_scene, save_location,
                              prompt_before_save, disable_in_playback):
    prefs = {
        "interval": int(interval),
        "save_next_to_scene": save_next_to_scene,
        "save_location": save_location,
        "prompt_before_save": prompt_before_save,
        "disable_in_playback": disable_in_playback,
    }
    save_preferences(prefs)

def show_incremental_save_ui():
    global autosave_running
    if cmds.window("incrementalSaveUI", exists=True):
        cmds.deleteUI("incrementalSaveUI")
    window = cmds.window("incrementalSaveUI", title="Autosave+", widthHeight=(350, 400))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    preferences = load_preferences()
    cmds.text(label="Autosave Interval (minutes):")
    interval_field = cmds.intField(value=preferences["interval"])
    save_next_to_scene_cb = cmds.checkBoxGrp(
        label="Save next to scene file:",
        value1=preferences["save_next_to_scene"]
    )
    location_field = cmds.textField(
        text=preferences["save_location"],
        editable=not preferences["save_next_to_scene"]
    )
    def browse_location(_):
        folder = cmds.fileDialog2(dialogStyle=2, fileMode=3)
        if folder:
            cmds.textField(location_field, edit=True, text=folder[0])
            cmds.checkBoxGrp(save_next_to_scene_cb, edit=True, value1=False)
    cmds.button(label="Browse", command=browse_location)
    def toggle_save_location(*_):
        next_to_scene = cmds.checkBoxGrp(save_next_to_scene_cb, query=True, value1=True)
        cmds.textField(location_field, edit=True, editable=not next_to_scene)
    cmds.checkBoxGrp(save_next_to_scene_cb, edit=True, changeCommand=toggle_save_location)
    prompt_before_save_cb = cmds.checkBoxGrp(
        label="Prompt before save:",
        value1=preferences["prompt_before_save"]
    )
    disable_in_playback_cb = cmds.checkBoxGrp(
        label="Disable Autosave in Playback:",
        value1=preferences["disable_in_playback"]
    )
    cmds.separator(height=10, style="double")
    cmds.button(
        START_BUTTON_NAME,
        label="Start Autosave+",
        command=lambda _: start_autosave_job(),
        enable=not autosave_running
    )
    cmds.button(label="Stop Autosave+", command=lambda _: stop_autosave_job())
    cmds.separator(height=10, style="double")
    cmds.button(
        label="Save Preferences",
        command=lambda _: save_preferences_callback(
            cmds.intField(interval_field, query=True, value=True),
            cmds.checkBoxGrp(save_next_to_scene_cb, query=True, value1=True),
            cmds.textField(location_field, query=True, text=True),
            cmds.checkBoxGrp(prompt_before_save_cb, query=True, value1=True),
            cmds.checkBoxGrp(disable_in_playback_cb, query=True, value1=True),
        ),
    )
    cmds.button(label="Clean Autosaves", command=show_clean_autosaves_ui)
    cmds.button(label="Open Autosave Folder", command=lambda _: open_autosave_folder())
    cmds.button(label="About", command=lambda _: show_about_dialog())
    cmds.showWindow(window)
    toggle_save_location()
    if autosave_running:
        cmds.button(START_BUTTON_NAME, edit=True, enable=False)
        display_message("Autosave+ is already running.")

if not autosave_running:
    start_autosave_job()
