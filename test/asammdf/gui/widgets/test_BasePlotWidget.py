import json
import pathlib
import time
from asammdf.gui.widgets.tree import get_data
from test.asammdf.gui.test_base import DragAndDrop
from test.asammdf.gui.widgets.test_BaseFileWidget import TestFileWidget
from unittest import mock

from PySide6 import QtCore, QtTest, QtWidgets, QtGui
from PySide6.QtCore import QCoreApplication, QPoint, QPointF, Qt
from PySide6.QtGui import QInputDevice, QPointingDevice, QWheelEvent
from PySide6.QtWidgets import QWidget


class QMenuWrap(QtWidgets.QMenu):
    return_action = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def exec(self, *args, **kwargs):
        if not self.return_action:
            return super().exec_(*args, **kwargs)
        return self.return_action


class TestPlotWidget(TestFileWidget):
    class Column:
        NAME = 0
        VALUE = 1
        UNIT = 2
        COMMON_AXIS = 3
        INDIVIDUAL_AXIS = 4

    measurement_file = str(pathlib.Path(TestFileWidget.resource, "ASAP2_Demo_V171.mf4"))

    def add_channel_to_plot(self, plot=None, channel_name=None, channel_index=None):
        if not plot and self.plot:
            plot = self.plot

        # Select channel
        channel_tree = self.widget.channels_tree
        channel_tree.clearSelection()

        selected_channel = self.find_channel(channel_tree, channel_name, channel_index)
        selected_channel.setSelected(True)
        if not channel_name:
            channel_name = selected_channel.text(self.Column.NAME)

        drag_position = channel_tree.visualItemRect(selected_channel).center()
        drop_position = plot.channel_selection.viewport().rect().center()

        # PreEvaluation
        DragAndDrop(
            src_widget=channel_tree,
            dst_widget=plot.channel_selection,
            src_pos=drag_position,
            dst_pos=drop_position,
        )
        self.processEvents(0.05)
        plot_channel = None
        iterator = QtWidgets.QTreeWidgetItemIterator(plot.channel_selection)
        while iterator.value():
            item = iterator.value()
            if item and item.text(0) == channel_name:
                plot_channel = item
            iterator += 1

        return plot_channel

    def context_menu(self, action_text, position=None):
        self.processEvents()
        with mock.patch("asammdf.gui.widgets.tree.QtWidgets.QMenu", wraps=QMenuWrap):
            mo_action = mock.MagicMock()
            mo_action.text.return_value = action_text
            QMenuWrap.return_action = mo_action

            if not position:
                QtTest.QTest.mouseClick(self.plot.channel_selection.viewport(), QtCore.Qt.MouseButton.RightButton)
            else:
                QtTest.QTest.mouseClick(
                    self.plot.channel_selection.viewport(),
                    QtCore.Qt.MouseButton.RightButton,
                    QtCore.Qt.KeyboardModifiers(),
                    position,
                )
            self.processEvents(0.01)

            while not mo_action.text.called:
                self.processEvents(0.02)

    def drag_n_drop(self, src, dst):
        def wait(ms: int = 1):
            QtTest.QTest.qWait(ms)

        def getIntEquidistantPoints(x1: int, y1: int, x2: int, y2: int):
            def l(v0, v1, i):
                return v0 + i * (v1 - v0)

            n = int(((((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5))
            return [
                (int(x), int(y)) for x, y in [(l(x1, x2, 1. / n * i), l(y1, y2, 1. / n * i)) for i in range(n + 1)]
            ]

        class StartDragThread(QtCore.QThread):
            def __init__(self, source=self.plot.channel_selection):
                super().__init__()
                self.src = source

            def run(self):
                time.sleep(0.1)
                self.src.startDrag(Qt.DropAction.MoveAction)
                wait()

        src_widget = src.treeWidget()
        dst_widget = self.plot.channel_selection
        drag_x, drag_y = src_widget.visualItemRect(src).center().x(), src_widget.visualItemRect(src).center().y() + 28
        drop_x, drop_y = dst_widget.visualItemRect(dst).center().x(), dst_widget.visualItemRect(dst).center().y() + 28

        if not src.isSelected():
            src.setSelected(True)
        if dst.isSelected():
            dst.setSelected(False)
        mime_data = QtCore.QMimeData()
        data = json.dumps(get_data(self.plot, [src])).encode()
        mime_data.setData("application/octet-stream-asammdf", QtCore.QByteArray(data))

        QtTest.QTest.mouseMove(src_widget, QPoint(drag_x, drag_y + 28))
        wait()
        start_drag_thread = StartDragThread(src_widget)
        start_drag_thread.start()
        start_drag_thread.quit()

        for x, y in getIntEquidistantPoints(drag_x, drag_y, drop_x, drop_y):
            move_point = QPoint(x, y)
            # event = QtGui.QDragMoveEvent(
            #     move_point,
            #     Qt.DropAction.MoveAction,
            #     mime_data,
            #     Qt.MouseButton.LeftButton,
            #     Qt.NoModifier
            # )
            QtTest.QTest.mouseMove(src_widget, move_point)
            # dst_widget.dragMoveEvent(event)
            wait()

        event = QtGui.QDropEvent(
            QPoint(drop_x, drop_y),
            Qt.DropAction.MoveAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.NoModifier
        )
        dst_widget.dropEvent(event)
        wait(10)
        start_drag_thread.terminate()

        wait(10)
        self.processEvents(1)

    def move_channel_to_group(self, plot=None, src=None, dst=None):
        if not plot and self.plot:
            plot = self.plot
        cs = plot.channel_selection

        if QtCore.qVersion() in ('6.7.0', '6.6.0'):
            self.drag_n_drop(src, dst)
        else:  # Perform Drag and Drop
            drag_position = cs.visualItemRect(src).center()
            drop_position = cs.visualItemRect(dst).center()
            DragAndDrop(
                src_widget=cs,
                dst_widget=cs,
                src_pos=drag_position,
                dst_pos=drop_position,
            )
        self.processEvents(0.05)

    def wheel_action(self, w: QWidget, x: float, y: float, angle_delta: int):
        """
        Used to simulate mouse wheel event.

        Parameters
        ----------
        w: widget - widget object
        x: float - x position of cursor
        y: float - y position of cursor
        angle_delta: int - physical-wheel rotations units

        Returns
        -------

        """
        pos = QPointF(x, y)

        widget_x, widget_y = self.widget.geometry().x(), self.widget.geometry().y()
        widget_width, widget_height = self.widget.width(), self.widget.height()

        global_pos = QPointF(widget_width + widget_x - x, widget_height + widget_y - y)

        pixel_d = QPoint(0, 0)
        angle_d = QPoint(0, angle_delta * 120)
        buttons = Qt.MouseButtons()
        modifiers = Qt.KeyboardModifiers()
        phase = Qt.ScrollPhase(0x0)
        inverted = False
        source = Qt.MouseEventSource(0x0)
        device = QPointingDevice(
            "core pointer",
            1,
            QInputDevice.DeviceType(0x1),
            QPointingDevice.PointerType(0x0),
            QInputDevice.Capabilities(),
            1,
            3,
        )
        # Create event
        event = QWheelEvent(pos, global_pos, pixel_d, angle_d, buttons, modifiers, phase, inverted, source, device)
        # Post event
        QCoreApplication.postEvent(w, event)
        self.assertTrue(event.isAccepted())
        QCoreApplication.processEvents()
