from __future__ import annotations

import enum

TOOL_ID = 'tp.rig.jointtoolbox'

XYZ_LIST = ['X', 'Y', 'Z']
XYZ_WITH_NEG_LIST = ['X', 'Y', 'Z', '-X', '-Y', '-Z']
AXIS_VECTORS = [
    (1.0, 0.0, 0.0),    # X
    (0.0, 1.0, 0.0),    # Y
    (0.0, 0.0, 1.0),    # Z
    (-1.0, 0.0, 0.0),   # -X
    (0.0, -1.0, 0.0),   # -Y
    (0.0, 0.0, -1.0)    # -Z
]


class JointDrawMode(enum.Enum):
    Bone = enum.auto()
    Hide = enum.auto()
    Joint = enum.auto()
    MultiBoxChild = enum.auto()


RADIO_TOOLTIPS = ['Affects only selected joints.', 'Affects selected joints and all of child joints.']
PRIMARY_AXIS_COMBO_TOOLTIP = 'Set the primary axis, which is the axis that the joints will aim towards their children.'
SECONDARY_AXIS_COMBO_TOOLTIP = """
Set the secondary axis, which is the axis the joints roll towards relative to the "World Up" settings.
To set the roll axis to the negative, press the down button (below)."""
WORLD_UP_AXIS_COMBO_TOOLTIP = """
The world up axis to use when orienting joints.

    - X: Up axis points to the side (right) in world coordinates.
    - Y: Up axis points to up in world coordinates.
    - Z: Up axis points to the front in world coordinates.
    - Plane: Builds a plane control for both orient and position snapping."""
START_END_ARROW_CHAIN_BUTTON_TOOLTIP = """
Select a start and end joint to position and orient the plane/arrow control along a joint chain.
The automatic start/end positioning should find the most accurate up direction for the joints.
Right-click for more options, including setting the plane to a given world axis."""
SELECT_PLANE_ARROW_CONTROL_BUTTON_TOOLTIP = 'Select the "Up Arrow/Plane Control" in the scene.'
ORIENT_Y_POSITIVE_BUTTON_TOOLTIP = """
Orient joints so that the roll axis orient "up" as per the "World Up" setting.
The "Aim Axis" will aim toward the child joint, or if None exists, from its parent.

World Up set to "Up Ctrl": Joint roll will orient in the direction of the arrow control.
World Up set to "Plane": Joints will both orient and position-snap to the plane control.

Select joints to orient (and or position) and run."""
ORIENT_Y_NEGATIVE_BUTTON_TOOLTIP = """
Orient joints so that the roll axis orient "down" as per the "World Up" setting.
The "Aim Axis" will aim toward the child joint, or if None exists, from its parent.

World Up set to "Up Ctrl": Joint roll will orient in the direction of the arrow control.
World Up set to "Plane": Joints will both orient and position-snap to the plane control.

Select joints to orient (and or position) and run."""
EDIT_LRA_BUTTON_TOOLTIP = """
Enter component mode and make the local rotation axis selectable, so that manipulators can be manually rotated"""
EXIT_LRA_BUTTON_TOOLTIP = """
Exit component mode into object mode and turns off the local rotation axis selectability.
Note: To b safe always run Zero Rotation Axis after existing LRA mode."""
ALIGN_PARENT_BUTTON_TOOLTIP = """
Align selected joint to its parent.
Useful for end joints that have no children to orient towards"""
ZERO_ROTATION_AXIS_BUTTON_TOOLTIP = """
After manually re-orienting a joint LRA, this button allows zero out joints rotation axis attributes.
This will keep the joint orientation predictable.
Note: This button should be pressed after exiting LRA mode if modifications have been made."""
ROTATE_COMBO_TOOLTIP = """
Rotate around the selected axis ("X", "Y", "Z')."""
ROTATE_LRA_TOOLTIP = """
Rotate the local rotation axis by this angle (in degrees)."""
ROTATE_LRA_BUTTON_TOOLTIP = """
Rotates the local rotation `roll axis` in degrees.

    - Slow (Ctrl + Left Click): 22.5 degrees.
    - Medium (Left Click): 45 degrees.
    - Fast (Shift + Left Click): 09 degrees.
"""
RESET_UI_BUTTON_TOOLTIP = """
Resets th `Orient UI Elements` to the default values."""
DRAW_BONE_BUTTON_TOOLTIP = """
Set 'Draw Style' joint attribute to be 'Bone', which is the default mode.
Joints will be visualized with bones and lines connecting if a hierarchy."""
DRAW_NONE_BUTTON_TOOLTIP = """
Set 'Draw Style' joint attribute to be 'None'.
Joints become hidden no matter the visibility settings."""
DRAW_JOINT_BUTTON_TOOLTIP = """
Set 'Draw Style' joint attribute to be 'Joint'.
Joints will be visualized with no connections between joints."""
DRAW_MULTI_CHILD_BOX_BUTTON_TOOLTIP = """
Set 'Draw Style' joint attribute to be 'Multi-Child Box'.
Joints with multiple children will be visualized as `boxes`, otherwise as `bones`."""
