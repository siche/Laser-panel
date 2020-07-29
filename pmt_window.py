from PyQt5.QtWidgets import QApplication,QLineEdit,QWidget,QFormLayout, QPushButton,QGridLayout,QLabel,QCheckBox,QSpinBox,QLCDNumber
from PyQt5 import QtCore,QtWidgets,QtGui
import sys
import matplotlib
matplotlib.use('Qt5Agg')
# 使用 matplotlib中的FigureCanvas (在使用 Qt5 Backends中 FigureCanvas继承自QtWidgets.QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np 
import time 

from time_count import time_count
from serial import Serial

data_len = 100
class get_data(QtCore.QThread):
    def __ini__(self):
        super(get_data, self).__init__()
        #self.com = 'com6'
    
    def run(self):
        ser = Serial('com11')
        ser.baudrate = 115200
        if ser.is_open:
            ser.close()

        ser.open()
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        global y_data 
        y_data = [0]*data_len
        global y_mean
        y_mean = [0]*data_len 
        global y_stdv
        y_stdv = [0]*data_len
        global y_up 
        y_up = [0]*data_len 
        global y_down
        y_down = [0]*data_len

        count = 0 
        i = 0
        while True:
            data = ser.read(2)
            num = int.from_bytes(data, byteorder = 'little')
            count+=num 
            # print('i: %d, num: %.4f' %(i,num))
            i+=1 
            if (i==15):
                temp_mean = np.mean(y_data)
                temp_stdv = np.std(y_data)

                y_now = count/16 
                y_data = y_data[1:] + [y_now]
                y_mean = y_mean[1:] + [temp_mean]
                y_stdv = y_stdv[1:] + [temp_stdv]
                y_up = y_up[1:] + [temp_mean+5*temp_stdv]
                y_down = y_down[1:] + [temp_mean - 5*temp_stdv]

                count = 0 
                i = 0

class pmt_window(QWidget):
        def __init__(self,parent=None):
            super(pmt_window, self).__init__(parent=None)
            self.initUi()
    
        def initUi(self):
            layout = QGridLayout()

            win1 = time_count()

            # btn21 = QLineEdit('[1,2,3,4,5,5,4,3,2,1]')
            # figure part 
            self.figure = plt.figure()
            self.fig1, = plt.plot(list(range(data_len)),list(range(data_len)),'r')
            self.fig2, = plt.plot(list(range(data_len)),list(range(data_len)),'g')
            self.fig3, = plt.plot(list(range(data_len)),list(range(data_len)),'g')

            self.ax = plt.gca()
            self.txt = self.ax.text(0.8,0.9,'test',verticalalignment = 'center', transform=self.ax.transAxes)
            self.canvas = FigureCanvas(self.figure)
            #layout.addWidget(label10,1,0)
            layout.addWidget(win1,0,0,1,4)
            layout.addWidget(self.canvas,3,0,2,4)
            self.setLayout(layout)
            self.Mytimer(300,self.plot_figure)

        def Mytimer(self,interval,func):
            timer=QtCore.QTimer(self)
            timer.timeout.connect(func)
            timer.start(interval)
        
        def plot_figure(self):
            self.txt.remove()
            self.fig1.set_ydata(y_data)
            self.fig2.set_ydata(y_up)
            self.fig3.set_ydata(y_down)

            self.ax.relim()
            self.ax.autoscale_view(True,True,True)

            show_data = "Count: %.2f\nMean: %.2f" %(y_data[-1], y_mean[-1])
            self.txt=self.ax.text(0.8,0.8,show_data ,verticalalignment = 'center', transform=self.ax.transAxes)
            # print('min is %.6f max is %.6f' % (min(data), max(data)))
            # self.ax.relim()
            # self.ax.autoscale_view(True, True, True)
            self.canvas.draw()

        def key_print(self):
            print(self.btn11.text())

if __name__ == '__main__':

    update_data = get_data()
    update_data.start()

    time.sleep(0.2)
    app = QApplication(sys.argv)
    ex = pmt_window()
    ex.show()
    sys.exit(app.exec_())

