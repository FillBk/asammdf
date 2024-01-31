#!/usr/bin/env python
import os

from asammdf.gui.widgets.formated_axis import FormatedAxis as FA
from test.asammdf.gui.test_base import Pixmap
from test.asammdf.gui.widgets.test_BasePlotWidget import TestPlotWidget
from unittest import mock

from PySide6 import QtCore, QtGui, QtTest, QtWidgets


class TestPlotGraphicsShortcuts(TestPlotWidget):
    def setUp(self):
        # Open measurement file
        self.setUpFileWidget(measurement_file=self.measurement_file, default=True)
        # Switch ComboBox to "Natural sort"
        self.widget.channel_view.setCurrentText("Natural sort")
        # Select channels -> Press PushButton "Create Window" -> "Plot"
        self.create_window(window_type="Plot")
        self.assertEqual(len(self.widget.mdi_area.subWindowList()), 1)
        self.w = self.widget.mdi_area.subWindowList()[0].widget()
        self.plot = self.w.plot

        self.widget.add_new_channels([self.widget.channels_tree.topLevelItem(35).name], self.w)
        self.processEvents()

    def test_Plot_PlotGraphics_Shortcuts(self):
        """
        ...
        """
        with self.subTest("test_Y"):
            if self.plot.region_lock is None:
                QtTest.QTest.keyClick(self.plot, QtCore.Qt.Key_Y)
                self.assertIsNotNone(self.plot.region_lock)
                self.assertFalse(self.plot.region.movable)
                self.assertFalse(self.plot.region.lines[0].movable)
                self.assertTrue(self.plot.region.lines[0].locked)

                QtTest.QTest.keyClick(self.plot, QtCore.Qt.Key_Y)
                self.assertIsNone(self.plot.region_lock)
                self.assertTrue(self.plot.region.movable)
                self.assertTrue(self.plot.region.lines[0].movable)
                self.assertFalse(self.plot.region.lines[0].locked)

            else:
                QtTest.QTest.keyClick(self.plot, QtCore.Qt.Key_Y)
                self.assertIsNone(self.plot.region_lock)
                self.assertTrue(self.plot.region.movable)
                self.assertTrue(self.plot.region.lines[0].movable)
                self.assertFalse(self.plot.region.lines[0].locked)

                QtTest.QTest.keyClick(self.plot, QtCore.Qt.Key_Y)
                self.assertIsNotNone(self.plot.region_lock)
                self.assertFalse(self.plot.region.movable)
                self.assertFalse(self.plot.region.lines[0].movable)
                self.assertTrue(self.plot.region.lines[0].locked)

        with self.subTest("test_X"):
            ...


class TestPlotGraphicsShortcuts_Functionality(TestPlotWidget):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName)

    def setUp(self):
        # Open measurement file
        self.setUpFileWidget(measurement_file=self.measurement_file, default=True)
        # Switch ComboBox to "Natural sort"
        self.widget.channel_view.setCurrentText("Natural sort")
        # Select channels -> Press PushButton "Create Window" -> "Plot"
        self.create_window(window_type="Plot")
        self.assertEqual(len(self.widget.mdi_area.subWindowList()), 1)
        self.plot = self.widget.mdi_area.subWindowList()[0].widget()
        # Settings for cursor
        # self.widget.set_cursor_options(False, False, 1, Pixmap.COLOR_BACKGROUND)

        # Remove dots
        if self.plot.plot.with_dots:
            self.plot.plot.set_dots(False)
        self.processEvents()
        # check if grid is available -> hide grid
        if not self.plot.hide_axes_btn.isFlat():
            QtTest.QTest.mouseClick(self.plot.hide_axes_btn, QtCore.Qt.MouseButton.LeftButton)
        # hide bookmarks if it's available
        if self.plot.show_bookmarks:
            self.plot.toggle_bookmarks(hide=True)
        self.processEvents()
        # pixmap is not black
        self.assertTrue(Pixmap.is_black(self.plot.plot.viewport().grab()))

    def addChannelsToPlot(self, channels: list):
        """
        add channels from a list with channels indexes
        """
        if channels:
            self.channels = []

        for _, ch in enumerate(channels):
            self.widget.add_new_channels([self.widget.channels_tree.topLevelItem(ch).name], self.plot)
            # channels
            self.channels.append(self.plot.channel_selection.topLevelItem(_))

        self.assertEqual(len(channels), self.plot.channel_selection.topLevelItemCount())
        self.processEvents()

    def test_Plot_PlotGraphics_Shortcut_Key_Y(self):
        """
        Test Scope:
            Check if Range Selection cursor is locked/unlocked after pressing key Y.
        Events:
            - Open 'FileWidget' with valid measurement.
            - Press PushButton "Create Window"
            - Press PushButton HideAxis (easy for evaluation)
            - Press Key R for range selection
            - Move Cursors
            - Press Key R for range selection
        Evaluate:
            - Evaluate that two cursors are available
            - Evaluate that new rectangle with different color is present
            - Evaluate that sum of rectangle areas is same with the one when plot is full black.
            - Evaluate that range selection disappear.
        """
        if not self.plot.hide_axes_btn.isFlat():
            QtTest.QTest.mouseClick(self.plot.hide_axes_btn, QtCore.Qt.LeftButton)
        self.widget.set_cursor_options(False, False, 1, Pixmap.COLOR_CURSOR)
        # Save PixMap of clear plot
        clear_pixmap = self.plot.plot.viewport().grab()
        clear_pixmap.save("D:\\huletdadagsautuai.png")

        self.assertTrue(Pixmap.is_black(clear_pixmap))
        # Get X position of Cursor
        cursors = Pixmap.cursors_x(clear_pixmap)
        # Evaluate that there is only one cursor
        self.assertEqual(1, len(cursors))

        # Press Key 'R' for range selection
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_Y)
        self.processEvents(timeout=0.01)

        # Save PixMap of Range plot
        range_pixmap = self.plot.plot.viewport().grab()
        self.assertFalse(Pixmap.is_black(range_pixmap))

        # Get X position of Cursors
        cursors = Pixmap.cursors_x(range_pixmap)
        # Evaluate that two cursors are available
        self.assertEqual(2, len(cursors))

        # Evaluate that new rectangle with different color is present
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=0,
                y=0,
                width=min(cursors) - 1,
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_RANGE,
                x=min(cursors) + 1,
                y=0,
                width=max(cursors),
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=max(cursors) + 1,
                y=0,
            )
        )

        # Move Cursors
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_Left)
        self.processEvents(timeout=0.01)
        QtTest.QTest.keySequence(self.plot.plot, QtGui.QKeySequence("Ctrl+Left"))
        self.processEvents(timeout=0.01)

        # Save PixMap of Range plot
        range_pixmap = self.plot.plot.viewport().grab()
        self.assertFalse(Pixmap.is_black(range_pixmap))

        # Get X position of Cursors
        new_cursors = Pixmap.cursors_x(range_pixmap)
        # Evaluate that two cursors are available
        self.assertEqual(2, len(cursors))
        self.assertEqual(cursors[0], new_cursors[0], "First cursor have new position after manipulation")
        self.assertNotEqual(cursors[1], new_cursors[1], "Second cursors have same position after manipulation")

        # Evaluate that new rectangle with different color is present
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=0,
                y=0,
                width=min(new_cursors) - 1,
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_RANGE,
                x=min(new_cursors) + 1,
                y=0,
                width=max(new_cursors),
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=max(new_cursors) + 1,
                y=0,
            )
        )

        cursors = new_cursors
        # Press Key 'R' for range selection
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_Y)
        self.processEvents(timeout=0.01)

        # Move Cursors
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_Right)
        self.processEvents(timeout=0.01)
        QtTest.QTest.keySequence(self.plot.plot, QtGui.QKeySequence("Ctrl+Left"))
        self.processEvents(timeout=0.01)

        # Save PixMap of Range plot
        range_pixmap = self.plot.plot.viewport().grab()
        self.assertFalse(Pixmap.is_black(range_pixmap))

        # Get X position of Cursors
        new_cursors = Pixmap.cursors_x(range_pixmap)
        # Evaluate that two cursors are available
        self.assertEqual(2, len(cursors))
        for c in cursors:
            self.assertNotIn(c, new_cursors, f"cursor {c} is the same")

        # Evaluate that new rectangle with different color is present
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=0,
                y=0,
                width=min(new_cursors) - 1,
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_RANGE,
                x=min(new_cursors) + 1,
                y=0,
                width=max(new_cursors),
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=max(new_cursors) + 1,
                y=0,
            )
        )

        # Press Key 'R' for range selection
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_R)
        self.processEvents(timeout=0.01)
        # Save PixMap of clear plot
        clear_pixmap = self.plot.plot.viewport().grab()
        self.assertTrue(Pixmap.is_black(clear_pixmap))

    def test_Plot_PlotGraphics_Shortcut_Key_X(self):
        """
        Test Scope:
            Check if fitting between cursors is released after pressing key "X".
        Events:
            - Open 'FileWidget' with valid measurement.
            - Display 1 signal on plot
            - Maximize window
            - Count how many times signal intersects midd line of plot
            - Mouse click in the middle of plot
            - Press "R"
            - Get color of signal between cursors
            - Get Y coordinates of signal where it intersects cursors
            - Count how many times signal intersect midd line of plot between cursors
            - Press "X"
            - Get Y coordinates of start and end point of signal
            - Count how many times signal intersect midd line of plot
        Evaluate:
            > Precondition
                - Evaluate that plot is not black
                - Evaluate that plot intersects midd line of plot
                - Evaluate that new color of signal was found
                - Evaluate that one row after first cursor and one row before second cursor signal exist
                        or signal was found between cursors
                - Evaluate that signal intersect midd line of plot between cursors
            > Final tests
                - Evaluate that start and end points of signal was found
                - Evaluate lines where is situated start and end points of signal by this logic:
                    • After zooming to range - signal slope decrease
                    • After calculus - points can differ, but difference must be minimal, a few pixels maximum
                    • By dividing expected values and actual values if the values not differ too much,
                        expected result must be near 1, precision can be adjusted
                - Evaluate that the number of intersections between signal and the midd line inner cursors are equal
                    with number of intersections between signal and the midd line after pressing key "X"
                - Evaluate that the signal intersect the midd line less time after pressing key "X"
        """
        # Setup
        self.addChannelsToPlot([35])
        channel_color = self.channels[0].color.name()

        self.widget.showMaximized()
        self.processEvents()

        # Count intersections between middle line and signal
        firstIntersections = Pixmap.color_map(
            self.plot.plot.viewport().grab(QtCore.QRect(0, int(self.plot.plot.height() / 2), self.plot.plot.width(), 1))
        )[0].count(channel_color)
        self.assertTrue(firstIntersections)

        # Setup for cursor
        self.widget.set_cursor_options(False, False, 1, Pixmap.COLOR_CURSOR)
        # Mouse click on a center of plot
        QtTest.QTest.mouseClick(
            self.plot.plot.viewport(),
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.KeyboardModifiers(),
            self.plot.plot.viewport().rect().center(),
        )
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_R)
        self.processEvents()
        # Get X position of Cursor
        cursors = Pixmap.cursors_x(self.plot.plot.viewport().grab())
        self.assertEqual(len(cursors), 2)

        # Get a set of colors founded between cursors
        colors = Pixmap.color_names_exclude_defaults(
            self.plot.plot.viewport().grab(
                QtCore.QRect(cursors[0], 0, cursors[1] - cursors[0], self.plot.plot.height())
            )
        )
        # Exclude channel original color
        if channel_color in colors:
            colors.remove(channel_color)
        # caught ya
        color = colors.pop()
        # Evaluate if color was found
        self.assertTrue(color)

        # Count intersection of midd line and signal between cursors
        interCursorsIntersectionsR = Pixmap.color_map(
            self.plot.plot.viewport().grab(
                QtCore.QRect(cursors[0], int(self.plot.plot.height() / 2), cursors[1] - cursors[0], 1)
            )
        )[0].count(color)
        self.assertTrue(interCursorsIntersectionsR)
        # Search lines where signal intersects cursors
        expectedSignalStartYPoint = Pixmap.search_y_of_signal_in_column(
            self.plot.plot.viewport().grab(QtCore.QRect(cursors[0] + 2, 0, 1, self.plot.plot.height())), color
        )
        expectedSignalEndYPoint = Pixmap.search_y_of_signal_in_column(
            self.plot.plot.viewport().grab(QtCore.QRect(cursors[1] - 2, 0, 1, self.plot.plot.height())), color
        )
        self.assertTrue(expectedSignalStartYPoint)
        self.assertTrue(expectedSignalEndYPoint)

        # Press key "X"
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_X)
        self.processEvents()

        # Find where signal start and end on X axes
        from_to_x = Pixmap.search_signal_extremes_by_ax(self.plot.plot.viewport().grab(), channel_color, "x")
        self.assertEqual(len(from_to_x), 2)
        # Search lines where signal start and end
        signalStartOnLine = Pixmap.search_y_of_signal_in_column(
            self.plot.plot.viewport().grab(QtCore.QRect(from_to_x[0], 0, 1, self.plot.plot.height())),
            channel_color,
        )
        signalEndOnLine = Pixmap.search_y_of_signal_in_column(
            self.plot.plot.viewport().grab(QtCore.QRect(from_to_x[1], 0, 1, self.plot.plot.height())),
            channel_color,
        )
        # Evaluate
        precission = 0.1  # for displays with smaller resolution
        self.assertAlmostEqual(
            expectedSignalStartYPoint / signalStartOnLine,
            1,
            msg=f"Difference is too big: {expectedSignalStartYPoint} / {signalStartOnLine} = "
            f"{expectedSignalStartYPoint / signalStartOnLine}",
            delta=precission,
        )
        self.assertAlmostEqual(
            expectedSignalEndYPoint / signalEndOnLine,
            1,
            msg=f"Difference is too big: {expectedSignalEndYPoint} / {signalEndOnLine} = "
            f"{expectedSignalEndYPoint / signalEndOnLine}",
            delta=precission,
        )
        # The Number of intersections between signal and midd line must be the same as in the first case
        interCursorsIntersectionsX = Pixmap.color_map(
            self.plot.plot.viewport().grab(QtCore.QRect(0, int(self.plot.plot.height() / 2), self.plot.plot.width(), 1))
        )[0].count(channel_color)
        self.assertEqual(interCursorsIntersectionsR, interCursorsIntersectionsX)
        self.assertLess(interCursorsIntersectionsX, firstIntersections)

    def test_Plot_PlotGraphics_Shortcut_Key_S_ShiftS_ShiftF_F(self):
        """
        Test Scope:
            To check if:
              > all signals is stack after pressing key "S"
              > only selected signal is fitted after pressing combination "Sift + F"
              > only selected signal is stacked after pressing combination "Shift + S"
              > all signals is fitted after pressing key "F"
        Events:
            - Open 'FileWidget' with valid measurement.
            - Select 3 signals and create a plot
            - Press Key "S"
            - Press combination "Shift + F"
            - Press combination "Shift + S"
            - press key "F"
        Evaluate:
            - Evaluate that two signals are available
            - Evaluate that plot is not black
            - Evaluate that signals are separated in top, midd and bottom third of plot after pressing key "S"
            - Evaluate that only selected signal is fitted after pressing combination "Shift + F"
            - Evaluate that only selected signal is stacked after pressing combination "Shift + S"
            - Evaluate that all signals is fitted after pressing key "F"
        """

        self.addChannelsToPlot([35, 36, 37])

        self.channel_35 = self.channels[0]
        self.channel_36 = self.channels[1]
        self.channel_37 = self.channels[2]
        # Press "S"
        QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_S)
        self.processEvents()
        # Evaluate
        with self.subTest("test_shortcut_S"):
            # First 2 lines
            self.assertTrue(
                Pixmap.is_black(self.plot.plot.viewport().grab(QtCore.QRect(0, 0, self.plot.plot.width(), 2)))
            )
            # Top
            pixmap = self.plot.plot.viewport().grab(
                QtCore.QRect(0, 0, self.plot.plot.width(), int(self.plot.plot.height() / 3))
            )
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_36.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_37.color.name()))
            # Midd
            pixmap = self.plot.plot.viewport().grab(
                QtCore.QRect(
                    0, int(self.plot.plot.height() / 3), self.plot.plot.width(), int(self.plot.plot.height() / 3)
                )
            )
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_35.color.name()))
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_36.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_37.color.name()))
            # Bottom
            pixmap = self.plot.plot.viewport().grab(
                QtCore.QRect(
                    0, int(self.plot.plot.height() / 3) * 2, self.plot.plot.width(), int(self.plot.plot.height() / 3)
                )
            )
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_35.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_36.color.name()))
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_37.color.name()))
            # Last 2 lines
            self.assertTrue(
                Pixmap.is_black(
                    self.plot.plot.viewport().grab(
                        QtCore.QRect(0, self.plot.plot.height() - 2, self.plot.plot.width(), 2)
                    )
                )
            )

        # select the first channel
        self.mouseClick_WidgetItem(self.channel_35)
        # Press "Shift+F"
        QtTest.QTest.keySequence(self.plot.plot, QtGui.QKeySequence("Shift+F"))
        self.avoid_blinking_issue(self.plot.channel_selection)
        for _ in range(50):
            self.processEvents()
        # Evaluate
        with self.subTest("test_shortcut_Shift_F"):
            # First line
            self.assertTrue(
                Pixmap.is_black(self.plot.plot.viewport().grab(QtCore.QRect(0, 0, self.plot.plot.width(), 1)))
            )
            # Second line
            self.assertTrue(
                Pixmap.has_color(
                    self.plot.plot.viewport().grab(QtCore.QRect(0, 1, self.plot.plot.width(), 1)),
                    self.channel_35.color.name(),
                )
            )
            # Top
            pixmap = self.plot.plot.viewport().grab(
                QtCore.QRect(0, 0, self.plot.plot.width(), int(self.plot.plot.height() / 3))
            )
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_36.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_37.color.name()))
            # Midd
            pixmap = self.plot.plot.viewport().grab(
                QtCore.QRect(
                    0, int(self.plot.plot.height() / 3), self.plot.plot.width(), int(self.plot.plot.height() / 3)
                )
            )
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_36.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_37.color.name()))
            # Bottom
            pixmap = self.plot.plot.viewport().grab(
                QtCore.QRect(
                    0, int(self.plot.plot.height() / 3) * 2, self.plot.plot.width(), int(self.plot.plot.height() / 3)
                )
            )
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_36.color.name()))
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_37.color.name()))
            # Last 2 lines
            self.assertTrue(
                Pixmap.has_color(
                    self.plot.plot.viewport().grab(
                        QtCore.QRect(0, self.plot.plot.height() - 2, self.plot.plot.width(), 1)
                    ),
                    self.channel_35.color.name(),
                )
            )
            self.assertTrue(
                Pixmap.is_black(
                    self.plot.plot.viewport().grab(
                        QtCore.QRect(0, self.plot.plot.height() - 1, self.plot.plot.width(), 1)
                    )
                )
            )

        # select second channel
        self.mouseClick_WidgetItem(self.channel_36)
        # Press "Shift+F"
        QtTest.QTest.keySequence(self.plot.plot, QtGui.QKeySequence("Shift+S"))
        self.avoid_blinking_issue(self.plot.channel_selection)
        # Evaluate
        with self.subTest("test_shortcut_Shift_S"):
            # First line
            self.assertTrue(
                Pixmap.is_black(self.plot.plot.viewport().grab(QtCore.QRect(0, 0, self.plot.plot.width(), 1)))
            )
            # Second line
            self.assertTrue(
                Pixmap.has_color(
                    self.plot.plot.viewport().grab(QtCore.QRect(0, 1, self.plot.plot.width(), 1)),
                    self.channel_35.color.name(),
                )
            )
            # Top
            pixmap = self.plot.plot.viewport().grab(
                QtCore.QRect(0, 0, self.plot.plot.width(), int(self.plot.plot.height() / 3))
            )
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_36.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_37.color.name()))
            # Midd
            pixmap = self.plot.plot.viewport().grab(
                QtCore.QRect(
                    0, int(self.plot.plot.height() / 3), self.plot.plot.width(), int(self.plot.plot.height() / 3)
                )
            )
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_36.color.name()))
            self.assertFalse(Pixmap.has_color(pixmap, self.channel_37.color.name()))
            # Bottom
            pixmap = self.plot.plot.viewport().grab(
                QtCore.QRect(
                    0, int(self.plot.plot.height() / 3) * 2, self.plot.plot.width(), int(self.plot.plot.height() / 3)
                )
            )
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_36.color.name()))
            self.assertTrue(Pixmap.has_color(pixmap, self.channel_37.color.name()))
            # Last 2 lines
            self.assertTrue(
                Pixmap.has_color(
                    self.plot.plot.viewport().grab(
                        QtCore.QRect(0, self.plot.plot.height() - 2, self.plot.plot.width(), 1)
                    ),
                    self.channel_35.color.name(),
                )
            )
            self.assertTrue(
                Pixmap.is_black(
                    self.plot.plot.viewport().grab(
                        QtCore.QRect(0, self.plot.plot.height() - 1, self.plot.plot.width(), 1)
                    )
                )
            )

            # Press "F"
            QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_F)
            self.avoid_blinking_issue(self.plot.channel_selection)
            # Evaluate
            with self.subTest("test_shortcut_S"):
                # First line
                self.assertTrue(
                    Pixmap.is_black(self.plot.plot.viewport().grab(QtCore.QRect(0, 0, self.plot.plot.width(), 1)))
                )
                # Top
                pixmap = self.plot.plot.viewport().grab(
                    QtCore.QRect(0, 0, self.plot.plot.width(), int(self.plot.plot.height() / 3))
                )
                self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
                self.assertTrue(Pixmap.has_color(pixmap, self.channel_36.color.name()))
                self.assertTrue(Pixmap.has_color(pixmap, self.channel_37.color.name()))
                # Midd
                pixmap = self.plot.plot.viewport().grab(
                    QtCore.QRect(
                        0, int(self.plot.plot.height() / 3), self.plot.plot.width(), int(self.plot.plot.height() / 3)
                    )
                )
                self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
                self.assertTrue(Pixmap.has_color(pixmap, self.channel_36.color.name()))
                self.assertTrue(Pixmap.has_color(pixmap, self.channel_37.color.name()))
                # Bottom
                pixmap = self.plot.plot.viewport().grab(
                    QtCore.QRect(
                        0,
                        int(self.plot.plot.height() / 3) * 2,
                        self.plot.plot.width(),
                        int(self.plot.plot.height() / 3),
                    )
                )
                self.assertTrue(Pixmap.has_color(pixmap, self.channel_35.color.name()))
                self.assertTrue(Pixmap.has_color(pixmap, self.channel_36.color.name()))
                self.assertTrue(Pixmap.has_color(pixmap, self.channel_37.color.name()))
                # Last line
                self.assertTrue(
                    Pixmap.is_black(
                        self.plot.plot.viewport().grab(
                            QtCore.QRect(0, self.plot.plot.height() - 1, self.plot.plot.width(), 1)
                        )
                    )
                )

    def test_Plot_PlotGraphics_Shortcut_Key_G(self):
        """
        Test Scope:
            Check if grid is created properly after pressing key "G".
        Events:
            - Open 'FileWidget' with valid measurement.
            - Create a plot window
            - If axes is hidden - press "Show axes" button
            - Press Key "G" 3 times
        Evaluate:
            - Evaluate that window is created
            - Evaluate that grid is displayed in order after pressing key "G":
                1. Is only X axes grid
                2. Is X and Y axes grid
                3. There is no grid
        """
        # check if grid is available
        if self.plot.hide_axes_btn.isFlat():
            QtTest.QTest.mouseClick(self.plot.hide_axes_btn, QtCore.Qt.MouseButton.LeftButton)
        # case 1: X and Y axes is hidden
        if not self.plot.plot.x_axis.grid and not self.plot.plot.y_axis.grid:
            with self.subTest("test_shortcut_key_G_no_grid_displayed"):
                # press key "G"
                QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_G)
                self.processEvents()
                self.assertTrue(self.plot.plot.x_axis.grid)
                self.assertFalse(self.plot.plot.y_axis.grid)
                # press key "G"
                QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_G)
                self.processEvents()
                self.assertTrue(self.plot.plot.x_axis.grid)
                self.assertTrue(self.plot.plot.y_axis.grid)
                # press key "G"
                QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_G)
                self.processEvents()
                self.assertFalse(self.plot.plot.x_axis.grid)
                self.assertFalse(self.plot.plot.y_axis.grid)
        # case 2: X is visible, Y is hidden
        elif self.plot.plot.x_axis.grid and not self.plot.plot.y_axis.grid:
            with self.subTest("test_shortcut_key_G_X_grid_already_displayed"):
                # press key "G"
                QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_G)
                self.processEvents()
                self.assertTrue(self.plot.plot.x_axis.grid)
                self.assertTrue(self.plot.plot.y_axis.grid)
                # press key "G"
                QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_G)
                self.processEvents()
                self.assertFalse(self.plot.plot.x_axis.grid)
                self.assertFalse(self.plot.plot.y_axis.grid)
                # press key "G"
                QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_G)
                self.processEvents()
                self.assertTrue(self.plot.plot.x_axis.grid)
                self.assertFalse(self.plot.plot.y_axis.grid)
        # case 3: X and Y axes is visible
        else:
            with self.subTest("test_shortcut_key_G_XU_grid_already_displayed"):
                # press key "G"
                QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_G)
                self.processEvents()
                self.assertTrue(self.plot.plot.x_axis.grid)
                self.assertFalse(self.plot.plot.y_axis.grid)
                # press key "G"
                QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_G)
                self.processEvents()
                self.assertTrue(self.plot.plot.x_axis.grid)
                self.assertTrue(self.plot.plot.y_axis.grid)
                # press key "G"
                QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_G)
                self.processEvents()
                self.assertFalse(self.plot.plot.x_axis.grid)
                self.assertFalse(self.plot.plot.y_axis.grid)

    def test_Plot_PlotGraphics_Shortcut_Key_I(self):
        """
        Test Scope:
            Check if zooming is released after pressing key "I".
        Events:
            - Open 'FileWidget' with valid measurement.
            - Display 1 signal on plot
            - Select signal
            - Press "I""
        Evaluate:
            - Evaluate that plot is not black
            - Evaluate that distance between first and second transition of signal in the same line is increased
                after pressing key "I"
        """
        self.addChannelsToPlot([35])
        self.channel_35 = self.channels[0]

        # Select line
        yMiddLine = self.plot.plot.viewport().grab(
            QtCore.QRect(0, int(self.plot.plot.height() / 2), self.plot.plot.viewport().width(), 1)
        )
        colorMap = Pixmap.color_map(yMiddLine)
        distanceInPixels_1 = 0
        # Find distance between first and second signal transit trough midd line
        for i, x in enumerate(colorMap[0]):
            if x == self.channel_35.color.name():
                distanceInPixels_1 = i - distanceInPixels_1
                if distanceInPixels_1 != i:
                    break
        self.assertTrue(distanceInPixels_1)
        # Press "I"
        QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_I)
        self.processEvents()
        # Select line
        yMiddLine = self.plot.plot.viewport().grab(
            QtCore.QRect(0, int(self.plot.plot.height() / 2), self.plot.plot.viewport().width(), 1)
        )
        colorMap = Pixmap.color_map(yMiddLine)
        distanceInPixels_2 = 0
        # Find distance between first and second signal transit trough midd line
        for i, x in enumerate(colorMap[0]):
            if x == self.channel_35.color.name():
                distanceInPixels_2 = i - distanceInPixels_2
                if distanceInPixels_2 != i:
                    break
        self.assertLess(distanceInPixels_1, distanceInPixels_2)

    def test_Plot_PlotGraphics_Shortcut_Key_O(self):
        """
        Test Scope:
            Check if zooming is released after pressing key "O".
        Events:
            - Open 'FileWidget' with valid measurement.
            - Display 1 signal on plot
            - Select signal
            - Press "O"
        Evaluate:
            - Evaluate that plot is not black
            - Evaluate that the distance between first and second transition of signal in the same line is decreased
                after pressing key "O"
        """
        self.addChannelsToPlot([35])
        self.channel_35 = self.channels[0]
        # Select line
        yMiddLine = self.plot.plot.viewport().grab(
            QtCore.QRect(0, int(self.plot.plot.height() / 2), self.plot.plot.viewport().width(), 1)
        )
        colorMap = Pixmap.color_map(yMiddLine)
        distanceInPixels_1 = 0
        # Find distance between first and second signal transit trough midd line
        for i, x in enumerate(colorMap[0]):
            if x == self.channel_35.color.name():
                distanceInPixels_1 = i - distanceInPixels_1
                if distanceInPixels_1 != i:
                    break
        self.assertTrue(distanceInPixels_1)
        # Press "I"
        QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_O)
        self.processEvents()
        # Select line
        yMiddLine = self.plot.plot.viewport().grab(
            QtCore.QRect(0, int(self.plot.plot.height() / 2), self.plot.plot.viewport().width(), 1)
        )
        colorMap = Pixmap.color_map(yMiddLine)
        distanceInPixels_2 = 0
        # Find distance between first and second signal transit trough midd line
        for i, x in enumerate(colorMap[0]):
            if x == self.channel_35.color.name():
                distanceInPixels_2 = i - distanceInPixels_2
                if distanceInPixels_2 != i:
                    break
        self.assertGreater(distanceInPixels_1, distanceInPixels_2)

    def test_Plot_PlotGraphics_Shortcut_Key_R(self):
        """
        Test Scope:
            Check if Range Selection rectangle is painted over the self.plot.
        Events:
            - Open 'FileWidget' with valid measurement.
            - Press PushButton "Create Window"
            - Press PushButton HideAxis (easy for evaluation)
            - Press Key R for range selection
            - Move Cursors
            - Press Key R for range selection
        Evaluate:
            - Evaluate that two cursors are available
            - Evaluate that new rectangle with different color is present
            - Evaluate that sum of rectangle areas is same with the one when plot is full black.
            - Evaluate that range selection disappear.
        """
        self.widget.set_cursor_options(False, False, 1, Pixmap.COLOR_CURSOR)
        # Save PixMap of clear plot
        clear_pixmap = self.plot.plot.viewport().grab()
        self.assertTrue(Pixmap.is_black(clear_pixmap))

        # Get X position of Cursor
        cursors = Pixmap.cursors_x(clear_pixmap)
        # Evaluate that there is only one cursor
        self.assertEqual(1, len(cursors))

        # Press Key 'R' for range selection
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_R)
        self.processEvents(timeout=0.01)

        # Save PixMap of Range plot
        range_pixmap = self.plot.plot.viewport().grab()
        self.assertFalse(Pixmap.is_black(range_pixmap))

        # Get X position of Cursors
        cursors = Pixmap.cursors_x(range_pixmap)
        # Evaluate that two cursors are available
        self.assertEqual(2, len(cursors))

        # Evaluate that new rectangle with different color is present
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=0,
                y=0,
                width=min(cursors) - 1,
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_RANGE,
                x=min(cursors) + 1,
                y=0,
                width=max(cursors),
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=max(cursors) + 1,
                y=0,
            )
        )

        # Move Cursors
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_Right)
        self.processEvents(timeout=0.01)
        QtTest.QTest.keySequence(self.plot.plot, QtGui.QKeySequence("Ctrl+Left"))
        self.processEvents(timeout=0.01)

        # Save PixMap of Range plot
        range_pixmap = self.plot.plot.viewport().grab()
        self.assertFalse(Pixmap.is_black(range_pixmap))

        # Get X position of Cursors
        new_cursors = Pixmap.cursors_x(range_pixmap)
        # Evaluate that two cursors are available
        self.assertEqual(2, len(cursors))
        for c in cursors:
            self.assertNotIn(c, new_cursors, f"cursor {c} is the same")

        # Evaluate that new rectangle with different color is present
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=0,
                y=0,
                width=min(new_cursors) - 1,
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_RANGE,
                x=min(new_cursors) + 1,
                y=0,
                width=max(new_cursors),
            )
        )
        self.assertTrue(
            Pixmap.is_colored(
                pixmap=range_pixmap,
                color_name=Pixmap.COLOR_BACKGROUND,
                x=max(new_cursors) + 1,
                y=0,
            )
        )
        # Press Key 'R' for range selection
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_R)
        self.processEvents(timeout=0.01)

        # Save PixMap of clear plot
        clear_pixmap = self.plot.plot.viewport().grab()
        self.assertTrue(Pixmap.is_black(clear_pixmap))

    def test_Plot_PlotGraphics_Shortcut_Key_LeftRight(self):
        """
        Test Scope:
            Check that Arrow Keys: Left & Right ensure navigation on channels evolution.
            Ensure that navigation is working.
        Events:
            - Open 'FileWidget' with valid measurement.
            - Switch ComboBox to "Natural sort"
            - Press PushButton "Create Window"
            - Drag and Drop channels from FileWidget.channels_tree to self.plot.channels_selection:
                # First
                - ASAM_[15].M.MATRIX_DIM_16.UBYTE.IDENTICAL
                # Second
                - ASAM_[14].M.MATRIX_DIM_16.UBYTE.IDENTICAL
            - Send KeyClick Right 5 times
            - Send KeyClick Left 4 times
        Evaluate:
            - Evaluate values from `Value` column on self.plot.channels_selection
            - Evaluate timestamp label
        """
        self.addChannelsToPlot([36, 37])
        self.channel_36 = self.channels[0]
        self.channel_37 = self.channels[1]

        # Case 0:
        with self.subTest("test_Plot_Plot_Shortcut_Key_LeftRight_0"):
            # Select channel: ASAM_[15].M.MATRIX_DIM_16.UBYTE.IDENTICAL
            self.mouseClick_WidgetItem(self.channel_37)
            self.plot.plot.setFocus()
            self.processEvents(0.1)

            self.assertEqual("25", self.channel_36.text(self.Column.VALUE))
            self.assertEqual("244", self.channel_37.text(self.Column.VALUE))

            # Send Key strokes
            for _ in range(6):
                QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_Right)
                self.processEvents(0.1)
            self.processEvents(0.1)

            # Evaluate
            self.assertEqual("8", self.channel_36.text(self.Column.VALUE))
            self.assertEqual("6", self.channel_37.text(self.Column.VALUE))
            self.assertEqual("t = 0.082657s", self.plot.cursor_info.text())

            # Send Key strokes
            for _ in range(5):
                QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_Left)
                self.processEvents(0.1)
            self.processEvents(0.1)

            # Evaluate
            self.assertEqual("21", self.channel_36.text(self.Column.VALUE))
            self.assertEqual("247", self.channel_37.text(self.Column.VALUE))
            self.assertEqual("t = 0.032657s", self.plot.cursor_info.text())

        # Case 1:
        with self.subTest("test_Plot_Plot_Shortcut_Key_LeftRight_1"):
            # Select channel: ASAM_[14].M.MATRIX_DIM_16.UBYTE.IDENTICAL
            self.mouseClick_WidgetItem(self.channel_37)
            self.plot.plot.setFocus()
            self.processEvents(0.1)

            # Send Key strokes
            for _ in range(6):
                QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_Right)
                self.processEvents(0.1)
            self.processEvents(0.1)

            # Evaluate
            self.assertEqual("5", self.channel_36.text(self.Column.VALUE))
            self.assertEqual("9", self.channel_37.text(self.Column.VALUE))
            self.assertEqual("t = 0.092657s", self.plot.cursor_info.text())

            # Send Key strokes
            for _ in range(5):
                QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_Left)
                self.processEvents(0.1)
            self.processEvents(0.1)

            # Evaluate
            self.assertEqual("18", self.channel_36.text(self.Column.VALUE))
            self.assertEqual("250", self.channel_37.text(self.Column.VALUE))
            self.assertEqual("t = 0.042657s", self.plot.cursor_info.text())

    def test_Plot_PlotGraphics_Shortcut_Key_Shift_Arrows(self):
        """
        Test Scope:
            Check that Shift + Arrow Keys ensure moving of selected channels.
        Events:
            - Open 'FileWidget' with valid measurement.
            - Switch ComboBox to "Natural sort"
            - Press PushButton "Create Window"
            - Create plot with 2 channels
            - Press key "S" to separate signals for better evaluation
            - Click on first channel
            - Press "Shift" key + arrow "Down" & "Left"
            - Click on second channel
            - Press "Shift" key + arrow "Up" & "Right"
        Evaluate:
            - Evaluate that two signals are available
            - Evaluate that plot is not black and contain colors of all 3 channels
            - Evaluate that first signal is shifted down & left after pressing combination "Shift+Down" & "Shift+Left"
            - Evaluate that second signal is shifted up & right after pressing combination "Shift+Up" & "Shift+Right"
        """
        self.addChannelsToPlot([36, 37])
        self.channel_36 = self.channels[0]
        self.channel_37 = self.channels[1]

        QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_S)
        self.processEvents(0.01)
        old_from_to_y_channel_36 = Pixmap.search_signal_extremes_by_ax(
            self.plot.plot.viewport().grab(), self.channel_36.color.name(), "y"
        )
        old_from_to_y_channel_37 = Pixmap.search_signal_extremes_by_ax(
            self.plot.plot.viewport().grab(), self.channel_37.color.name(), "y"
        )
        old_from_to_x_channel_36 = Pixmap.search_signal_extremes_by_ax(
            self.plot.plot.viewport().grab(), self.channel_36.color.name(), "x"
        )
        old_from_to_x_channel_37 = Pixmap.search_signal_extremes_by_ax(
            self.plot.plot.viewport().grab(), self.channel_37.color.name(), "x"
        )

        self.mouseClick_WidgetItem(self.channel_36)
        QtTest.QTest.keySequence(self.plot.plot.viewport(), QtGui.QKeySequence("Shift+Down"))
        QtTest.QTest.keySequence(self.plot.plot.viewport(), QtGui.QKeySequence("Shift+Left"))
        self.mouseClick_WidgetItem(self.channel_37)
        QtTest.QTest.keySequence(self.plot.plot.viewport(), QtGui.QKeySequence("Shift+Up"))
        QtTest.QTest.keySequence(self.plot.plot.viewport(), QtGui.QKeySequence("Shift+Right"))

        self.avoid_blinking_issue(self.plot.channel_selection)

        new_from_to_y_channel_36 = Pixmap.search_signal_extremes_by_ax(
            self.plot.plot.viewport().grab(), self.channel_36.color.name(), "y"
        )
        new_from_to_y_channel_37 = Pixmap.search_signal_extremes_by_ax(
            self.plot.plot.viewport().grab(), self.channel_37.color.name(), "y"
        )
        new_from_to_x_channel_36 = Pixmap.search_signal_extremes_by_ax(
            self.plot.plot.viewport().grab(), self.channel_36.color.name(), "x"
        )
        new_from_to_x_channel_37 = Pixmap.search_signal_extremes_by_ax(
            self.plot.plot.viewport().grab(), self.channel_37.color.name(), "x"
        )

        # Evaluate
        self.assertLess(old_from_to_y_channel_36[0], new_from_to_y_channel_36[0])
        self.assertLess(old_from_to_y_channel_36[1], new_from_to_y_channel_36[1])
        self.assertGreater(old_from_to_x_channel_36[0], new_from_to_x_channel_36[0])
        self.assertGreater(old_from_to_x_channel_36[1], new_from_to_x_channel_36[1])

        self.assertGreater(old_from_to_y_channel_37[0], new_from_to_y_channel_37[0])
        self.assertGreater(old_from_to_y_channel_37[1], new_from_to_y_channel_37[1])
        self.assertLess(old_from_to_x_channel_37[0], new_from_to_x_channel_37[0])
        self.assertLess(old_from_to_x_channel_37[1], new_from_to_x_channel_37[1])

    def test_Plot_PlotGraphics_Shortcut_Key_H(self):
        """
        Test Scope:
            Check if honeywell is the same every time key "H" is pressed.
        Events:
            - Open 'FileWidget' with valid measurement.
            - Display 1 signal on plot
            - Select signal
            - Press "H"
            - Press "O"
            - Press "H"
        Evaluate:
            - Evaluate that plot is not black
            - Evaluate that the range of x-axis was changed after pressing key "H"
            - Evaluate that the range of x-axis was changed after pressing key "O"
            - Evaluate that the range of x-axis is same after pressing key "H" second time
                    with range of x-axis after pressing key "H" first time
        """
        delta_x_range = self.plot.plot.x_range[1] - self.plot.plot.x_range[0]
        # Press "H"
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_H)
        self.avoid_blinking_issue(self.plot.channel_selection)
        delta_x_honey_range = self.plot.plot.x_range[1] - self.plot.plot.x_range[0]

        # Evaluate
        self.assertNotEqual(delta_x_range, delta_x_honey_range)

        # Press "O"
        QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_O)
        self.processEvents()

        # Evaluate
        self.assertNotEqual(delta_x_honey_range, self.plot.plot.x_range[1] - self.plot.plot.x_range[0])

        # Press H
        QtTest.QTest.keyClick(self.plot.plot, QtCore.Qt.Key_H)
        self.avoid_blinking_issue(self.plot.channel_selection)

        # Evaluate
        self.assertEqual(delta_x_honey_range, self.plot.plot.x_range[1] - self.plot.plot.x_range[0])

    def test_Plot_PlotGraphics_Shortcut_Key_W(self):
        """
        Check if the signal is fitted properly after pressing key "W".
        Events:
            - Open 'FileWidget' with valid measurement.
            - Create a plot window and load 2 signals
            - Press key "I"
            - Press key "W"
        Evaluate:
            - Evaluate that window is created
            - Evaluate that there is at least one column with first signal color
            - Evaluate first and last columns where is first signal:
                > first column after pressing "I" is full black => signal colors are not there
                > signal is zoomed => is extended to left side => last column contain signal color
            - Evaluate that after pressing key "W" from first to last column is displayed signal
        """
        self.addChannelsToPlot([35])
        self.channel_35 = self.channels[0]

        # check if the grid is available
        if not self.plot.hide_axes_btn.isFlat():
            QtTest.QTest.mouseClick(self.plot.hide_axes_btn, QtCore.Qt.MouseButton.LeftButton)

        # search first and last column where is displayed first signal
        extremesOfChannel_35 = Pixmap.search_signal_extremes_by_ax(
            self.plot.plot.viewport().grab(), self.channel_35.color.name(), "x"
        )
        # Evaluate that there are extremes of first signal
        self.assertTrue(extremesOfChannel_35)
        # Press "I"
        QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_I)
        self.processEvents()

        # save left and right pixel column
        xLeftColumn = self.plot.plot.viewport().grab(
            QtCore.QRect(extremesOfChannel_35[0], 0, 1, self.plot.plot.height())
        )
        xRightColumn = self.plot.plot.viewport().grab(
            QtCore.QRect(extremesOfChannel_35[1], 0, 1, self.plot.plot.height())
        )
        self.assertTrue(Pixmap.is_black(xLeftColumn))
        self.assertTrue(Pixmap.has_color(xRightColumn, self.channel_35.color.name()))
        # Press "W"
        QtTest.QTest.keyClick(self.plot.plot.viewport(), QtCore.Qt.Key_W)
        self.processEvents()
        # Select all columns from left to right
        for x in range(self.plot.plot.height() - 1):
            column = self.plot.plot.viewport().grab(QtCore.QRect(x, 0, 1, self.plot.plot.height()))
            if x < extremesOfChannel_35[0] - 1:
                self.assertTrue(Pixmap.is_black(column), f"column {x} is not black")
            elif extremesOfChannel_35[0] <= x <= extremesOfChannel_35[1]:
                self.assertTrue(
                    Pixmap.has_color(column, self.channel_35.color.name()),
                    f"column {x} doesn't have {self.channel_35.name} color",
                )
            else:
                self.assertTrue(Pixmap.is_black(column), f"column {x} is not black")

    def test_Plot_PlotGraphics_Shortcut_Key_Insert(self):
        """
        Test Scope:
            Check Insert key shortcut action
        Events:
            - Open 'FileWidget' with valid measurement.
            - Press Insert with preconditions:
                > There is no user defined functon
                > There is user defined functon, button Cancel or "X" was pressed
                > There is user defined function, button Apply was pressed
        Evaluate:
            - Evaluate that channel selection area is empty
        Evaluate (0):
            - Evaluate that warning message box was triggered after pressing key insert
            - Evaluate displayed warning message
            - Evaluate that channel selection area is empty
        Evaluate (1):
            - Evaluate that channel selection area is empty
            - Evaluate that DefineChannel object was called
        Evaluate (2):
            - Evaluate that there is one channel in channel selection area
            - Evaluate that the name of this channel is correct
            - Evaluate that DefineChannel object was called
        """
        # Evaluate precondition
        self.assertEqual(0, self.plot.channel_selection.topLevelItemCount())

        with self.subTest("_0_test_warning_no_user_function_defined"):
            warnings_msgs = [
                "Cannot add computed channel",
                "There is no user defined function. Create new function using the Functions Manger (F6)",
            ]
            # mock for warning message box
            with mock.patch("asammdf.gui.widgets.plot.MessageBox.warning") as mo_waring:
                # Press key Insert
                QtTest.QTest.keyClick(self.plot.channel_selection, QtCore.Qt.Key_Insert)
            # Evaluate
            self.assertEqual(0, self.plot.channel_selection.topLevelItemCount())
            mo_waring.assert_called()
            for w in warnings_msgs:
                self.assertIn(w, mo_waring.call_args.args)

        with self.subTest("-1_test_cancel_dlg_with_user_function_defined"):
            file_name = "test_insert_cfg.dspf"
            file_path = os.path.join(self.resource, file_name)
            self.load_display_file(file_path)
            self.plot = self.widget.mdi_area.subWindowList()[0].widget()
            with mock.patch("asammdf.gui.widgets.plot.DefineChannel") as mo_DefineChannel:
                # Press key Insert
                QtTest.QTest.keyClick(self.plot.channel_selection, QtCore.Qt.Key_Insert)

            # Evaluate
            self.assertEqual(0, self.plot.channel_selection.topLevelItemCount())
            mo_DefineChannel.assert_called()

        with self.subTest("_2_test_apply_dlg_with_user_function_defined"):
            file_name = "test_insert_cfg.dspf"
            file_path = os.path.join(self.resource, file_name)
            self.load_display_file(file_path)
            self.plot = self.widget.mdi_area.subWindowList()[0].widget()
            computed_channel = {
                "type": "channel",
                "common_axis": False,
                "individual_axis": False,
                "enabled": True,
                "mode": "phys",
                "fmt": "{:.3f}",
                "format": "phys",
                "precision": 3,
                "flags": 0,
                "ranges": [],
                "unit": "",
                "computed": True,
                "color": "#994380",
                "uuid": "525ad72a531a",
                "origin_uuid": "812d7b792168",
                "group_index": -1,
                "channel_index": -1,
                "name": self.id(),
                "computation": {
                    "args": {},
                    "type": "python_function",
                    "definition": "",
                    "channel_name": "Function_728d4a149b44",
                    "function": "Function1",
                    "channel_unit": "",
                    "channel_comment": "",
                    "triggering": "triggering_on_all",
                    "triggering_value": "all",
                    "computation_mode": "sample_by_sample",
                },
            }
            with mock.patch("asammdf.gui.widgets.plot.DefineChannel") as mo_DefineChannel:
                mo_DefineChannel.return_value.result = computed_channel
                # Press key Insert
                QtTest.QTest.keyClick(self.plot.channel_selection, QtCore.Qt.Key_Insert)

            # Evaluate
            self.assertEqual(1, self.plot.channel_selection.topLevelItemCount())
            self.assertEqual(self.plot.channel_selection.topLevelItem(0).name, self.id())
            mo_DefineChannel.assert_called()
