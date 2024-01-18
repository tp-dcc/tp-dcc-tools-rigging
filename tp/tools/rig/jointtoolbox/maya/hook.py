from __future__ import annotations

import typing

from tp.maya.cmds import decorators
from tp.maya.cmds.nodes import joints
from tp.tools.rig.jointtoolbox import hook
from tp.libs.rig.jointtolbox.maya import api

if typing.TYPE_CHECKING:
    from tp.tools.rig.jointtoolbox.tool import AlignJointEvent


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
