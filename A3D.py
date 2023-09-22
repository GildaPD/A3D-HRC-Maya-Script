import os
import json
import maya.cmds as cmds
import math

# InputName
file_name = "A3D2"

# Maya Scene
frame_start = int(cmds.playbackOptions(q=True, min=True))
frame_end = int(cmds.playbackOptions(q=True, max=True))

# Obtén todos los nodos en la escena y excluye cámaras predeterminadas
all_nodes = cmds.ls(dag=True, long=True)
excluded_nodes = ["persp", "perspShape", "top", "front", "side", "perspShape", "topShape", "frontShape", "sideShape"]
relevant_nodes = [cmds.ls(node, shortNames=True)[0] for node in all_nodes if cmds.ls(node, shortNames=True)[0] not in excluded_nodes]

# Function to calculate relative head positions for the entire animation
def calculate_relative_head_positions(node_name):
    res = {"X": [], "Y": [], "Z": []}
    prev_frame = None
    prev_trans_x, prev_trans_y, prev_trans_z = None, None, None
    
    for frame in range(frame_start, frame_end + 1):
        cmds.currentTime(frame)

        # Get translation values in local coordinates
        trans_x = cmds.getAttr(f"{node_name}.translateX")
        trans_y = cmds.getAttr(f"{node_name}.translateY")
        trans_z = cmds.getAttr(f"{node_name}.translateZ")

        # Check for NaN values
        if not (math.isnan(trans_x) or math.isnan(trans_y) or math.isnan(trans_z)):
            # Check if this frame has the same translation values as the previous frame
            if (trans_x, trans_y, trans_z) != (prev_trans_x, prev_trans_y, prev_trans_z):
                # Store the relative head position for this frame
                res["X"].append(keys(frame, trans_x))
                res["Y"].append(keys(frame, trans_y))
                res["Z"].append(keys(frame, trans_z))

            prev_trans_x, prev_trans_y, prev_trans_z = trans_x, trans_y, trans_z

    return res

# Extract node rotation as Euler angles (XYZ order)
def get_node_rotation(node_name):
    res_euler = []
    prev_frame = None
    prev_rotation_euler = None
    
    for frame in range(frame_start, frame_end + 1):
        cmds.currentTime(frame)
        
        # Get rotation values in local coordinates (with respect to the parent)
        rotation_euler = cmds.xform(node_name, query=True, rotation=True, relative=True)
        rotation_euler = [math.radians(angle) for angle in rotation_euler]  # Convert to radians

        # Check for NaN values
        if not any(math.isnan(angle) for angle in rotation_euler):
            # Check if this frame has the same rotation values as the previous frame
            if rotation_euler != prev_rotation_euler:
                # Store the relative head rotation for this frame
                res_euler.append(keys(frame, rotation_euler))

            prev_rotation_euler = rotation_euler

    return res_euler

class keys:
    def __init__(self, frame, value):
        self.frame = frame
        self.value = value

# List all nodes in the scene
all_nodes = cmds.ls(dag=True)

# Generate node animation data for A3DA
node_animations = []
node_index_map = {}  # Dictionary to store the mapping of node names to node indices

for node_name in relevant_nodes:
    trans_data = calculate_relative_head_positions(node_name)
    trans_x = trans_data["X"]
    trans_y = trans_data["Y"]
    trans_z = trans_data["Z"]
    rot_euler = get_node_rotation(node_name)
    # Add node entry
    node_animation = {
        "Name": node_name,
        "Rot": {
            "X": {"Type": "Linear", "Keys": [[i.frame, i.value[0]] if not any(math.isnan(v) for v in i.value) else {"Type": "None"} for i in rot_euler]},
            "Y": {"Type": "Linear", "Keys": [[i.frame, i.value[1]] if not any(math.isnan(v) for v in i.value) else {"Type": "None"} for i in rot_euler]},
            "Z": {"Type": "Linear", "Keys": [[i.frame, i.value[2]] if not any(math.isnan(v) for v in i.value) else {"Type": "None"} for i in rot_euler]}
        },
        "Scale": {
            "X": {"Type": "Static", "Value": 1},
            "Y": {"Type": "Static", "Value": 1},
            "Z": {"Type": "Static", "Value": 1}
        },
        "Trans": {
            "X": {"Type": "Linear", "Keys": [[i.frame, i.value] if not math.isnan(i.value) else {"Type": "None"} for i in trans_x]},
            "Y": {"Type": "Linear", "Keys": [[i.frame, i.value] if not math.isnan(i.value) else {"Type": "None"} for i in trans_y]},
            "Z": {"Type": "Linear", "Keys": [[i.frame, i.value] if not math.isnan(i.value) else {"Type": "None"} for i in trans_z]}
        },
        "Visibility": {"Type": "Static", "Value": 1}
    }

    node_animations.append(node_animation)
    node_index_map[node_name] = len(node_animations)  # Store the index of the node

# Generate the parent-child relationships
for node_name in all_nodes:
    parent_node = cmds.listRelatives(node_name, parent=True)
    if parent_node:
        parent_node_name = cmds.ls(parent_node[0], shortNames=True)[0]
        if parent_node_name in node_index_map:
            parent_index = node_index_map[parent_node_name]
            node_index = node_index_map[node_name]
            node_animations[node_index - 1]["Parent"] = parent_index

# Convert tangent values to match DIVA format
for node_animation in node_animations:
    for transform_type in ["Rot", "Trans"]:
        for axis in ["X", "Y", "Z"]:
            key_list = node_animation[transform_type][axis]["Keys"]
            for i in range(1, len(key_list)):
                prev_key = key_list[i - 1]
                current_key = key_list[i]

                # Check if the previous key has enough elements to access the first tangent
                if len(prev_key) > 2:
                    # Check if the current_key has enough elements before modifying the third index
                    if len(current_key) > 2:
                        current_key[2] = prev_key[2]  # Set the second tangent to be the same as the first tangent of the previous keyframe
                    else:
                        current_key.append(prev_key[2])  # Add the second tangent from the previous keyframe
                else:
                    # If the previous key doesn't have enough elements, add the second tangent with a value of 0
                    prev_key.append(0)
                    current_key.insert(2, 0)

# A3DA base structure
A3DABase = {
    "A3D": {
        "_": {"ConverterVersion": "20050823", "FileName": "", "PropertyVersion": "20050706"},
        "ObjectHRC": [
            {
                "Name": "EFFCHRPV739MIK001_MOB",
                "UIDName": "EFFCHRPV739MIK001_MOB__DIVSKN",
                "Node": [
                    {
                        "Name": "OBJHRC_EFFCHRPV739MIK001_MOB",
                        "Parent": -1,
                        "Rot": {
                            "X": {"Type": "None"},
                            "Y": {"Type": "None"},
                            "Z": {"Type": "None"}
                        },
                        "Scale": {
                            "X": {"Type": "Static", "Value": 1},
                            "Y": {"Type": "Static", "Value": 1},
                            "Z": {"Type": "Static", "Value": 1}
                        },
                        "Trans": {
                            "X": {"Type": "None"},
                            "Y": {"Type": "None"},
                            "Z": {"Type": "None"}
                        },
                        "Visibility": {"Type": "Static", "Value": 1}
                    }
                ] + node_animations  # Concatenate the node animations
            }
        ],
        "ObjectHRCList": ["EFFCHRPV739MIK001_MOB"],
        "PlayControl": {"Begin": frame_start, "FPS": 60, "Size": frame_end - frame_start + 1}
    }
}

# Export A3DA data to JSON file
output_file_path = os.path.join(cmds.workspace(q=True, rd=True), f"{file_name}.json")
with open(output_file_path, 'w') as f:
    f.write(json.dumps(A3DABase, indent=2))

print(f"Animation data exported to: {output_file_path}")
