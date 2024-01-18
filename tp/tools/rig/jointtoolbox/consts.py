from __future__ import annotations

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
