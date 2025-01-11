![Autosave+](https://blog.anildevran.com/content/images/size/w800/format/webp/2025/01/maya_7VoLMHjoHD.png)
# Autosave+

Autosave+ is a simple but reliable autosaving tool for Autodesk Maya, designed to address some of the quirks and limitations of Maya's native autosave feature. It’s not a groundbreaking tool, but it can make your workflow a little smoother and help you avoid data loss when it matters most.

## Why Use Autosave+?

Maya’s built-in autosave is fine for basic use, but it has its limitations:
- It only saves the scene, ignoring important external files like `.xgen` data.
- It can interrupt your playback or workflow at inconvenient times.
- It doesn’t give you much control over how or where your files are saved.

Autosave+ improves on these areas by:
- **Saving Everything:** It does a full scene save, ensuring `.xgen` files and other dependencies are stored alongside your scene.
- **Pausing During Playback:** If you’re animating and there is a playback, autosaving automatically pauses untill playback finishes, avoiding Maya crashes.
- **Flexible Saving Options:** Save files next to your scene or in a custom folder. Whatever works best for your setup.

## Key Features

- **Incremental Saves:** Autosave+ creates uniquely named versions of your file, so you can easily track progress or roll back changes.
- **Customizable Preferences:** You can adjust the autosave interval, choose where files are saved, and even enable a prompt to confirm saves.
- **Playback-Aware:** It stays out of your way when the timeline is playing.
- **Built-In Cleanup Tools:** Find and manage old autosave files quickly from the interface.

## Installation

1. Download the `autosavePlus.py` script.
2. Drag and drop the `drag_and_drop.py` file into the Maya viewport.
3. Follow the prompts to locate and install `autosavePlus.py`.
4. A new "ASV+" button will appear on your active shelf. Click it to open the Autosave+ UI.

## How to Use

1. Disable Maya default autosave behavior from Maya>Preferences>Files/Projects
2. Open the UI from the shelf button.
3. Configure your preferences (like the save interval or location).
4. Click "Start Autosave+" to enable autosaving.
5. That’s it — your work will now be saved automatically at regular intervals.
6. Change autosave+ folder depending on your active project and hit Save Preferences.

## How to always run Autosave+ each time Maya initializes?
1. Go to your userSetup.py file (usually in maya/scripts/userSetup.py), if you don't have this file, create one yourself
2. Copy and paste [this code](https://github.com/adevra/AutosavePlus/blob/main/userSetup.py) into userSetup.py 


### Autosave+ was built with simplicity and practicality in mind. If you’ve ever been frustrated by Maya’s native autosave or lost work due to an overlooked dependency, this tool might be a small improvement to your workflow. 
Contributions, feedback, and suggestions are always welcome!
