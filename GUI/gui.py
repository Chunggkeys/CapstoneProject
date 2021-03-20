from PyQt5 import QtWidgets, uic, QtGui
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
import numpy as np

from control import ControlModule
from output import OutputModule

paramMappings = {
    'l': 'Length',
    't': 'Thickness',
    'd': 'Deformation',
    'n': 'Number of Cycles',
    'p1': 'Potentiometer 1',
    'p2': 'Potentiometer 2',
    'p3': 'Potentiometer 3',
    'p4': 'Potentiometer 4'
}

maxParamMappings = {
    'l': str(ControlModule.MAX_LENGTH) + ' mm',
    't': str(ControlModule.MAX_THICK) + ' mm',
    'd': str(ControlModule.MAX_DEF) + ' mm',
    'n': str(ControlModule.MAX_CYCLES),
    'p1': str(ControlModule.MAX_POT) + ' \u03A9',
    'p2': str(ControlModule.MAX_POT) + ' \u03A9',
    'p3': str(ControlModule.MAX_POT) + ' \u03A9',
    'p4': str(ControlModule.MAX_POT) + ' \u03A9'
}

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('mainwindow.ui', self)

        #Initialize button behaviour
        self.btn_submit.clicked.connect(self.submit)
        self.btn_start.clicked.connect(self.toggleStart)
        self.btn_start.setEnabled(False)

        #set input validators
        intValidator = QtGui.QIntValidator()
        doubleValidator = QtGui.QDoubleValidator()

        self.input_length.setValidator(doubleValidator)
        self.input_thick.setValidator(doubleValidator)
        self.input_def.setValidator(doubleValidator)
        self.input_nCycles.setValidator(intValidator)
        self.input_ptt1.setValidator(doubleValidator)
        self.input_ptt2.setValidator(doubleValidator)
        self.input_ptt3.setValidator(doubleValidator)
        self.input_ptt4.setValidator(doubleValidator)

        #Initialize graph widgets
        self.graph_def.setLabel('bottom', 'Time', 's')
        self.graph_def.setLabel('left', 'Motor Position', 'mm')
        self.graph_def.setYRange(0, 1, padding=0.1)

        self.graph_resist.setLabel('bottom', 'Time', 's')
        self.graph_resist.setLabel('left', 'Resistance', '\u03A9')
        self.graph_resist.setYRange(0, 2, padding=0.1)

        self.curveDef = self.graph_def.plot()
        self.curveResist = self.graph_resist.plot()

        #initialize dialog box
        self.messageBox = QtWidgets.QMessageBox()

        #Initialize timer
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)

        #initialize event loop
        self.eventTimer = pg.QtCore.QTimer()
        self.eventTimer.timeout.connect(self.checkEvents)
        self.eventTimer.start(50)
    
    def checkEvents(self):
        if not self.messageBox.isVisible():
            message = OutputModule.readMessages()
            if message:
                self.displayMessage(message, 'info')

    def update(self):
        error = OutputModule.getError()
        if error:
            self.timer.stop()
            self.displayMessage(error, 'error')
        else:
            [ptr, x, dataDef, dataResist] = OutputModule.getData()
            if (ptr < OutputModule.DATA_BUFF_SIZE):
                self.curveDef.setData(x[:ptr], dataDef[:ptr])
                self.curveResist.setData(x[:ptr], dataDef[:ptr])
            else:
                self.curveDef.setData(x, dataDef)
                self.curveResist.setData(x, dataResist)

    def submit(self):
        params = self.parseInputs()

        if params:
            invalid = ControlModule.validateParams(params)

            if not invalid:
                ControlModule.setDataBuffer(params)
                self.graph_def.setYRange(0, params['d'], padding=0.1)
                self.btn_start.setEnabled(True)
            else: 
                errorMessage = ''
                for p in invalid:
                    errorMessage = errorMessage + paramMappings[p] + ' must be positive and less than ' + maxParamMappings[p] + '\n'
                self.displayMessage(errorMessage, 'warning')
                self.btn_start.setEnabled(False)
        
    def parseInputs(self):
        l = self.input_length.text()
        t = self.input_thick.text()
        d = self.input_def.text()
        n = self.input_nCycles.text()
        p1 = self.input_ptt1.text()
        p2 = self.input_ptt2.text()
        p3 = self.input_ptt3.text()
        p4 = self.input_ptt4.text()

        if (not l or not t or not d or not n or not
            p1 or not p2 or not p3 or not p4):
            self.displayMessage('Cannot leave field empty', 'warning')
            return {}
        else:
            return {
                'l': float(l), 
                't': float(t), 
                'd': float(d), 
                'n': int(n), 
                'p1': float(p1), 
                'p2': float(p2), 
                'p3': float(p3), 
                'p4': float(p4)
            }


    def toggleStart(self):
        if not self.btn_start.isChecked():
            ControlModule.setRunning(False)
            self.timer.stop()
            self.btn_start.setText('Begin Cycles')
        else:
            ControlModule.setRunning(True)
            self.timer.start(50)
            self.btn_start.setText('Stop')
            self.input_length.setReadOnly(True)
            self.input_thick.setReadOnly(True)
            self.input_def.setReadOnly(True)
            self.input_nCycles.setReadOnly(True)
            self.input_ptt1.setReadOnly(True)
            self.input_ptt2.setReadOnly(True)
            self.input_ptt3.setReadOnly(True)
            self.input_ptt4.setReadOnly(True)

    def displayMessage(self, message, type):
        msgType = QtWidgets.QMessageBox.Information
        if type == 'error':
            msgType = QtWidgets.QMessageBox.Critical
        elif type == 'warning':
            msgType = QtWidgets.QMessageBox.Warning

        self.messageBox.setIcon(msgType)
        self.messageBox.setText(message)
        self.messageBox.setWindowTitle(type)
        self.messageBox.exec()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()