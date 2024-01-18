from __future__ import annotations

import typing

from tp.tools.rig.jointtoolbox import hook
from tp.libs.rig.jointtolbox.maya import api

if typing.TYPE_CHECKING:
    from tp.tools.rig.jointtoolbox.tool import AlignJointEvent


class MayaJointToolbox(hook.JointToolboxHook):

    def align_joint(self, event: AlignJointEvent):
        if not event.align_to_plane:
            api.align_selected_joints(
                primary_axis_vector=event.primary_axis_vector, secondary_axis_vector=event.secondary_axis_vector,
                world_up_axis_vector=event.world_up_axis_vector, orient_children=event.orient_children)
        else:
            raise NotImplementedError
