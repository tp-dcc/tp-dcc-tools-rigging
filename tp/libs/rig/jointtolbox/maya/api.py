from __future__ import annotations

import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

from tp.core import log
from tp.maya import api
from tp.commands import maya
from tp.maya.cmds.nodes import joints

logger = log.rigLogger


def align_selected_joints(
        primary_axis_vector: tuple[float, float, float] = (1.0, 0.0, 0.0),
        secondary_axis_vector: tuple[float, float, float] = (0.0, 1.0, 0.0),
        world_up_axis_vector: tuple[float, float, float] = (0.0, 1.0, 0.0), orient_children: bool = False,
        ignore_connected_joints: bool = True, freeze_joints: bool = True, message: bool = True):
    """
    Aligns the world up of currently selected joints to be X, Y or Z based on given world up axis.

    :param int primary_axis_vector: aim primary axis vector.
    :param int secondary_axis_vector: up secondary axis vector.
    :param int world_up_axis_vector: world up axis vector.
    :param int orient_children: whether all child joints should be oriented.
    :param int ignore_connected_joints: whether to ignore joints that are connected
        (have constraints, locked or have keyframes).
    :param int freeze_joints: whether to freeze all joints after orienting them.
    :param bool message: whether report message to user.
    """

    selected_joints = cmds.ls(selection=True, long=True, exactType='joint')
    if not selected_joints:
        logger.warning('No joints selected. Please select some joints.')
        return

    align_joints(
        selected_joints, primary_axis_vector=primary_axis_vector, secondary_axis_vector=secondary_axis_vector,
        world_up_axis_vector=world_up_axis_vector, orient_children=orient_children,
        ignore_connected_joints=ignore_connected_joints, freeze_joints=freeze_joints, message=message)


def align_joints(
        joint_names: list[str], primary_axis_vector: tuple[float, float, float] = (1.0, 0.0, 0.0),
        secondary_axis_vector: tuple[float, float, float] = (0.0, 1.0, 0.0),
        world_up_axis_vector: tuple[float, float, float] = (0.0, 1.0, 0.0), orient_children: bool = False,
        ignore_connected_joints: bool = True, freeze_joints: bool = True, message: bool = True) -> bool:
    """
    Aligns the world up of given joints to be X, Y or Z based on given world up axis.

    :param list[str] joint_names: list of joint names.
    :param int primary_axis_vector: aim primary axis vector.
    :param int secondary_axis_vector: up secondary axis vector.
    :param int world_up_axis_vector: world up axis vector.
    :param int orient_children: whether all child joints should be oriented.
    :param int ignore_connected_joints: whether to ignore joints that are connected
        (have constraints, locked or have keyframes).
    :param int freeze_joints: whether to freeze all joints after orienting them.
    :param bool message: whether report message to user.
    :return: True if align joints operation was successful; False otherwise.
    :rtype: bool
    """

    success = False

    primary_axis_vector = OpenMaya.MVector(primary_axis_vector)
    secondary_axis_vector = OpenMaya.MVector(secondary_axis_vector)
    world_up_axis_vector = OpenMaya.MVector(world_up_axis_vector)

    if orient_children:
        new_joints = cmds.listRelatives(joint_names, allDescendents=True, type='joint', fullPath=True) or []
        joint_names.extend(new_joints)

    joint_chains, ignore_joints = joints.joint_chains(
        list(joint_names), ignore_connected_joints=ignore_connected_joints)
    for joint_chain in joint_chains:

        # Last joint in chain may have a child, and if so, include first found.
        skip_end = False
        children = cmds.listRelatives(joint_chain[-1], allDescendents=True, type='joint', fullPath=True)
        if children:
            joint_chain.append(children[0])
            skip_end = True

        nodes = list(api.nodes_by_names(joint_chain))
        maya.orient_nodes(nodes, primary_axis_vector, secondary_axis_vector, world_up_axis_vector, skip_end=skip_end)
        success = True

    if freeze_joints:
        for joint_chain in joint_chains:
            cmds.makeIdentity(joint_chain, apply=True, scale=True, rotate=True, translate=True)

    if message:
        pass

    return success
