# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'visualization/ui_files/saveImg.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 500)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.plot_layout = QtWidgets.QHBoxLayout()
        self.plot_layout.setObjectName("plot_layout")
        self.gridLayout_2.addLayout(self.plot_layout, 0, 0, 1, 1)
        self.grid_rt = QtWidgets.QGridLayout()
        self.grid_rt.setObjectName("grid_rt")
        self.titleInput = QtWidgets.QLineEdit(Form)
        self.titleInput.setObjectName("titleInput")
        self.grid_rt.addWidget(self.titleInput, 3, 1, 1, 1)
        self.lineThickInput = QtWidgets.QComboBox(Form)
        self.lineThickInput.setObjectName("lineThickInput")
        self.grid_rt.addWidget(self.lineThickInput, 1, 1, 1, 1)
        self.okBtn = QtWidgets.QDialogButtonBox(Form)
        self.okBtn.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.okBtn.setObjectName("okBtn")
        self.grid_rt.addWidget(self.okBtn, 4, 1, 1, 1)
        self.annCbox = QtWidgets.QCheckBox(Form)
        self.annCbox.setObjectName("annCbox")
        self.grid_rt.addWidget(self.annCbox, 0, 0, 1, 2)
        self.lineLabel = QtWidgets.QLabel(Form)
        self.lineLabel.setObjectName("lineLabel")
        self.grid_rt.addWidget(self.lineLabel, 1, 0, 1, 1)
        self.textSizeInput = QtWidgets.QComboBox(Form)
        self.textSizeInput.setObjectName("textSizeInput")
        self.grid_rt.addWidget(self.textSizeInput, 2, 1, 1, 1)
        self.textLabel = QtWidgets.QLabel(Form)
        self.textLabel.setObjectName("textLabel")
        self.grid_rt.addWidget(self.textLabel, 2, 0, 1, 1)
        self.titleCbox = QtWidgets.QCheckBox(Form)
        self.titleCbox.setObjectName("titleCbox")
        self.grid_rt.addWidget(self.titleCbox, 3, 0, 1, 1)
        self.gridLayout_2.addLayout(self.grid_rt, 0, 1, 1, 1)

        self.retranslateUi(Form)
        self.annCbox.toggled.connect(Form.ann_checked)
        self.titleCbox.toggled.connect(Form.title_checked)
        self.lineThickInput.currentIndexChanged['int'].connect(Form.chg_line_thick)
        self.textSizeInput.currentIndexChanged['int'].connect(Form.chg_text_size)
        self.titleInput.textChanged.connect(Form.title_changed)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Export Image Options"))
        self.annCbox.setText(_translate("Form", "Show annotations"))
        self.lineLabel.setText(_translate("Form", "Line thickness"))
        self.textLabel.setText(_translate("Form", "Font size"))
        self.titleCbox.setText(_translate("Form", "Show title"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

