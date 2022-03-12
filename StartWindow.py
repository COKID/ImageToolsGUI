# -*- coding: UTF-8 -*-
import traceback
import sys
import os
from os import listdir,makedirs, mkdir
from os.path import join,basename,dirname,exists

from PIL import Image, ImageDraw
# from PyQt5 import company_namei,QtCore
# from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog,QLineEdit,QMessageBox, QWidget,QTableWidgetItem
from PyQt5.QtGui import QImage, QPixmap
from UI_MainWindow import Ui_ImageTools

class StartWindow(QMainWindow, Ui_ImageTools):
    def __init__(self):
        super(StartWindow,self).__init__()
        self.setupUi(self) #加载UI
        self.event_init() #加载事件绑定
        self.env_init()#环境初始化
        
        self.old_hook=sys.excepthook
        sys.excepthook=self.catch_exceptions
    
    def catch_exceptions(self, exType, exValue, exTraceback):       
        traceback_format = traceback.format_exception(exType, exValue, exTraceback)
        traceback_string = "".join(traceback_format)
        QMessageBox.critical(None, "An exception was raised", "{}".format(traceback_string))
        self.old_hook(exType, exValue, exTraceback)

    def env_init(self):
        self.last_directory=os.getcwd()#用于保存上次路径，从当前运行环境路径开始
        self.workdir=dirname(sys.argv[0])#工作目录设定为项目文件路径
        wd=join(self.workdir,"workdir")
        if not exists(wd):mkdir(wd)

    def event_init(self):
        #标签页切换事件
        self.pixelLocationButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.pixelLocation))#lambda定义匿名函数否则不能绑定带参数的函数
        self.imageSelectorButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.imageSelector))
        self.imageCropButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.imageCrop))
        self.drawBoxButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.drawBox))
        self.resampleButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.imageResample))
        
        #像素定位功能相关事件
        self.openImageButton.clicked.connect(self.showImage)

        #图片筛选功能相关事件
        self.selectFolder1.clicked.connect(lambda:self.open_folder_dialog(self.selectPath1))
        self.selectFolder2.clicked.connect(lambda:self.open_folder_dialog(self.selectPath2))
        self.selectFolder3.clicked.connect(lambda:self.open_folder_dialog(self.selectPath3))
        self.selectFolder4.clicked.connect(lambda:self.open_folder_dialog(self.selectPath4))
        self.selectFolder5.clicked.connect(lambda:self.open_folder_dialog(self.selectPath5))
        self.selectFolder6.clicked.connect(lambda:self.open_folder_dialog(self.selectPath6))
        self.selectImageButton.clicked.connect(self.start_selector)
        self.nextButton.clicked.connect(self.next_image)
        self.preButton.clicked.connect(self.pre_image)

        #图片裁剪功能相关事件
        self.singleCropButton.clicked.connect(lambda:self.open_file_dialog(self.singleCropPath))
        self.batchCropButton.clicked.connect(lambda:self.open_folder_dialog(self.batchCropPath))
        self.singlePreview.clicked.connect(self.crop_preview)
        self.singleSave.clicked.connect(self.crop_single_save)
        self.batchSave.clicked.connect(self.crop_batch_save)

        #图片绘制相关事件
        self.singleDrawButton.clicked.connect(lambda:self.open_file_dialog(self.singleDrawPath))
        self.batchDrawButton.clicked.connect(lambda:self.open_folder_dialog(self.batchDrawPath))
        self.singleDrawPreview.clicked.connect(self.draw_preview)
        self.singleDrawSave.clicked.connect(self.draw_single_save)
        self.batchDrawSave.clicked.connect(self.draw_batch_save)

        #重采样相关事件
        self.resampleFolderButton.clicked.connect(lambda:self.open_folder_dialog(self.resamplePath))
        self.resampleRun.clicked.connect(self.resample)

    
    
    
    def showImage(self):
        fileName,fileType = QFileDialog.getOpenFileName(self, "选取文件",self.last_directory,"All Files(*);;Image Files(*.png);;(*.jpg);;(*.jpeg);;(*.bmp)")
        if(fileName==""):return
        self.last_directory=fileName
        self.pixelImage.setPixmap(QPixmap(str(fileName)))

    def open_file_dialog(self,textBox:QLineEdit):
        fileName,fileType = QFileDialog.getOpenFileName(self, "选取文件",self.last_directory,"All Files(*);;Image Files(*.png);;(*.jpg);;(*.jpeg);;(*.bmp)")
        self.last_directory=fileName
        textBox.setText(fileName)

    def open_folder_dialog(self,textBox:QLineEdit):
        directory=QFileDialog.getExistingDirectory(self,"选取文件夹",self.last_directory)
        self.last_directory=directory
        textBox.setText(directory)
    
    def start_selector(self):
        self.active_window={
            '1':self.image1,
            '2':self.image2,
            '3':self.image3,
            '4':self.image4,
            '5':self.image5,
            '6':self.image6
        }
        self.active_path={
            '1':None,
            '2':None,
            '3':None,
            '4':None,
            '5':None,
            '6':None
        }
        if(self.selectPath1.text()!=''):self.active_path['1']=decode_full_path(self.selectPath1.text())
        if(self.selectPath2.text()!=''):self.active_path['2']=decode_full_path(self.selectPath2.text())
        if(self.selectPath3.text()!=''):self.active_path['3']=decode_full_path(self.selectPath3.text())
        if(self.selectPath4.text()!=''):self.active_path['4']=decode_full_path(self.selectPath4.text())
        if(self.selectPath5.text()!=''):self.active_path['5']=decode_full_path(self.selectPath5.text())
        if(self.selectPath6.text()!=''):self.active_path['6']=decode_full_path(self.selectPath6.text())
        self.stackedWidget.setCurrentWidget(self.imageSelector2)
        self.current_index=1
        self.step_image(self.current_index)

    def next_image(self):
        self.current_index=self.current_index+1
        self.step_image(self.current_index)

    def pre_image(self):
        self.current_index=self.current_index-1
        self.step_image(self.current_index)
        
    def step_image(self,i):#i代表第几张从1开始
        for key in self.active_window:
            if(self.active_path[key]!=None):
                window=self.active_window[key]
                paths=self.active_path[key]
                length=len(paths)

                if(i<=0):i+=length
                
                path=paths[(i-1)%length]

                window.setPixmap(QPixmap(path))
                self.status_message(decode_file_name(path))
                self.current_index=i%(length+1)

    def crop_preview(self):
        
        img=Image.open(self.singleCropPath.text())

        p=decode_pos(self.singleCropPos.text())

        result=img.crop(p)
        result.show()

    def crop_single_save(self):
        p=decode_pos(self.singleCropPos.text())
        img_name=decode_file_name(self.singleCropPath.text())
        full_filename=join(self.workdir,"workdir","crop_"+img_name)
        
        img=Image.open(self.singleCropPath.text())
        result=img.crop(p)

        result.save(full_filename)
        self.status_message("处理完成")

    def crop_batch_save(self):
        self.status_message("处理中")
        full_path_filenames=decode_full_path(self.batchCropPath.text())
        t=decode_pos(self.batchCropPos.text())

        for path in full_path_filenames:
            img=Image.open(path)

            result=img.crop(t)

            img_name=decode_file_name(path)
            full_filename=join(self.workdir,"workdir","crop_"+img_name)
            result.save(full_filename)

        self.status_message("处理完成")

    def draw_preview(self):
        p=decode_pos(self.drawPos.text())
        c=self.drawColor.currentText()
        w=int(self.drawWidth.currentText())

        img=Image.open(self.singleDrawPath.text())
        draw=ImageDraw.ImageDraw(img)
        draw.rectangle(p,fill=None,outline=c,width=w)

        img.show()
    
    def draw_single_save(self):
        p=decode_pos(self.drawPos.text())
        c=self.drawColor.currentText()
        w=int(self.drawWidth.currentText())

        img_name=decode_file_name(self.singleDrawPath.text())
        isChecked=self.checkBox.isChecked()

        img=Image.open(self.singleDrawPath.text())
        if(isChecked):
            full_filename=join(self.workdir,"workdir","drawCrop_"+img_name)
            crop=img.crop(p)
            crop.save(full_filename)

        draw=ImageDraw.ImageDraw(img)
        draw.rectangle(p,fill=None,outline=c,width=w)

        full_filename=join(self.workdir,"workdir","draw_"+img_name)
        img.save(full_filename)
        self.status_message("处理完成")

    def draw_batch_save(self):
        self.status_message("处理中")

        full_path_filenames=decode_full_path(self.batchDrawPath.text())

        p=decode_pos(self.drawPos.text())
        c=self.drawColor.currentText()
        w=int(self.drawWidth.currentText())
        isChecked=self.checkBox.isChecked()


        for path in full_path_filenames:
            img_name=decode_file_name(path)#解析文件名
            img=Image.open(path)#打开文件

            if(isChecked):#先保存剪裁
                full_filename=join(self.workdir,"workdir","drawCrop_"+img_name)
                crop=img.crop(p)
                crop.save(full_filename)

            draw=ImageDraw.ImageDraw(img)
            draw.rectangle(p,fill=None,outline=c,width=w)
            full_filename=join(self.workdir,"workdir","draw_"+img_name)
            img.save(full_filename)

        self.status_message("处理完成")

    def resample(self):
        full_path_filenames=decode_full_path(self.resamplePath.text())

        sf_list=self.scaleFactor.text().split(',')
        sf_int=tuple(int(i)for i in sf_list)

        mode=self.resampleMode.currentText()

        alg=self.resampleAlgorithm.currentText().split('-')[1]
        alg_dic = {
            "BICUBIC" : Image.BICUBIC,
            "BILINEAR" : Image.BILINEAR,
            "NEAREST" : Image.NEAREST,
            "LANCZOS" : Image.LANCZOS
        }

        for sf in sf_int:
            for path,i in zip(full_path_filenames,range(len(full_path_filenames))):
               
                img_name=decode_file_name(path)
                message="{}中,倍率:{},第{}张图,{}".format(mode,str(sf),str(i+1),img_name)
                self.status_message(message)

                img=Image.open(path)

                if(mode=="上采样"):
                    resample_img=img.resize((img.size[0]*sf,img.size[1]*sf),alg_dic[alg])
                    prefix="up_"+str(sf)+"_"
                elif(mode=="下采样"):
                    resample_img=img.resize((img.size[0]//sf,img.size[1]//sf),alg_dic[alg])
                    prefix="down_"+str(sf)+"_"

                full_filename=join(self.workdir,"workdir",prefix+img_name)
                resample_img.save(full_filename)

        self.status_message("处理完成")
    def status_message(self,message):
        self.statusBar.showMessage(message,9999)

def decode_full_path(input_dir):#给定文件夹路径下的所有文件列表
    filenames = [join(input_dir, x) for x in listdir(input_dir)]
    return filenames
def decode_file_name(input_dir):#给定文件路径解析文件名
    return basename(input_dir)
def decode_pos(pos):
    pos_list=pos.split(',')
    t_pos=tuple(int(i)for i in pos_list)
    return t_pos


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win=StartWindow()
    main_win.show()
    sys.exit(app.exec_())