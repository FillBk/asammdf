#!/usr/bin/env python\

import pathlib
from test.asammdf.gui.widgets.test_BaseFileWidget import TestFileWidget
from unittest import mock

from PySide6 import QtCore, QtGui, QtTest


class TestFileWidgetShortcuts(TestFileWidget):
    """
    Events:
        Open measurement file "ASAP2_Demo_V171.mf4" on FileWidget
    """

    def setUp(self):
        # Open measurement file
        measurement_file = str(pathlib.Path(TestFileWidget.resource, "ASAP2_Demo_V171.mf4"))
        self.setUpFileWidget(measurement_file=measurement_file, default=True)

    def test_FileWidget_Shortcut_Key_Shift_Alt_F(self):
        """
        Test Scope:
            Check if sub-windows frame was toggled after pressing keys "Shift+Alt+F"
        Events:
            - Press twice "Shift+Alt+F"
        Evaluate:
            - Evaluate that by default sub-windows are not frameless
            - Evaluate that sub-windows is frameless after pressing "Shift+Alt+F" first time
            - Evaluate that sub-windows is not frameless after pressing "Shift+Alt+F" second time
        """
        # Evaluate
        self.assertFalse(self.widget._frameless_windows)
        # Press Shift+Alt+F first time
        QtTest.QTest.keySequence(self.widget, QtGui.QKeySequence("Shift+Alt+F"))
        # Evaluate
        self.assertTrue(self.widget._frameless_windows)
        # Press Shift+Alt+F second time
        QtTest.QTest.keySequence(self.widget, QtGui.QKeySequence("Shift+Alt+F"))
        # Evaluate
        self.assertFalse(self.widget._frameless_windows)

    def test_FileWidget_Shortcut_Key_Shift_V(self):
        """
        Test Scope:
            Check if object tile_vertically() from QMdiArea module of PySide6.QtWidgets was called
                after pressing the combination of keys "Shift+V"
        Events:
            - Press "Shift+V"
        Evaluate (0):
            - Evaluate that the tile_vertically() object was called"
        """
        # mock for tile_vertically object
        with mock.patch("asammdf.gui.widgets.file.MdiAreaWidget.tile_vertically") as mo_tile_vertically:
            # Press Shift+V
            QtTest.QTest.keySequence(self.widget, QtGui.QKeySequence("Shift+V"))
        # Evaluate
        mo_tile_vertically.assert_called()

    def test_FileWidget_Shortcut_Key_Shift_H(self):
        """
        Test Scope:
            Check if object tile_horizontally() from QMdiArea module of PySide6.QtWidgets was called
                after pressing the combination of keys "Shift+H"
        Events:
            - Press "Shift+H"
        Evaluate (0):
            - Evaluate that the tile_horizontally() object was called"
        """
        # mock for tile_horizontally object
        with mock.patch("asammdf.gui.widgets.file.MdiAreaWidget.tile_horizontally") as mo_tile_horizontally:
            # Press Shift+H
            QtTest.QTest.keySequence(self.widget, QtGui.QKeySequence("Shift+H"))
        # Evaluate
        mo_tile_horizontally.assert_called()

    def test_FileWidget_Shortcut_Key_Shift_C(self):
        """
        Test Scope:
            Check if object cascadeSubWindows() from C module of PySide6.QtWidgets was called
                after pressing the combination of keys "Shift+C"
        Events:
            - Press "Shift+C"
        Evaluate (0):
            - Evaluate that only cascadeSubWindows() object was called"
        """
        # mock for cascadeSubWindows object
        with mock.patch("asammdf.gui.widgets.file.MdiAreaWidget.cascadeSubWindows") as mo_cascadeSubWindows:
            # Press Shift+C
            QtTest.QTest.keySequence(self.widget, QtGui.QKeySequence("Shift+C"))
        # Evaluate
        mo_cascadeSubWindows.assert_called()

    def test_FileWidget_Shortcut_Key_Shift_T(self):
        """
        Test Scope:
            Check if object tileSubWindows() from QMdiArea module of PySide6.QtWidgets was called
                after pressing the combination of keys "Shift+T"
        Events:
            - Press "Shift+T"
        Evaluate (0):
            - Evaluate that only tileSubWindows() object was called"
        """
        # mock for tileSubWindows object
        with mock.patch("asammdf.gui.widgets.file.MdiAreaWidget.tileSubWindows") as mo_tileSubWindows:
            # Press Shift+T
            QtTest.QTest.keySequence(self.widget, QtGui.QKeySequence("Shift+T"))
        # Evaluate
        mo_tileSubWindows.assert_called()

    def test_FileWidget_Shortcut_Key_Shift_L(self):
        """
        Test Scope:
            Check if by pressing the combination of keys "Shift+L", visibility of channel list is changed
        Events:
            - Press twice combination"Shift+L"
        Evaluate:
            - Evaluate that channel list is visible by default
            - Evaluate that channel list is hidden after pressing first time "Shift+L"
            - Evaluate that channel list is visible after pressing second time "Shift+L"
        """
        # Evaluate
        self.assertTrue(self.widget.channel_view.isVisible())
        # Press "Shift+L" first time
        QtTest.QTest.keySequence(self.widget, QtGui.QKeySequence("Shift+L"))
        # Evaluate
        self.assertFalse(self.widget.channel_view.isVisible())
        # Press "Shift+L" second time
        QtTest.QTest.keySequence(self.widget, QtGui.QKeySequence("Shift+L"))
        # Evaluate
        self.assertTrue(self.widget.channel_view.isVisible())

    def test_FileWidget_Shortcut_Key_Period(self):
        """
        Test Scope:
            Check if set_line_style method is called after pressing key Period
        Events:
            - Press key "Period" <<.>>
        Evaluate:
            - Evaluate that set_line_style object was called
        """
        # mock for set_line_style object
        with mock.patch.object(self.widget, "set_line_style") as mo_set_line_style:
            # Event
            QtTest.QTest.keyClick(self.widget, QtCore.Qt.Key_Period)
        # Evaluate
        mo_set_line_style.assert_called()
