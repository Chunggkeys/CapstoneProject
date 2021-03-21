from PyQt5 import QtWidgets, uic, QtGui
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
from constants import *

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
    'l': str(MAX_LENGTH) + ' mm',
    't': str(MAX_THICK) + ' mm',
    'd': str(MAX_DEF) + ' mm',
    'n': str(MAX_CYCLES),
    'p1': str(MAX_POT) + ' \u03A9',
    'p2': str(MAX_POT) + ' \u03A9',
    'p3': str(MAX_POT) + ' \u03A9',
    'p4': str(MAX_POT) + ' \u03A9'
}

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self, control, output, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('mainwindow.ui', self)

        #ui title and positioning
        self.setWindowTitle("Mesomat Strain Apparatus")
        self.setGeometry(0,0,800,479)

        #initialize modules
        self.control = control
        self.output = output

        #Initialize button behaviour
        self.btn_clear.clicked.connect(self.clearInputs)
        self.btn_start.clicked.connect(self.toggleStart)

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
        self.graph_pos.setLabel('bottom', 'Time', 's')
        self.graph_pos.setLabel('left', 'Motor Position', 'mm')
        self.graph_pos.setYRange(0, 1, padding=0.1)

        self.graph_resist.setLabel('bottom', 'Time', 's')
        self.graph_resist.setLabel('left', 'Resistance', '\u03A9')
        # self.graph_resist.setYRange(0, 1.2, padding=0.1)

        self.curvePos = self.graph_pos.plot()

        self.curveResist0 = self.graph_resist.plot()
        self.curveResist1 = self.graph_resist.plot()
        self.curveResist2 = self.graph_resist.plot()
        self.curveResist3 = self.graph_resist.plot()

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
            message = self.output.readMessages()
            if message:
                self.displayMessage(message, 'info')

    def update(self):
        error = self.output.getError()
        if error:
            self.timer.stop()
            self.displayMessage(error, 'error')
        else:
            [ptr, x, dataPos, dataResist] = self.output.getData()
            if (ptr < DATA_BUFF_SIZE):
                self.curvePos.setData(x[:ptr], dataPos[:ptr])
                self.curveResist0.setData(x[:ptr], dataResist[0][:ptr])
                self.curveResist1.setData(x[:ptr], dataResist[1][:ptr])
                self.curveResist2.setData(x[:ptr], dataResist[2][:ptr])
                self.curveResist3.setData(x[:ptr], dataResist[3][:ptr])
            else:
                self.curvePos.setData(x, dataPos)
                self.curveResist0.setData(x, dataResist[0])
                self.curveResist1.setData(x, dataResist[1])
                self.curveResist2.setData(x, dataResist[2])
                self.curveResist3.setData(x, dataResist[3])
        
    def clearInputs(self):
        self.input_length.clear()
        self.input_thick.clear()
        self.input_def.clear()
        self.input_nCycles.clear()
        self.input_ptt1.clear()
        self.input_ptt2.clear()
        self.input_ptt3.clear()
        self.input_ptt4.clear()

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
            self.control.setStopPressed(False)
            self.timer.stop()
            self.btn_start.setText('Start')
        else:
            params = self.parseInputs()
            if params:
                invalid = self.control.validateParams(params)

                if not invalid:
                    self.control.setDataBuffer(params)
                    self.graph_pos.setYRange(0, params['d'], padding=0.1)
                    self.btn_start.setEnabled(True)

                    self.timer.start(50)
                    self.btn_start.setText('Stop')

                    # self.input_length.setReadOnly(True)
                    # self.input_thick.setReadOnly(True)
                    # self.input_def.setReadOnly(True)
                    # self.input_nCycles.setReadOnly(True)
                    # self.input_ptt1.setReadOnly(True)
                    # self.input_ptt2.setReadOnly(True)
                    # self.input_ptt3.setReadOnly(True)
                    # self.input_ptt4.setReadOnly(True)
                else: 
                    errorMessage = ''
                    for p in invalid:
                        errorMessage = errorMessage + paramMappings[p] + ' must be positive and less than ' + maxParamMappings[p] + '\n'
                    self.displayMessage(errorMessage, 'warning')
                    self.btn_start.setEnabled(False)

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

def initGUI(control, output):
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow(control, output)
    main.show()
    sys.exit(app.exec_())
