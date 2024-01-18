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
