from PyQt5 import QtWidgets, uic, QtGui
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
from os import path
import pickle
from .constants import *

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
        uic.loadUi('./GUI/mainwindow.ui', self)

        #ui title and positioning
        self.setWindowTitle("Mesomat Strain Apparatus")
        self.setGeometry(0,0,800,479)

        #initialize modules
        self.control = control
        self.output = output

        #Initialize button behaviour
        self.btn_clear.clicked.connect(self.clearInputs)
        self.btn_start.clicked.connect(self.toggleStart)
        self.input_sLabel.setFocus()

        #Initialize resistance select dropdown
        self.select_resist.currentIndexChanged.connect(self.resGraphChanged)
        self.selected_res = 0

        #look for any stored inputs
        if path.exists('inputs.pckl'):
            f = open('inputs.pckl', 'rb')
            params = pickle.load(f)
            self.input_sLabel.setText(params['sample_label'])
            self.input_tLabel.setText(params['test_label'])
            self.input_length.setText(str(params['l']))
            self.input_thick.setText(str(params['t']))
            self.input_def.setText(str(params['d']))
            self.input_nCycles.setText(str(params['n']))
            self.input_ptt1.setText(str(params['p1']))
            self.input_ptt2.setText(str(params['p2']))
            self.input_ptt3.setText(str(params['p3']))
            self.input_ptt4.setText(str(params['p4']))

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

        self.graph_resist.setLabel('bottom', 'Time', 's')
        self.graph_resist.setLabel('left', 'Resistance', '\u03A9')

        self.graph_pos.setMouseEnabled(x=False, y=False)
        self.graph_resist.setMouseEnabled(x=False, y=False)

        self.curvePos = self.graph_pos.plot()
        self.curveResist = self.graph_resist.plot()

        #initialize dialog box
        self.messageBox = QtWidgets.QMessageBox()
        self.confirmDialog = QtWidgets.QMessageBox()

        #Initialize timer
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)

        #initialize event loop
        self.eventTimer = pg.QtCore.QTimer()
        self.eventTimer.timeout.connect(self.checkEvents)
        self.eventTimer.start(50)
    
    # when enter key is pressed
    def keyPressEvent(self, event):
        if event.key() == pg.QtCore.Qt.Key_Return:
            if not self.btn_start.isChecked():
                self.btn_start.toggle()
                self.toggleStart()
        else:
            super().keyPressEvent(event) 
    
    # check if there are any messages from the system
    def checkEvents(self):
        if not self.messageBox.isVisible():
            message = self.output.readMessages()
            error = self.output.readErrors()
            if message:
                self.displayMessage(message, 'info')
            if error:
                self.displayMessage(error, 'error')

        if self.output.isTestComplete():
            self.reset()
            self.output.setTestComplete(False)
        
    def update(self):
        error = self.output.readErrors()
        if error:
            self.timer.stop()
            self.displayMessage(error, 'error')
        else:
            # update graph
            [ptr, x, dataPos, dataResist] = self.output.getData()
            if (ptr < DATA_BUFF_SIZE):
                self.curvePos.setData(x[:ptr], dataPos[:ptr])
                self.curveResist.setData(x[:ptr], dataResist[self.selected_res][:ptr])
            else:
                self.curvePos.setData(x, dataPos)
                self.curveResist.setData(x, dataResist[self.selected_res])
        
    def clearInputs(self):
        self.input_sLabel.clear()
        self.input_tLabel.clear()
        self.input_length.clear()
        self.input_thick.clear()
        self.input_def.clear()
        self.input_nCycles.clear()
        self.input_ptt1.clear()
        self.input_ptt2.clear()
        self.input_ptt3.clear()
        self.input_ptt4.clear()

    # reset buttons, inputs, and graphs
    def reset(self):
        self.timer.stop()
        self.btn_start.setText('Start')
        self.input_sLabel.setReadOnly(False)
        self.input_tLabel.setReadOnly(False)
        self.input_length.setReadOnly(False)
        self.input_thick.setReadOnly(False)
        self.input_def.setReadOnly(False)
        self.input_nCycles.setReadOnly(False)
        self.input_ptt1.setReadOnly(False)
        self.input_ptt2.setReadOnly(False)
        self.input_ptt3.setReadOnly(False)
        self.input_ptt4.setReadOnly(False)
        self.btn_clear.setEnabled(True)
        self.btn_start.setChecked(False)

    # convert inputs to numbers and check if any inputs are empty
    def parseInputs(self):
        sample_label = self.input_sLabel.text()
        test_label = self.input_tLabel.text()
        l = self.input_length.text()
        t = self.input_thick.text()
        d = self.input_def.text()
        n = self.input_nCycles.text()
        p1 = self.input_ptt1.text()
        p2 = self.input_ptt2.text()
        p3 = self.input_ptt3.text()
        p4 = self.input_ptt4.text()

        if (not sample_label or not test_label or not l or not t or not d or not n or not
            p1 or not p2 or not p3 or not p4):
            self.displayMessage('Cannot leave field empty', 'warning')
            return {}
        else:
            return {
                'sample_label': sample_label,
                'test_label': test_label,
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
        # if operation has started
        if not self.btn_start.isChecked():
            if self.confirmQuestion('Are you sure you want to stop operation?'):
                self.control.setStopPressed(True)
                self.timer.stop()
                self.btn_start.setText('Start')

                self.input_sLabel.setReadOnly(False)
                self.input_tLabel.setReadOnly(False)
                self.input_length.setReadOnly(False)
                self.input_thick.setReadOnly(False)
                self.input_def.setReadOnly(False)
                self.input_nCycles.setReadOnly(False)
                self.input_ptt1.setReadOnly(False)
                self.input_ptt2.setReadOnly(False)
                self.input_ptt3.setReadOnly(False)
                self.input_ptt4.setReadOnly(False)
                self.btn_clear.setEnabled(True)
            else:
                self.btn_start.toggle()

        #if operation has not started
        else:
            params = self.parseInputs()
            if params:
                invalid = self.control.validateParams(params)

                if not invalid:
                    #store inputs
                    f = open('inputs.pckl', 'wb')
                    pickle.dump(params, f)
                    f.close()

                    self.curvePos.setData([])
                    self.curveResist.setData([])
                    self.control.setDataBuffer(params)

                    self.timer.start(50)
                    self.btn_start.setText('Stop')

                    self.input_sLabel.setReadOnly(True)
                    self.input_tLabel.setReadOnly(True)
                    self.input_length.setReadOnly(True)
                    self.input_thick.setReadOnly(True)
                    self.input_def.setReadOnly(True)
                    self.input_nCycles.setReadOnly(True)
                    self.input_ptt1.setReadOnly(True)
                    self.input_ptt2.setReadOnly(True)
                    self.input_ptt3.setReadOnly(True)
                    self.input_ptt4.setReadOnly(True)
                    self.btn_clear.setEnabled(False)
                else:
                    errorMessage = ''
                    for p in invalid:
                        errorMessage = errorMessage + paramMappings[p] + ' must be positive and less than ' + maxParamMappings[p] + '\n'
                    self.displayMessage(errorMessage, 'warning')
                    self.btn_start.toggle()
            else:
                self.btn_start.toggle()
                    
    # message dialog
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

    # confirm dialog
    def confirmQuestion(self, message):
        res = self.confirmDialog.question(self, '', message, self.confirmDialog.Yes | self.confirmDialog.No)
        return (res == self.confirmDialog.Yes)

    # change the displayed resistance
    def resGraphChanged(self, i):
        self.selected_res = i

def initGUI(control, output):
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow(control, output)
    main.show()
    sys.exit(app.exec_())
