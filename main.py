import base64
import os

import tkinter as tk

from tkinter import filedialog
from tkinter import ttk
import threading
from tkinter.messagebox import showinfo

import requests
from bs4 import BeautifulSoup

#全部方法调用区
import method
import frozen_dir
import icon


def ALL_Window():
    # 定义一个窗口程序
    My_Window = tk.Tk()
    # 窗口的标题显示名
    My_Window.title('风灵月影下载器')
    # 窗口的大小
    My_Window.geometry('400x500')
    # 窗口颜色
    My_Window.config(background='#333333')
    # 得到屏幕宽度
    sw = My_Window.winfo_screenwidth()
    # 得到屏幕高度
    sh = My_Window.winfo_screenheight()

    ww = 400
    wh = 500
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    My_Window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    #窗口不可调节大小
    My_Window.resizable(False, False)
    #添加程序图标
    icon1 = icon.Icon
    # 获取改ig变量的内容
    icc = icon1().ig
    with open('tmp.ico', 'wb') as tmp:
        tmp.write(base64.b64decode(icc))
    # 创建一个临时ico图标给程序使用
    My_Window.iconbitmap('tmp.ico')
    # 最后删除该文件
    os.remove('tmp.ico')

    # 搜索栏
    Srarch_txt = tk.Entry()
    Srarch_txt.place(x=40, y=50, width=230, height=40, anchor='nw')

    #搜索用线程池
    def Srarch_lock():
        # 执行一些耗时操作
        # 删除全部列表元素
        Gametxt.delete(0, 'end')
        st = Srarch_txt.get()
        # 将搜索栏内容扔到解析去
        gamename = method.Srarch_GameName(st)
        allGameName = gamename

        for game in allGameName:
            # 在末位依次添加列表元素
            Gametxt.insert('end', game)
    #执行搜索线程池
    def SrarchTxt():
        # 创建一个新线程
        t = threading.Thread(target=Srarch_lock)
        # 启动线程
        t.start()

    # 搜索按钮
    Srarch_Button = tk.Button(text='点击搜索', command=SrarchTxt)
    Srarch_Button.place(x=290, y=50, width=90, height=40, anchor='nw')

    # 游戏列表
    Gametxt = tk.Listbox()
    Gametxt.place(x=40, y=120, width=230, height=300, anchor='nw')

    # 下载用线程池
    def download_lock():
        # 执行一些耗时操作
        # 锁定按钮
        download_Button.state(['disabled'])
        st = Srarch_txt.get()
        # 将搜索栏内容扔到解析去
        gameURl = method.Srarch_GameURl(st)
        allGameURl = gameURl
        #获取选中游戏的下标
        txtgame = Gametxt.index('active')
        #获取选中游戏名称
        game_Name = Gametxt.get(txtgame)
        # 请求头
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
        headers['Referer'] = 'https://www.baidu.com/'
        #对应选中游戏的下载链接
        gameMenu = allGameURl[int(txtgame)]
        gameMenu_req = requests.request(url=gameMenu, headers=headers, method='GET')
        soup = BeautifulSoup(gameMenu_req.text, 'html.parser')
        #获取对应修改器第一位链接
        find_gameMenuUrl = soup.find_all('a', class_ = "attachment-link" ,target="_self")[0]
        gameMenu_URL = find_gameMenuUrl['href']
        print("对应修改器第一位链接:",gameMenu_URL)
        #创建本地下载文件夹
        download_folder()
        #下载程序
        ################
        #去除文件夹不能存在的特殊字符
        name = game_Name
        sets = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in name:
            if char in sets:
                name = name.replace(char, '')
        #下载地址
        path = download_path_Read()+'/'
        #调用下载
        method.download_file(gameMenu_URL,path)
        #自动解压
        #压缩包名字
        res = requests.get(gameMenu_URL, headers=headers)
        # 获取文件名称
        package_Name = res.url.split("/")[-1]
        # 下载压缩包地址
        package_path = path+package_Name
        print("下载压缩包地址:",package_path)
        print("特殊字符改：",name)
        #执行解压缩
        method.zip_decompress(package_path,path,name)
        #删除原压缩包
        if os.path.exists(package_path):  # 检查文件是否存在
            os.remove(package_path)
        #下载完成弹窗
        showinfo(title='下载进度', message ='下载已完成，自动解压并删除压缩包')
        # 解锁按钮
        download_Button.state(['!disabled'])

    # 执行下载线程池
    def download_Game():
        # 创建一个新线程
        t = threading.Thread(target=download_lock)
        # 启动线程
        t.start()


    # 下载按钮
    download_Button = ttk.Button(text='点击下载',command=download_Game)
    download_Button.place(x=290, y=120, width=90, height=40, anchor='nw')


    #读取保存地址信息
    def download_path_Read():
        DW_path_Read = frozen_dir.app_path() + '/Set/Download_path.txt'
        with open(DW_path_Read,"r") as file_txt_Read:
            txt_Read = file_txt_Read.read()
            #判断是否有地址
            if txt_Read == '':
                with open(DW_path_Read, "w") as file_txt:
                    # 默认下载地址
                    download_txt = frozen_dir.app_path() + '/Download/'
                    file_txt.write(download_txt)
                    file_txt.close()
                    return txt_Read
            else:
                return txt_Read

    # 下载文件地址显示框
    download_path = tk.Label(justify="left", anchor="w", text=f'下载文件地址：\n{download_path_Read()}',wraplength=340)
    download_path.pack()
    download_path.place(x=40, y=430, width=340, height=50)

    # 储存下载位置信息
    def download_path_Txt_lock():
        # 下载路径保存位置(反正都建立了Set文件夹了，总得多点啥玩意)
        DW_path = frozen_dir.app_path() + '/Set/Download_path.txt'
        path = open(DW_path, "w")
        path.close()
        # 开始写入路径信息
        # 默认下载地址
        download_txt = frozen_dir.app_path() + '/Download/'
        # 选择保存文件夹地址
        # 地址格式： D:/Python项目/My_Game/Download
        file = filedialog.askdirectory()
        if file == '':
            with open(DW_path, "w") as file_txt:
                file_txt.write(download_txt)
                file_txt.close()
            download_path.config(text=f'下载文件地址：\n{download_path_Read()}',wraplength=340)
        else:
            with open(DW_path,"w") as path_txt:
                path_txt.write(file)
                path_txt.close()
            download_path.config(text=f'下载文件地址：\n{download_path_Read()}',wraplength=340)

    # 执行创建下载地址线程池
    def download_path_txt():
        # 创建一个新线程
        t = threading.Thread(target=download_path_Txt_lock)
        # 启动线程
        t.start()

    #更改下载地址
    download_path_Button = tk.Button(text='更改下载位置',command=download_path_txt)
    download_path_Button.place(x=290, y=180, width=90, height=40, anchor='nw')

    #窗口主程序
    My_Window.mainloop()

# 本地根目录创建文件夹
def download_folder():
    save_path = frozen_dir.app_path() + r"/Download"
    if os.path.exists(save_path):
        print(f'文件{save_path}存在')
    else:
        print(f'文件{save_path}不存在')
        os.mkdir(save_path)



if __name__ == "__main__":
    ALL_Window()