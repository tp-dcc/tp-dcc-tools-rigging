from __future__ import annotations

import typing

from tp.maya.cmds import decorators
from tp.maya.cmds.nodes import joints
from tp.tools.rig.jointtoolbox import hook
from tp.libs.rig.jointtolbox.maya import api

if typing.TYPE_CHECKING:
    from tp.tools.rig.jointtoolbox.tool import AlignJointEvent, ZeroRotationAxisEvent, RotateLraEvent


class MayaJointToolbox(hook.JointToolboxHook):

    @decorators.undo
    def align_joint(self, event: AlignJointEvent):
        """
        Aligns current selected joints in the scene.

        :param AlignJointEvent event: align joint event.
        """

        if not event.align_to_plane:
            api.align_selected_joints(
                primary_axis_vector=event.primary_axis_vector, secondary_axis_vector=event.secondary_axis_vector,
                world_up_axis_vector=event.world_up_axis_vector, orient_children=event.orient_children)
        else:
            raise NotImplementedError

    @decorators.undo
    def edit_lra(self):
        """
        Enters component mode, switch on edit local rotation axis and turns handle visibility on.
        """

        joints.edit_component_lra(True)

    @decorators.undo
    def exit_lra(self):
        """
        Exists component mode and turns off local rotation axis.
        """

        joints.edit_component_lra(False)

    @decorators.undo
    def align_to_parent(self):
        """
        Aligns selected joint to its parent.
        """

        joints.align_selected_joints_to_parent()

    @decorators.undo
    def zero_rotation_axis(self, event: ZeroRotationAxisEvent):
        """
        Zeroes out the rotation axis of the selected joints.

        :param ZeroRotationAxisEvent event: zero rotation axis event.
        """

        joints.zero_selected_joints_rotation_axis(zero_children=event.orient_children)

    @decorators.undo
    def rotate_lra(self, event: RotateLraEvent):
        """
        Rotates Local Rotate Axis of the selected joints.

        :param RotateLraEvent event: rotate local rotation axis event.
        """

        joints.rotate_selected_joints_local_rotation_axis(event.lra_rotation, include_children=event.orient_children)
