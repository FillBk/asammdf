from natsort import natsorted
from PySide6 import QtCore, QtGui, QtWidgets


class MinimalListWidget(QtWidgets.QListWidget):
    itemsDeleted = QtCore.Signal(list)
    itemsPasted = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

        self.setAlternatingRowColors(True)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

        self.setAcceptDrops(True)
        self.show()

        self.itemSelectionChanged.connect(self.item_selection_changed)

        self.minimal_menu = False
        self.all_texts = False
        self.placeholder_text = ""

        self.user_editable = True

    def item_selection_changed(self, item=None):
        try:
            selection = list(self.selectedItems())
            for row in range(self.count()):
                item = self.item(row)
                if item in selection:
                    self.itemWidget(item).set_selected(True)
                else:
                    self.itemWidget(item).set_selected(False)
        except:
            pass

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if key == QtCore.Qt.Key.Key_Delete and self.user_editable:
            selected_items = self.selectedItems()
            deleted = []

            if self.all_texts:
                to_delete = set()
                for item in selected_items:
                    row = self.row(item)
                    deleted.append(row)
                    item_widget = self.itemWidget(item)
                    if hasattr(item_widget, "disconnect_slots"):
                        item_widget.disconnect_slots()
                    to_delete.add(item.text())

                all_texts = set()

                count = self.count()
                for row in range(count):
                    item = self.item(row)
                    all_texts.add(item.text())

                self.clear()
                self.addItems(natsorted(all_texts - to_delete))

            else:
                for item in selected_items:
                    row = self.row(item)
                    deleted.append(row)
                    item_widget = self.itemWidget(item)
                    if hasattr(item_widget, "disconnect_slots"):
                        item_widget.disconnect_slots()
                    self.takeItem(row)

            if deleted:
                self.itemsDeleted.emit(deleted)

            event.accept()

        elif key == QtCore.Qt.Key.Key_C and modifiers == QtCore.Qt.KeyboardModifier.ControlModifier:
            text = []
            for item in self.selectedItems():
                try:
                    text.append(self.itemWidget(item).text())
                except:
                    text.append(item.text())

            if text:
                text = "\n".join(text)
            else:
                text = ""

            QtWidgets.QApplication.instance().clipboard().setText(text)
            event.accept()

        elif (
            key == QtCore.Qt.Key.Key_V
            and modifiers == QtCore.Qt.KeyboardModifier.ControlModifier
            and self.user_editable
        ):
            lines = QtWidgets.QApplication.instance().clipboard().text().splitlines()
            if lines:
                try:
                    self.addItems(lines)
                    self.itemsPasted.emit()
                except:
                    pass
            event.accept()
        else:
            super().keyPressEvent(event)

    def open_menu(self, position):
        menu = QtWidgets.QMenu()

        if self.minimal_menu:
            if self.count() > 0:
                menu.addAction(self.tr(f"{self.count()} items in the list"))
                menu.addSeparator()
                menu.addAction(self.tr("Delete (Del)"))
            else:
                return
        else:
            if self.count() == 0:
                menu.addAction(self.tr(f"{self.count()} items in the list"))
                menu.addSeparator()
                if self.user_editable:
                    menu.addAction(self.tr("Paste names (Ctrl+V)"))
            else:
                menu.addAction(self.tr(f"{self.count()} items in the list"))
                menu.addSeparator()
                menu.addAction(self.tr("Copy names (Ctrl+C)"))
                if self.user_editable:
                    menu.addAction(self.tr("Paste names (Ctrl+V)"))
                    menu.addSeparator()
                    menu.addAction(self.tr("Delete (Del)"))

        action = menu.exec_(self.viewport().mapToGlobal(position))

        if action is None:
            return

        if action.text() == "Delete (Del)":
            event = QtGui.QKeyEvent(
                QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_Delete, QtCore.Qt.KeyboardModifier.NoModifier
            )
            self.keyPressEvent(event)
        elif action.text() == "Copy names (Ctrl+C)":
            event = QtGui.QKeyEvent(
                QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_C, QtCore.Qt.KeyboardModifier.ControlModifier
            )
            self.keyPressEvent(event)
        elif action.text() == "Paste names (Ctrl+V)":
            event = QtGui.QKeyEvent(
                QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_V, QtCore.Qt.KeyboardModifier.ControlModifier
            )
            self.keyPressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0 and self.placeholder_text:
            painter = QtGui.QPainter(self.viewport())
            painter.save()
            col = self.palette().placeholderText().color()
            painter.setPen(col)
            fm = self.fontMetrics()
            elided_text = fm.elidedText(
                self.placeholder_text, QtCore.Qt.TextElideMode.ElideRight, self.viewport().width()
            )
            painter.drawText(self.viewport().rect(), QtCore.Qt.AlignmentFlag.AlignCenter, elided_text)
            painter.restore()
