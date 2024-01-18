from __future__ import annotations

import typing
from functools import partial
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
    editLra = qt.Signal()
    exitLra = qt.Signal()

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
        self.editLra.connect(self._hook.edit_lra)
        self.exitLra.connect(self._hook.exit_lra)

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
        self.alignJoint.emit(event)

    def edit_lra(self):
        """
        Enters component mode, switch on edit local rotation axis and turns handle visibility on.
        """

        self.editLra.emit()

    def exit_lra(self):
        """
        Exists component mode and turns off local rotation axis.
        """

        self.exitLra.emit()


class JointToolboxView(qt.QWidget):
    def __init__(self, tool_instance: JointToolBox, parent: qt.QWidget | None = None):
        super().__init__(parent=parent)

        self._tool = tool_instance

        self._accordion: qt.AccordionWidget | None = None
        self._orient_widget: qt.QWidget | None = None
        self._select_radio_widget: qt.RadioButtonGroup | None = None
        self._primary_axis_combo: qt.ComboBoxRegularWidget | None = None
        self._secondary_axis_combo: qt.ComboBoxRegularWidget | None = None
        self._world_up_axis_combo: qt.ComboBoxRegularWidget | None = None
        self._start_end_arrow_chain_button: qt.LeftAlignedButton | None = None
        self._start_end_chain_button: qt.LeftAlignedButton | None = None
        self._select_plane_arrow_ctrl_button: qt.LeftAlignedButton | None = None
        self._orient_y_pos_button: qt.LeftAlignedButton | None = None
        self._orient_y_neg_button: qt.LeftAlignedButton | None = None
        self._edit_lra_button: qt.LeftAlignedButton | None = None
        self._exit_lra_button: qt.LeftAlignedButton | None = None
        self._draw_style_widget: qt.QWidget | None = None
        self._mirror_widget: qt.QWidget | None = None
        self._size_widget: qt.QWidget | None = None

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

        self._select_radio_widget = qt.RadioButtonGroup(
            radio_names=['Selected', 'Hierarchy'], tooltips=consts.RADIO_TOOLTIPS,
            margins=(qt.consts.SUPER_LARGE_SPACING_2, 0, qt.consts.SUPER_LARGE_SPACING_2, 0),
            spacing=qt.consts.SUPER_EXTRA_LARGE_SPACING, alignment=qt.Qt.AlignLeft,  parent=self)

        self._accordion = qt.AccordionWidget(parent=self)
        self._accordion.rollout_style = qt.AccordionStyle.ROUNDED

        self._orient_widget = qt.QWidget(parent=self)
        self._accordion.add_item('Orient', self._orient_widget)
        self._primary_axis_combo = qt.ComboBoxRegularWidget(
            label='Aim Axis', items=consts.XYZ_WITH_NEG_LIST, set_index=0, tooltip=consts.PRIMARY_AXIS_COMBO_TOOLTIP,
            parent=self)
        self._secondary_axis_combo = qt.ComboBoxRegularWidget(
            label='Roll Up', items=consts.XYZ_LIST, set_index=1, tooltip=consts.SECONDARY_AXIS_COMBO_TOOLTIP,
            parent=self)
        self._world_up_axis_combo = qt.ComboBoxRegularWidget(
            label='World Up', items=consts.XYZ_LIST + ['Up Ctrl', 'Plane'], set_index=1,
            tooltip=consts.WORLD_UP_AXIS_COMBO_TOOLTIP, parent=self)

        self._start_end_arrow_chain_button = qt.left_aligned_button(
            'Position Ctrl (Right Click)', icon='exit', tooltip=consts.START_END_ARROW_CHAIN_BUTTON_TOOLTIP,
            parent=self)
        self._start_end_chain_button = qt.left_aligned_button(
            'Position Ctrl (Right-Click)', icon='plane', tooltip=consts.START_END_ARROW_CHAIN_BUTTON_TOOLTIP,
            parent=self)
        self._select_plane_arrow_ctrl_button = qt.left_aligned_button(
            'Select Control', icon='cursor', tooltip=consts.SELECT_PLANE_ARROW_CONTROL_BUTTON_TOOLTIP, parent=self)
        self._orient_y_pos_button = qt.left_aligned_button(
            'Orient Roll +Y (Aim X)', icon='arrow_up', tooltip=consts.ORIENT_Y_POSITIVE_BUTTON_TOOLTIP, parent=self)
        self._orient_y_neg_button = qt.left_aligned_button(
            'Orient Roll -Y (Aim X)', icon='arrow_down', tooltip=consts.ORIENT_Y_NEGATIVE_BUTTON_TOOLTIP, parent=self)
        self._edit_lra_button = qt.left_aligned_button(
            'Edit LRA', icon='edit', tooltip=consts.EDIT_LRA_BUTTON_TOOLTIP, parent=self)
        self._exit_lra_button = qt.left_aligned_button(
            'Exit LRA', icon='exit', tooltip=consts.EXIT_LRA_BUTTON_TOOLTIP, parent=self)

        self._draw_style_widget = qt.QWidget(parent=self)
        self._accordion.add_item('Draw Style', self._draw_style_widget)

        self._mirror_widget = qt.QWidget(parent=self)
        self._accordion.add_item('Mirror', self._mirror_widget)

        self._size_widget = qt.QWidget(parent=self)
        self._accordion.add_item('Size', self._size_widget)

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

        orient_main_layout = qt.vertical_layout(margins=(0, 0, 0, 0), spacing=qt.consts.SPACING)
        self._orient_widget.setLayout(orient_main_layout)
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
        edit_lra_layout = qt.horizontal_layout(margins=(0, 0, 0, 0), spacing=qt.consts.SPACING)
        edit_lra_layout.addWidget(self._edit_lra_button)
        edit_lra_layout.addWidget(self._exit_lra_button)
        orient_main_layout.addLayout(axis_layout)
        orient_main_layout.addLayout(control_layout)
        orient_main_layout.addLayout(orient_layout)
        orient_main_layout.addLayout(edit_lra_layout)

        draw_style_layout = qt.vertical_layout(margins=(0, 0, 0, 0), spacing=qt.consts.SPACING)
        self._draw_style_widget.setLayout(draw_style_layout)

        mirror_layout = qt.vertical_layout(margins=(0, 0, 0, 0), spacing=qt.consts.SPACING)
        self._mirror_widget.setLayout(mirror_layout)

        size_layout = qt.vertical_layout(margins=(0, 0, 0, 0), spacing=qt.consts.SPACING)
        self._size_widget.setLayout(size_layout)

        contents_layout.addWidget(self._select_radio_widget)
        contents_layout.addWidget(self._accordion)

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
        self._orient_y_pos_button.clicked.connect(partial(self.tool.align_joint, align_up=True))
        self._orient_y_neg_button.clicked.connect(partial(self.tool.align_joint, align_up=False))
        self._edit_lra_button.clicked.connect(self.tool.edit_lra)
        self._exit_lra_button.clicked.connect(self.tool.exit_lra)

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
