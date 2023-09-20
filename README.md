# A3D-HRC-Maya-Script
This is a .py that exports the relevant information from the maya scene to a JSON file.

# What you will need:

Autodesk Maya 2022 is required to run the script.

PD_tool is required to convert the generated JSON to an A3DA.

Noesis (in some special cases, this is explained below).

# How to use:

Create a maya scene and load your animation IT IS IMPORTANT TO DELETE ALL THE MESHES IF THERE ARE ANY.

In the main menu bar, select Windows > Settings/Preferences > Plug-in Manager and click "Browse" then search for the .py.

The export process may take some time depending on how long the animation is.

# Credits:

korenkonder for the JSON layout and PD Tool.

ThisisHH and some friends for helping me and giving me some ideas.

# Notes:

This script only works with a node hierarchy, if your animation has an armature, I highly recommend opening your animation on noesis and exporting it as a .FBX, this may solve some issues related to the script not supporting this and refusing to export the animation. Then just re-open it again on Maya.

If you find any issue, please contact me on my discord (gilda.) Any feedback is appreciated!
