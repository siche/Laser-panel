
# QLineEdit Example

from PyQt5.QtWidgets import QApplication,QLineEdit,QWidget,QFormLayout, QPushButton,QGridLayout,QLabel,QCheckBox,QDoubleSpinBox,QLCDNumber
from PyQt5 import QtCore,QtWidgets,QtGui
import sys
import matplotlib
matplotlib.use('Qt5Agg')
# 使用 matplotlib中的FigureCanvas (在使用 Qt5 Backends中 FigureCanvas继承自QtWidgets.QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np 
import time 
from wlm_web import wlm_web
from toptica_laser import toptica_laser as laser
import threading 

# import pmt_window
data_len = 100

# data = [0]*100
# xdata = list(range(100))

# 利用QT自己的多线程，方便线程的结束

class update_data(QtCore.QThread):
    def __int__(self):
        super(update_data, self).__init__()

    def run(self):
        wlm = wlm_web()
        global data 
        data = [[0]*data_len]*8
        count = 0
        while True:
            count+=1
            wlm_data = wlm.get_data()
            for i in range(8):
                data[i] = data[i][1:] + [round(wlm_data[i],6)]
            # print('wavelength is %.6f' % wlm_data[3])
            # print(T_value, P_value)
            time.sleep(0.1)

class window(QWidget):
    def __init__(self,ip,default_fre,channel,parent=None):
        super(window, self).__init__(parent)
        self.setWindowTitle('Laser Control Panel')
        self.laser = laser(ip)
        self.default_fre = default_fre
        self.channel = channel-1
        self.initUi()
        
    def initUi(self):
        # layout
        l1 = QDoubleSpinBox()
        l1.setRange(300.,940.)
        l1.setDecimals(6)
        l1.setValue(self.default_fre)
        l1.setSingleStep(0.000001)
        
        # l1.setValidator(QtGui.QDoubleValidator())

        label1 = QLabel('WaveLength')
        btn1 = QCheckBox()
        btn1.setChecked(QtCore.Qt.Unchecked)
        # btn1.clicked.connect(self.plot_figure)
        btn1.clicked.connect(self.laser_lock)
    
        label2 = QLabel('Emission')
        btn2 = QCheckBox()
        btn2.setChecked(False)
        btn2.clicked.connect(self.laser_on)

        label21 = QLabel('Current')
        btn21 = QDoubleSpinBox()
        btn21.setRange(0,self.laser.max_current)
        btn21.setDecimals(5)
        btn21.setValue(self.laser.get_current())
        btn21.setSingleStep(0.01)
        btn21.editingFinished.connect(lambda:self.laser.set_current(btn21.value()))

        label22 = QLabel('Voltage')
        btn22 = QDoubleSpinBox()
        btn22.setRange(0,200)
        btn22.setDecimals(5)
        btn22.setValue(self.laser.get_voltage())
        btn22.setSingleStep(0.01)
        btn22.editingFinished.connect(lambda:self.laser.set_voltage(btn22.value()))
        
        self.figure = plt.figure()
        self.plot, = plt.plot(list(range(data_len)),list(range(data_len)))
        self.ax = plt.gca()
        self.txt = self.ax.text(0.8,0.9,'test',verticalalignment = 'center', transform=self.ax.transAxes)
        self.canvas = FigureCanvas(self.figure)

        # btn1.clicked.connect(lambda:self.key_print(l1.text()))
       
        # btn1.clicked.connect(self.key_print)
        layout = QGridLayout()
        layout.addWidget(label1,1,0)
        layout.addWidget(l1,1,1)
        layout.addWidget(btn1,1,2)
        layout.addWidget(label2,1,3)
        layout.addWidget(btn2,1,4)    
        layout.addWidget(label21,2,0)
        layout.addWidget(btn21,2,1) 
        layout.addWidget(label22,2,2)
        layout.addWidget(btn22,2,3)

        layout.addWidget(self.canvas,3,0,2,4)
        
        self.spin1 = l1
        self.btn1 = btn1
        self.btn21 = btn21
        self.btn22 = btn22 

        self.setLayout(layout)
        self.setGeometry(300, 300, 600, 500)
        self.setWindowTitle('Laser Control Panel')
        self.Mytimer2(100,self.plot_figure)
        self.Mytimer2(2001,self.laser_lock)
        self.Mytimer2(5000,self.refresh)    
        # self.show()
        # self.laser = laser(ip)
        
    def Mytimer(self):
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.plot_figure)
        timer.start(100)

    def Mytimer2(self,interval,func):
        timer=QtCore.QTimer(self)
        timer.timeout.connect(func)
        timer.start(interval)
    
    def refresh(self):
        self.btn21.setValue(self.laser.get_current())
        self.btn22.setValue(self.laser.get_voltage())

    def plot_figure(self):
        #if self.btn1.isChecked(): 
            self.txt.remove()
            self.plot.set_ydata(data[self.channel])
            self.ax.relim()
            self.ax.autoscale_view(True,True,True)

            show_data = '%.6fnm' % data[self.channel][-1]
            self.txt=self.ax.text(0.7,0.9,show_data ,verticalalignment = 'center', transform=self.ax.transAxes)
            # print('min is %.6f max is %.6f' % (min(data), max(data)))
            # self.ax.relim()
            # self.ax.autoscale_view(True, True, True)
            self.canvas.draw()
            # print(self.btn22.cursor().pos())

    def laser_lock(self):
        if self.btn1.isChecked():
            # print('locking')
            self.laser.lock(data[self.channel][-1], self.spin1.value())

    def laser_on(self):
        if (not self.laser.is_on() and self.btn1.isChecked()):
            self.laser.on()

    def laser_lock_bak(self,i):
        code = 'btn'+str(i)+'.isChecked()'
        status = eval(code)
        if status:
            code ='self.laser'+str(i)+'.lock(data[-1],self.spin'+str(i)+'.value())'
            self.laser.lock(data[self.channel][-1],self.spin1.value())
            # time.sleep(2)

    def laser_on_bak(self,i):
        code = 'self.laser'+str(i)+'.is_on()'
        status = eval(code)

    def key_print(self):
        if self.btn1.isChecked():
            print(self.spin1.value())

class main_window(QWidget):
    def __init__(self,parent = None):
        super(main_window, self).__init__(parent)
        self.initUi()
    
    def initUi(self):
        ip1 = '192.168.1.9'
        fre1 = 935.188960
        ch1 = 4 

        ip2 = '192.168.1.61'
        fre2 = 369.526096
        ch2 = 2

        ip3 = '192.168.1.8'
        fre3 = 398.910960
        ch3 = 3
        
        # pmt_com = 'com5'
        self.win1 = window(ip1,fre1,ch1)
        self.win2 = window(ip2,fre2,ch2)
        self.win3 = window(ip3,fre3,ch3)
        # self.win4 = pmt_window.pmt_window(pmt_com)

        layout = QGridLayout()
        layout.addWidget(self.win1,1,0)
        layout.addWidget(self.win2,1,1)
        layout.addWidget(self.win3,2,0)
        # layout.addWidget(self.win4,2,1)

        self.setLayout(layout)
        self.setWindowTitle('Laser Control')
        self.setGeometry(200,200,1200,1000)
        self.show()

if __name__ == '__main__':
    # import threading
    # t = threading.Thread(target=get_data)
    # t.start()
    app = QApplication(sys.argv)
    ex = main_window()
    update_data = update_data()
    update_data.start()
    
    sys.exit(app.exec_())
