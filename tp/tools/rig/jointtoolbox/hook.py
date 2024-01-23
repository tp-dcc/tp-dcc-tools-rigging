from __future__ import annotations

import typing

from tp.common.python import decorators

if typing.TYPE_CHECKING:
    from tp.tools.rig.jointtoolbox.tool import (
        AlignJointEvent, ZeroRotationAxisEvent, RotateLraEvent, SetJointDrawModeEvent
    )


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

    @decorators.abstractmethod
    def rotate_lra(self, event: RotateLraEvent):
        """
        Rotates Local Rotate Axis of the selected joints.

        :param RotateLraEvent event: rotate local rotation axis event.
        """

        raise NotImplementedError

    @decorators.abstractmethod
    def set_draw_joint_mode(self, event: SetJointDrawModeEvent):
        """
        Sets the draw joint mode of the selected joints.

        :param SetJointDrawModeEvent event: set joint draw mode event.
        """

        raise NotImplementedError
