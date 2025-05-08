from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QStyle

class LinesToolbar:
    def __init__(self, parent=None, font_family="Vazir"):
        self.widget = QToolBar()
        self.widget.setFont(QFont(font_family, 18))
        self.widget.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # Toolbar actions
        self.add_action = QAction(QIcon(self.widget.style().standardIcon(QStyle.SP_FileDialogNewFolder)), "افزودن خط جدید", parent)
        self.delete_action = QAction(QIcon(self.widget.style().standardIcon(QStyle.SP_TrashIcon)), "حذف", parent)
        self.edit_action = QAction(QIcon(self.widget.style().standardIcon(QStyle.SP_FileDialogContentsView)), "ویرایش", parent)
        self.import_excel_action = QAction(QIcon(self.widget.style().standardIcon(QStyle.SP_FileDialogStart)), "ورود اطلاعات از اکسل", parent)
        self.report_action = QAction(QIcon(self.widget.style().standardIcon(QStyle.SP_FileDialogDetailedView)), "خروجی گرفتن", parent)
        self.back_action = QAction(QIcon(self.widget.style().standardIcon(QStyle.SP_ArrowBack)), "برگشت", parent)

        # Add actions to toolbar
        self.widget.addAction(self.add_action)
        self.widget.addSeparator().setText("|")
        self.widget.addAction(self.delete_action)
        self.widget.addSeparator().setText("|")
        self.widget.addAction(self.edit_action)
        self.widget.addSeparator().setText("|")
        self.widget.addAction(self.import_excel_action)
        self.widget.addSeparator().setText("|")
        self.widget.addAction(self.report_action)
        self.widget.addSeparator().setText("|")
        self.widget.addAction(self.back_action)
