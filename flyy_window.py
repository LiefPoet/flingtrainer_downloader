import threading
from tkinter import filedialog
from tkinter.messagebox import showinfo

import customtkinter
from PIL import Image, ImageTk
import os
import requests
from bs4 import BeautifulSoup

import frozen_dir
import method


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("风灵月影下载器")
        ww = 550
        wh = 480
        # self.geometry("400x500")
        self.width = int((self.winfo_screenwidth() - ww) / 2)
        self.height = int((self.winfo_screenheight() - wh) / 2)
        self.geometry(f"{ww}x{wh}+{self.width}+{self.height}")
        self.minsize(550, 480)
        self.maxsize(550, 480)
        try:
            self.iconpath = ImageTk.PhotoImage(file=os.path.join("assets", "f.ico"))
            self.wm_iconbitmap()
            self.iconphoto(False, self.iconpath)
        except:
            pass

        # 搜索栏
        self.Srarch_Entry = customtkinter.CTkEntry(self, width=390, height=40)
        self.Srarch_Entry.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        self.Srarch_Button = customtkinter.CTkButton(self, width=120, height=40, text='点击搜索',
                                                     command=self.SrarchTxt)
        self.Srarch_Button.grid(row=0, column=1, padx=10, pady=10, sticky="nw")

        # 游戏列表
        self.GameList_frame = customtkinter.CTkScrollableFrame(self, width=510, height=300)
        self.GameList_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nw")
        # 进度条
        self.Srarch_ProgressBar = customtkinter.CTkProgressBar(self, width=20, height=10)
        self.Srarch_ProgressBar.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        self.Srarch_ProgressBar.set(0)
        # 保存位置显示
        self.download_path_Text = customtkinter.CTkLabel(self, width=390, height=20, font=('Segoe UI', 15),
                                                         wraplength=390, justify='left')
        self.download_path_Text.grid(row=3, column=0, padx=10, pady=10, sticky="nw")

        self.download_path_Button = customtkinter.CTkButton(self, text="更改保存位置", width=120, height=40,
                                                            command=self.download_path_txt)
        self.download_path_Button.grid(row=3, column=1, padx=10, pady=10, sticky="nw")
        # 记录按钮
        self.item_Button = {}
        # 创建下载文件夹
        self.download_folder()
        self.download_path_Read()
        self.download_path_Text.configure(text=f'保存地址：{self.download_path_Read()}')

    # 搜索用线程池
    def Srarch_lock(self):
        # 锁定按钮
        self.Srarch_Button.configure(state="disabled")
        # 清空字典
        self.item_Button = {}
        # 设置进度条
        self.Srarch_ProgressBar.set(0)
        # 执行一些耗时操作
        st = self.Srarch_Entry.get()
        # 将搜索栏内容扔到解析去
        game_Name_Img, game_Url, gameNameList = method.Srarch_GameName(st)
        allGameName = game_Name_Img
        allGameUrl = game_Url

        # 检查是否有对应名称游戏
        if allGameName != None:
            num = 0
            # 进度条计数器
            ProgressBar_num = float(1 / len(allGameName))
            ProgressBar_num_2 = float(1 / len(allGameName))
            for game in allGameName:
                game_Img_Url = allGameName.setdefault(game)
                # print(len(allGameName))
                # 请求头
                headers = {
                    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                }
                headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
                headers['Referer'] = 'https://www.baidu.com/'
                # 显示图片
                my_image = customtkinter.CTkImage(
                    light_image=Image.open(requests.get(game_Img_Url, headers=headers, stream=True).raw),
                    size=(50, 50))
                # 创建对应按钮
                Gameurl = allGameUrl.setdefault(game)
                self.item_Button[game] = customtkinter.CTkButton(self.GameList_frame, image=my_image, text=game,
                                                                 width=500, anchor='nw',
                                                                 command=lambda n=game, gurl=Gameurl: threading.Thread(
                                                                     target=self.download_Trainer, args=(n, gurl),
                                                                     daemon=True).start())
                self.item_Button[game].grid(row=num, column=0, padx=10, pady=(10, 0), sticky="sw")
                print('游戏名：', game)
                print('游戏链接：', allGameUrl.setdefault(game))
                num += 1
                self.Srarch_ProgressBar.set(ProgressBar_num)
                ProgressBar_num += ProgressBar_num_2
            # 解锁按钮
            self.Srarch_Button.configure(state="normal")
        else:
            # 无对应游戏弹窗
            showinfo(title='搜索结果', message='未能查找到对应名称游戏 ！\n请检查名称或扩大范围搜索')
            # 解锁按钮
            self.Srarch_Button.configure(state="normal")

    # 执行搜索线程池
    def SrarchTxt(self):
        # 创建一个新线程
        t = threading.Thread(target=self.Srarch_lock)
        t.daemon = True
        # 启动线程
        t.start()

    # 下载用
    def download_Trainer(self, game_Name, game_url):
        print('标识：', game_Name)
        print('游戏链接:', game_url)
        # 请求头
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
        headers['Referer'] = 'https://www.baidu.com/'
        # 对应选中游戏的下载链接
        gameMenu = game_url
        gameMenu_req = requests.request(url=gameMenu, headers=headers, method='GET')
        soup = BeautifulSoup(gameMenu_req.text, 'html.parser')
        # 获取对应修改器第一位链接
        find_gameMenuUrl = soup.find_all('a', class_="attachment-link", target="_self")[0]
        gameMenu_URL = find_gameMenuUrl['href']
        # 创建本地下载文件夹
        self.download_folder()
        # 下载程序
        ################
        # 去除文件夹不能存在的特殊字符
        name = game_Name
        sets = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in name:
            if char in sets:
                name = name.replace(char, '')
        # 下载地址
        path = self.download_path_Read() + '/'
        # 调用下载
        method.download_file(gameMenu_URL, path, game_name=name)
        print("特殊字符改：", name)
        # 下载完成弹窗
        showinfo(title='下载进度', message='下载已完成，自动解压并删除压缩包')

    # 读取保存地址信息
    def download_path_Read(self):
        DW_path_Read = frozen_dir.app_path() + '/assets/Download_path.txt'
        with open(DW_path_Read, "r") as file_txt_Read:
            txt_Read = file_txt_Read.read()
            # 判断是否有地址
            if txt_Read == '':
                with open(DW_path_Read, "w") as file_txt:
                    # 默认下载地址
                    download_txt = frozen_dir.app_path() + '/Download/'
                    file_txt.write(download_txt)
                    file_txt.close()
                    return txt_Read
            else:
                return txt_Read

    # 本地根目录创建文件夹
    def download_folder(self):
        save_path = frozen_dir.app_path() + r"/Download"
        if os.path.exists(save_path):
            print(f'文件{save_path}存在')
        else:
            print(f'文件{save_path}不存在')
            os.mkdir(save_path)

    # 储存下载位置信息
    def download_path_Txt_lock(self):
        # 下载路径保存位置(反正都建立文件夹了，总得多点啥玩意)
        DW_path = frozen_dir.app_path() + '/assets/Download_path.txt'
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
            self.download_path_Text.configure(text=f'保存地址：{self.download_path_Read()}')
        else:
            with open(DW_path, "w") as path_txt:
                path_txt.write(file)
                path_txt.close()
            self.download_path_Text.configure(text=f'保存地址：{self.download_path_Read()}')

    # 执行创建下载地址线程池
    def download_path_txt(self):
        # 创建一个新线程
        t = threading.Thread(target=self.download_path_Txt_lock)
        t.daemon = True
        # 启动线程
        t.start()


if __name__ == "__main__":
    app = App()
    app.mainloop()
