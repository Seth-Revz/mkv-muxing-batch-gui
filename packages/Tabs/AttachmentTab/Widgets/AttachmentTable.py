import sys
import PySide2
from PySide2.QtCore import Signal
from PySide2.QtGui import Qt, QColor
from PySide2.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem

from packages.Startup.InitializeScreenResolution import screen_size
from packages.Tabs.GlobalSetting import GlobalSetting, sort_names_like_windows
from packages.Widgets.TableWidget import TableWidget


class AttachmentTable(TableWidget):
    update_unchecked_attachment_signal = Signal(str)
    update_checked_attachment_signal = Signal(str)
    drop_folder_and_files_signal = Signal(list)

    def __init__(self):
        super().__init__()
        self.checking_row_updates = False
        self.setColumnCount(2)
        self.setRowCount(0)
        self.column_ids = {
            "Name": 0,
            "Size": 1,
        }
        self.disable_table_bold_column()
        self.disable_table_edit()
        self.force_select_whole_row()
        self.force_single_row_selection()
        self.make_column_expand_as_possible(column_index=self.column_ids["Name"])
        self.set_row_height(new_height=screen_size.height() // 27)
        self.setup_columns()
        self.itemChanged.connect(self.update_checked_attachments_state)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        paths_to_add = []
        for url in urls:
            if sys.platform == "win32":
                current_path = url.path()[1:]
            else:
                current_path = url.path()
            paths_to_add.append(current_path)
        self.drop_folder_and_files_signal.emit(sort_names_like_windows(paths_to_add))

    def disable_table_bold_column(self):
        self.horizontalHeader().setHighlightSections(False)

    def disable_table_edit(self):
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def force_select_whole_row(self):
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def make_column_expand_as_possible(self, column_index):
        header = self.horizontalHeader()
        header.setSectionResizeMode(column_index, QHeaderView.Stretch)

    def force_single_row_selection(self):
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def setup_columns(self):
        self.set_column_name(column_index=self.column_ids["Name"], name="Name")
        self.set_column_name(column_index=self.column_ids["Size"], name="Size")

    def set_column_name(self, column_index, name, alignment=Qt.AlignLeft):
        column = QTableWidgetItem(name)
        column.setTextAlignment(alignment)
        self.setHorizontalHeaderItem(column_index, column)

    def set_row_height(self, new_height):
        self.verticalHeader().setDefaultSectionSize(new_height)

    def resize_2nd_column(self):
        self.setColumnWidth(self.column_ids["Size"],
                            min(self.columnWidth(self.column_ids["Name"]) // 2, screen_size.width() // 14))

    def resizeEvent(self, event: PySide2.QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.resize_2nd_column()

    def show_files_list(self, files_names_list, files_names_checked_list, files_size_list):
        self.checking_row_updates = False
        self.setRowCount(len(files_names_list))
        self.set_row_height(new_height=screen_size.height() // 27)
        for i in range(len(files_names_list)):
            self.set_row_number(row_number=i + 1, row_index=i)
            self.set_row_file_name(file_name=files_names_list[i], row_index=i, is_checked=files_names_checked_list[i])
            self.set_row_file_size(file_size=files_size_list[i], row_index=i)
            if files_names_checked_list[i]:
                self.update_row_text_color(row_index=i, color_string="#FFFFFF")
            else:
                self.update_row_text_color(row_index=i, color_string="#787878")
        self.show()
        self.checking_row_updates = True

    def set_row_number(self, row_number, row_index):
        row_number_item = QTableWidgetItem(str(row_number))
        row_number_item.setTextAlignment(Qt.AlignCenter)
        self.setVerticalHeaderItem(row_index, row_number_item)

    def set_row_file_size(self, file_size, row_index):
        file_size_item = QTableWidgetItem(file_size)
        self.setItem(row_index, self.column_ids["Size"], file_size_item)

    def set_row_file_name(self, file_name, row_index, is_checked=True):
        file_name_item = QTableWidgetItem(" " + file_name)
        if is_checked:
            file_name_item.setCheckState(Qt.Checked)
        else:
            file_name_item.setCheckState(Qt.Unchecked)
        self.setItem(row_index, self.column_ids["Name"], file_name_item)

    def clear_table(self):
        self.setRowCount(0)
        self.clearSelection()

    def update_checked_attachments_state(self, item: QTableWidgetItem):
        attachment_index = item.row()
        if self.checking_row_updates:
            self.checking_row_updates = False
            self.update_selected_row(row_index=attachment_index)
            if attachment_index < len(GlobalSetting.ATTACHMENT_FILES_CHECKING_LIST):
                if item.checkState() == Qt.Unchecked:
                    GlobalSetting.ATTACHMENT_FILES_CHECKING_LIST[attachment_index] = False
                    self.update_row_text_color(row_index=attachment_index, color_string="#787878")
                    self.update_unchecked_attachment_signal.emit(
                        GlobalSetting.ATTACHMENT_FILES_ABSOLUTE_PATH_LIST[attachment_index])
                elif item.checkState() == Qt.Checked:
                    GlobalSetting.ATTACHMENT_FILES_CHECKING_LIST[attachment_index] = True
                    self.update_row_text_color(row_index=attachment_index, color_string="#FFFFFF")
                    self.update_checked_attachment_signal.emit(
                        GlobalSetting.ATTACHMENT_FILES_ABSOLUTE_PATH_LIST[attachment_index])
            self.checking_row_updates = True

    def update_row_text_color(self, row_index, color_string):
        new_color = QColor(color_string)
        self.item(row_index, self.column_ids["Name"]).setTextColor(new_color)
        self.item(row_index, self.column_ids["Size"]).setTextColor(new_color)

    def update_selected_row(self, row_index):
        self.selectRow(row_index)
