from __future__ import annotations

import typing

from tp.common.python import decorators

if typing.TYPE_CHECKING:
    from tp.tools.rig.jointtoolbox.tool import AlignJointEvent, ZeroRotationAxisEvent


class JointToolboxHook:

    @decorators.abstractmethod
    def align_joint(self, event: AlignJointEvent):
        """
        Aligns current selected joints in the scene.

        :param AlignJointEvent event: align joint event.
        """

        raise NotImplementedError

    @decorators.abstractmethod
    def edit_lra(self):
        """
        Enters component mode, switch on edit local rotation axis and turns handle visibility on.
        """

        raise NotImplementedError

    @decorators.abstractmethod
    def exit_lra(self):
        """
        Exists component mode and turns off local rotation axis.
        """

        raise NotImplementedError

    @decorators.abstractmethod
    def align_to_parent(self):
        """
        Aligns selected joint to its parent.
        """

        raise NotImplementedError

    @decorators.abstractmethod
    def zero_rotation_axis(self, event: ZeroRotationAxisEvent):
        """
        Zeroes out the rotation axis of the selected joints.
        
        :param ZeroRotationAxisEvent event: zero rotation axis event.
        """

        raise NotImplementedError
