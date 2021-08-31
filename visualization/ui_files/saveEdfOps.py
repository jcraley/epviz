# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'saveEdfOps.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_saveToEdf(object):
    def setupUi(self, saveToEdf):
        saveToEdf.setObjectName("saveToEdf")
        saveToEdf.setWindowModality(QtCore.Qt.NonModal)
        saveToEdf.resize(200, 171)
        self.gridLayoutWidget = QtWidgets.QWidget(saveToEdf)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 181, 151))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.layout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName("layout")
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.layout.addWidget(self.label, 0, 0, 1, 1)
        self.btn_editFields = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn_editFields.setObjectName("btn_editFields")
        self.layout.addWidget(self.btn_editFields, 3, 0, 1, 1)
        self.btn_anonAndSave = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn_anonAndSave.setObjectName("btn_anonAndSave")
        self.layout.addWidget(self.btn_anonAndSave, 4, 0, 1, 1)
        self.cbox_anon = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.cbox_anon.setObjectName("cbox_anon")
        self.layout.addWidget(self.cbox_anon, 2, 0, 1, 1)
        self.cbox_orig = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.cbox_orig.setChecked(True)
        self.cbox_orig.setObjectName("cbox_orig")
        self.layout.addWidget(self.cbox_orig, 1, 0, 1, 1)

        self.retranslateUi(saveToEdf)
        QtCore.QMetaObject.connectSlotsByName(saveToEdf)

    def retranslateUi(self, saveToEdf):
        _translate = QtCore.QCoreApplication.translate
        saveToEdf.setWindowTitle(_translate("saveToEdf", "Save to EDF"))
        self.label.setText(_translate("saveToEdf", "Header for saved file:"))
        self.btn_editFields.setText(_translate("saveToEdf", "Edit header fields..."))
        self.btn_anonAndSave.setText(_translate("saveToEdf", "Update header and save"))
        self.cbox_anon.setText(_translate("saveToEdf", "Anonymize all fields"))
        self.cbox_orig.setText(_translate("saveToEdf", "Same as original file"))

