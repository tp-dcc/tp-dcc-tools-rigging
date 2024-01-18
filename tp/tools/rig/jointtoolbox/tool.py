from __future__ import annotations

import typing
from dataclasses import dataclass

from overrides import override

from tp.core import log, tool, dcc
from tp.common.qt import api as qt

from . import consts, hook

if typing.TYPE_CHECKING:
    from tp.common.plugin import PluginFactory
    from tp.core.managers.tools import ToolsManager

logger = log.rigLogger


@dataclass()
class AlignJointEvent:
    align_to_plane: bool
    primary_axis_vector: tuple[float, float, float]
    secondary_axis_vector: tuple[float, float, float]
    world_up_axis_vector: tuple[float, float, float]
    orient_children: bool


class JointToolBox(tool.Tool):

    id = consts.TOOL_ID
    creator = 'Tomi Poveda'
    ui_data = tool.UiData(label='Joint Toolbox')
    tags = ['joint', 'toolbox']

    alignJoint = qt.Signal(AlignJointEvent)

    def __init__(self, factory: PluginFactory, tools_manager: ToolsManager):
        super().__init__(factory, tools_manager)

        self._hook: hook.JointToolboxHook | None = None
        self._coplanar_meta = None
        self._main_widget: JointToolboxView | None = None

    @override
    def initialize_properties(self) -> list[tool.UiProperty]:
        return [
            tool.UiProperty(name='affect_children', value=1),
            tool.UiProperty(name='global_display_size', value=1),
            tool.UiProperty(name='joint_radius', value=1.0),
            tool.UiProperty(name='mirror', value=0),
            tool.UiProperty(name='rotate', value=0),
            tool.UiProperty(name='rotate_lra', value=0),
            tool.UiProperty(name='world_up', value=1),
            tool.UiProperty(name='primary_axis', value=0),
            tool.UiProperty(name='secondary_axis', value=1),
        ]

    @override
    def pre_content_setup(self):

        self._coplanar_meta = None

        if dcc.is_maya():
            from tp.tools.rig.jointtoolbox.maya import hook as maya_hook
            self._hook = maya_hook.MayaJointToolbox()
        else:
            self._hook = hook.JointToolboxHook()

        self.alignJoint.connect(self._hook.align_joint)

    @override
    def contents(self) -> list[qt.QWidget]:
        self._main_widget = JointToolboxView(self)
        return [self._main_widget]

    @override
    def post_content_setup(self):
        self._main_widget.setup_signals()

        self.update_widgets_from_properties()

    def align_joint(self, align_up: bool = True):
        """
        Aligns the selected joints in the scene.

        :param bool align_up: if True, joint will point the axis up; False will point down relative to the world axis.
        """

        primary_axis_vector = consts.AXIS_VECTORS[self.properties.primary_axis.value]

        if align_up:
            secondary_axis_vector = consts.AXIS_VECTORS[self.properties.secondary_axis.value]
        else:
            # Make secondary axis negative
            secondary_axis_vector = consts.AXIS_VECTORS[self.properties.secondary_axis.value + 3]

        world_up_axis = self.properties.world_up.value
        align_to_plane = True if world_up_axis == 4 else False
        world_up_axis_vector = consts.AXIS_VECTORS[world_up_axis]
        if self._coplanar_meta:
            if world_up_axis == 3:      # Get vector normal from coplanar arrow plane normal
                world_up_axis_vector = self._coplanar_meta.arrow_plane_normal()
                if not world_up_axis_vector:
                    logger.warning('No arrow plane found, please create one.')
                    return
                world_up_axis_vector = tuple(world_up_axis_vector)

        event = AlignJointEvent(
            align_to_plane=align_to_plane, primary_axis_vector=primary_axis_vector,
            secondary_axis_vector=secondary_axis_vector, world_up_axis_vector=world_up_axis_vector,
            orient_children=bool(self.properties.affect_children))
        self._signals.alignJoint.emit(event)


class JointToolboxView(qt.QWidget):
    def __init__(self, tool_instance: JointToolBox, parent: qt.QWidget | None = None):
        super().__init__(parent=parent)

        self._tool = tool_instance

        self._select_radio_widget: qt.RadioButtonGroup | None = None
        self._primary_axis_combo: qt.ComboBoxRegularWidget | None = None
        self._secondary_axis_combo: qt.ComboBoxRegularWidget | None = None
        self._world_up_axis_combo: qt.ComboBoxRegularWidget | None = None
        self._start_end_arrow_chain_button: qt.LeftAlignedButton | None = None
        self._start_end_chain_button: qt.LeftAlignedButton | None = None
        self._select_plane_arrow_ctrl_button: qt.LeftAlignedButton | None = None
        self._orient_y_pos_button: qt.LeftAlignedButton | None = None
        self._orient_y_neg_button: qt.LeftAlignedButton | None = None

        self.setup_widgets()
        self.setup_layouts()
        self.link_properties()

    @property
    def tool(self) -> JointToolBox:
        """
        Getter method that returns tool instance.

        :return: tool instance.
        :rtype: JointToolBox
        """

        return self._tool

    def setup_widgets(self):
        """
        Function that setup widgets.
        """

        radio_names = ['Selected', 'Hierarchy']
        radio_tooltips = ['Affects only selected joints.', 'Affects selected joints and all of child joints.']
        self._select_radio_widget = qt.RadioButtonGroup(
            radio_names=radio_names, tooltips=radio_tooltips,
            margins=(qt.consts.SUPER_LARGE_SPACING_2, 0, qt.consts.SUPER_LARGE_SPACING_2, 0),
            spacing=qt.consts.SUPER_EXTRA_LARGE_SPACING, parent=self)

        tooltip = 'Set the primary axis, which is the axis that the joints will aim towards their children.'
        self._primary_axis_combo = qt.ComboBoxRegularWidget(
            label='Aim Axis', items=consts.XYZ_WITH_NEG_LIST, set_index=0, tooltip=tooltip, parent=self)

        tooltip = 'Set the secondary axis, which is the axis the joints roll towards relative to the "World Up" ' \
                  'settings.\nTo set the roll axis to the negative, press the down button (below).'
        self._secondary_axis_combo = qt.ComboBoxRegularWidget(
            label='Roll Up', items=consts.XYZ_LIST, set_index=1, tooltip=tooltip, parent=self)

        tooltip = 'The world up axis to use when orienting joints.\n\n' \
                  '   - X: Up axis points to the side (right) in world coordinates.\n' \
                  '   - Y: Up axis points to up in world coordinates.\n' \
                  '   - Z: Up axis points to the front in world coordinates.\n' \
                  '   - Plane: Builds a plane control for both orient and position snapping.'
        self._world_up_axis_combo = qt.ComboBoxRegularWidget(
            label='World Up', items=consts.XYZ_LIST + ['Up Ctrl', 'Plane'], set_index=1, tooltip=tooltip, parent=self)

        tooltip = 'Select a start and end joint to position and orient the plane/arrow control along a joint chain.\n' \
                  'The automatic start/end positioning should find the most accurate up direction for the joints.\n' \
                  'Right-click for more options, including setting the plane to a given world axis.'
        self._start_end_arrow_chain_button = qt.left_aligned_button(
            'Position Ctrl (Right Click)', icon='exit', tooltip=tooltip, parent=self)
        self._start_end_chain_button = qt.left_aligned_button(
            'Position Ctrl (Right-Click)', icon='plane', tooltip=tooltip, parent=self)

        tooltip = 'Select the "Up Arrow/Plane Control" in the scene.'
        self._select_plane_arrow_ctrl_button = qt.left_aligned_button(
            'Select Control', icon='cursor', tooltip=tooltip, parent=self)

        tooltip = 'Orient joints so that the roll axis orient "up" as per the "World Up" setting.\n' \
                  'The "Aim Axis" will aim toward the child joint, or if None exists, from its parent.\n\n' \
                  'World Up set to "Up Ctrl": Joint roll will orient in the direction of the arrow control.\n' \
                  'World Up set to "Plane": Joints will both orient and position-snap to the plane control.\n\n' \
                  'Select joints to orient (and or position) and run.'
        self._orient_y_pos_button = qt.left_aligned_button(
            'Orient Roll +Y (Aim X)', icon='arrow_up', tooltip=tooltip, parent=self)

        tooltip = 'Orient joints so that the roll axis orient "down" as per the "World Up" setting.\n' \
                  'The "Aim Axis" will aim toward the child joint, or if None exists, from its parent.\n\n' \
                  'World Up set to "Up Ctrl": Joint roll will orient in the direction of the arrow control.\n' \
                  'World Up set to "Plane": Joints will both orient and position-snap to the plane control.\n\n' \
                  'Select joints to orient (and or position) and run.'
        self._orient_y_neg_button = qt.left_aligned_button(
            'Orient Roll -Y (Aim X)', icon='arrow_down', tooltip=tooltip, parent=self)

    def setup_layouts(self):
        """
        Function that creates all UI layouts and add all widgets to them.
        """

        contents_layout = qt.vertical_layout(
            margins=(
                qt.consts.WINDOW_SIDE_PADDING, qt.consts.WINDOW_BOTTOM_PADDING,
                qt.consts.WINDOW_SIDE_PADDING, qt.consts.WINDOW_BOTTOM_PADDING),
            spacing=qt.consts.SPACING, parent=self)
        self.setLayout(contents_layout)

        axis_layout = qt.horizontal_layout(
            margins=(qt.consts.SMALL_SPACING, qt.consts.SMALL_SPACING, qt.consts.SMALL_SPACING, 0),
            spacing=qt.consts.SUPER_EXTRA_LARGE_SPACING)
        axis_layout.addWidget(self._primary_axis_combo, 5)
        axis_layout.addWidget(self._secondary_axis_combo, 5)
        axis_layout.addWidget(self._world_up_axis_combo, 5)

        control_layout = qt.horizontal_layout(margins=(0, 0, 0, 0), spacing=qt.consts.SPACING)
        control_layout.addWidget(self._start_end_arrow_chain_button)
        control_layout.addWidget(self._start_end_chain_button)
        control_layout.addWidget(self._select_plane_arrow_ctrl_button)

        orient_layout = qt.horizontal_layout(margins=(0, 0, 0, 0), spacing=qt.consts.SPACING)
        orient_layout.addWidget(self._orient_y_pos_button)
        orient_layout.addWidget(self._orient_y_neg_button)

        contents_layout.addWidget(self._select_radio_widget)
        contents_layout.addLayout(axis_layout)
        contents_layout.addLayout(control_layout)
        contents_layout.addLayout(orient_layout)

        contents_layout.addStretch()

    def link_properties(self):
        """
        Function that link between UI widgets and tool UI properties.
        """

        self.tool.link_property(self._select_radio_widget, 'affect_children')
        self.tool.link_property(self._primary_axis_combo, 'primary_axis')
        self.tool.link_property(self._secondary_axis_combo, 'secondary_axis')
        self.tool.link_property(self._world_up_axis_combo, 'world_up')

    def setup_signals(self):
        """
        Function that creates all the signal connections for all the widgets contained within this UI.
        """

        self._primary_axis_combo.currentIndexChanged.connect(self._on_primary_axis_combo_current_index_changed)
        self._orient_y_pos_button.clicked.connect(self.tool.align_joint)

    def _on_primary_axis_combo_current_index_changed(self):
        """
        Internal callback function that is called each time primary axis combobox index is changed by the user.
        """

        aim_index = self.tool.properties.primary_axis.value
        roll_up_index = self.tool.properties.secondary_axis.value
        if aim_index == roll_up_index:
            if roll_up_index == 1:
                self.tool.properties.secondary_axis.value = 2      # If Y, make Z
            else:
                self.tool.properties.secondary_axis.value = 1      # If Z or X, make Y

        self.tool.properties.rotate.value = aim_index

        self.tool.update_widgets_from_properties()
