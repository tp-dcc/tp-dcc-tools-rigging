from __future__ import annotations

import typing

from tp.common.python import decorators

if typing.TYPE_CHECKING:
    from tp.tools.rig.jointtoolbox.tool import AlignJointEvent


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
