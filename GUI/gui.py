from PyQt5 import QtWidgets, uic, QtGui
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
import numpy as np

from control import ControlModule

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

        self.initializeData()

        self.ptr = 1
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)

    def initializeData(self):
        self.x = np.empty(200)
        for i in range(200):
            self.x[i] = i/20
        self.dataDef = np.empty(200)
        self.dataResist = np.empty(200)

        self.dataDef[0] = 0
        self.dataResist[0] = 0
    
    def update(self):
        #Random data generation for testing
        deformation = ControlModule.getDataBuffer()['defn']
        if self.ptr < 200:
            self.dataDef[self.ptr] = self.dataDef[self.ptr-1] + deformation*np.random.rand()/10
            self.dataResist[self.ptr] = self.dataResist[self.ptr-1] + np.random.rand()/10

            if self.dataDef[self.ptr] > deformation:
                self.dataDef[self.ptr] = 0
            if self.dataResist[self.ptr] > 1.0:
                self.dataResist[self.ptr] = 0
            
            self.ptr += 1

            self.curveDef.setData(self.x[:self.ptr], self.dataDef[:self.ptr])
            self.curveResist.setData(self.x[:self.ptr], self.dataResist[:self.ptr])
        else :
            self.dataDef[:-1] = self.dataDef[1:]
            self.dataDef[-1] = self.dataDef[-2] + deformation*np.random.rand()/10

            self.dataResist[:-1] = self.dataResist[1:]
            self.dataResist[-1] = self.dataResist[-2] + np.random.rand()/10

            if self.dataDef[-1] > deformation:
                self.dataDef[-1] = 0
            if self.dataResist[-1] > 1.0:
                self.dataResist[-1] = 0

            self.ptr += 1

            self.x[:-1] = self.x[1:]
            self.x[-1] = self.ptr/20

            self.curveDef.setData(self.x, self.dataDef)
            self.curveResist.setData(self.x, self.dataResist)
            # self.curveDef.setPos(self.ptr/20, 0)
            # self.curveResist.setPos(self.ptr/20, 0)

    def submit(self):
        l = float(self.input_length.text())
        t = float(self.input_thick.text())
        d = float(self.input_def.text())
        n = int(self.input_nCycles.text())
        p1 = float(self.input_ptt1.text())
        p2 = float(self.input_ptt2.text())
        p3 = float(self.input_ptt3.text())
        p4 = float(self.input_ptt4.text())

        invalid = ControlModule.validateParams(l,t,d,n,p1,p2,p3,p4)
        if not invalid:
            ControlModule.setDataBuffer(l,t,d,n,p1,p2,p3,p4)
            self.graph_def.setYRange(0, d, padding=0.1)
            self.btn_start.setEnabled(True)
        else: 
            print(invalid)
            self.btn_start.setEnabled(False)

    def toggleStart(self):
        if not self.btn_start.isChecked():
            self.timer.stop()
            self.btn_start.setText('Begin Cycles')
        else:
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

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()