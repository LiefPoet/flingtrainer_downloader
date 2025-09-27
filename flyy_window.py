import json
import os
import threading
import time
import tkinter
from tkinter import filedialog
from tkinter.messagebox import showinfo

import requests
from bs4 import BeautifulSoup
import shutil

import customtkinter
from PIL import Image, ImageTk

import frozen_dir
import method


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("风灵月影下载器")
        ww = 650
        wh = 480
        # self.geometry("400x500")
        self.width = int((self.winfo_screenwidth() - ww) / 2)
        self.height = int((self.winfo_screenheight() - wh) / 2)
        self.geometry(f"{ww}x{wh}+{self.width}+{self.height}")
        self.minsize(650, 480)
        self.maxsize(650, 480)

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.Game_Name = []
        self.OpenD = "off"
        # 文件地址
        self.file_Path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        # 图片地址
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "doge.png")), size=(26, 26))
        self.download_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "Download.png")),
                                                     size=(26, 26))
        self.TrainerGameList_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "TrainerGameList.png")),
                                                            size=(26, 26))
        self.refresh_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "refresh.png")), size=(26, 26))
        self.delete_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "delete.png")), size=(26, 26))

        try:
            self.iconpath = ImageTk.PhotoImage(file=os.path.join(image_path, "f.ico"))
            self.wm_iconbitmap()
            self.iconphoto(False, self.iconpath)
        except:
            pass

        # ----导航栏----
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)
        # 游戏列表
        self.suggest_Label = customtkinter.CTkLabel(self.navigation_frame, text="免费软件\n买的你就上当咯")
        self.suggest_Label.grid(row=1, column=0, padx=20, pady=20)
        # 标题
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  选择菜单",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        self.downloadTrainer_Button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                              border_spacing=10,
                                                              text="下载修改器",
                                                              fg_color="transparent", text_color=("gray10", "gray90"),
                                                              hover_color=("gray70", "gray30"),
                                                              image=self.download_image, anchor="w",
                                                              command=self.download_button_event)
        self.downloadTrainer_Button.grid(row=2, column=0, sticky="ew")
        # 修改器列表
        self.TrainerGameList_Button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                              border_spacing=10,
                                                              text="修改器列表",
                                                              fg_color="transparent", text_color=("gray10", "gray90"),
                                                              hover_color=("gray70", "gray30"),
                                                              image=self.TrainerGameList_image, anchor="w",
                                                              command=self.TrainerList_Button_frame)
        self.TrainerGameList_Button.grid(row=3, column=0, sticky="ew")

        # 修改器列表框架
        self.TrainerList_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.TrainerList_frame.grid_columnconfigure(0, minsize=140)
        self.TrainerList_frame.grid_columnconfigure(1, weight=1)

        # ------------- 风灵月影下载相关 ---------------
        # 风灵月影下载界面框架
        # self.Game_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.downloadGame_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.downloadGame_frame.grid_columnconfigure(0, weight=1)
        # 搜索栏
        self.Srarch_Entry = customtkinter.CTkEntry(self.downloadGame_frame, width=390, height=40)
        self.Srarch_Entry.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        self.Srarch_Button = customtkinter.CTkButton(self.downloadGame_frame, width=120, height=40, text='点击搜索',
                                                     command=self.SrarchTxt)
        self.Srarch_Button.grid(row=0, column=1, padx=10, pady=10, sticky="nw")

        # 游戏列表
        self.GameList_frame = customtkinter.CTkScrollableFrame(self.downloadGame_frame, width=510, height=300)
        self.GameList_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nw")
        # 进度条
        self.Srarch_ProgressBar = customtkinter.CTkProgressBar(self.downloadGame_frame, width=20, height=10)
        self.Srarch_ProgressBar.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        self.Srarch_ProgressBar.set(0)
        # 保存位置显示
        self.download_path_Text = customtkinter.CTkLabel(self.downloadGame_frame, width=430, height=20,
                                                         font=('Segoe UI', 15),
                                                         wraplength=300, justify='left')
        self.download_path_Text.grid(row=3, column=0, padx=10, pady=10, sticky="nw")

        self.download_path_Button = customtkinter.CTkButton(self.downloadGame_frame, text="更改保存位置", width=120,
                                                            height=40,
                                                            command=self.download_path_txt)
        self.download_path_Button.grid(row=3, column=1, padx=10, pady=(5, 4), sticky="nw")
        # 记录按钮
        self.item_Button = {}
        # 记录修改器列表
        self.List_Button = {}
        # 创建下载文件夹
        self.download_folder()
        self.download_path_Read()
        self.download_path_Text.configure(text=f'保存地址：{self.download_path_Read()}')
        # 创建游戏信息记录
        self.Trainer_Info_Json()
        # -------------- 修改器列表相关 --------------
        # ---- 刷新按钮 ----
        self.refresh_Button = customtkinter.CTkButton(self.TrainerList_frame, text="刷新修改器列表",
                                                      image=self.refresh_image, command=self.create_GameList)
        self.refresh_Button.grid(row=0, column=0, padx=5, pady=(10, 5), sticky="nsew")
        self.delete_Button = customtkinter.CTkButton(self.TrainerList_frame, text="删除修改器",
                                                     image=self.delete_image, command=self.delete_Trainer)
        self.delete_Button.grid(row=0, column=1, padx=5, pady=(10, 5), sticky="nsew")

    # 激活框架
    def select_frame_by_name(self, name):
        # 设置选择按钮颜色
        self.downloadTrainer_Button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")

        # 显示的Frame
        if name == "下载修改器":
            self.downloadGame_frame.grid(row=0, column=1, sticky="nsew")
            # flyyapp = flyy_window.App()
            # flyyapp.mainloop()
        else:
            self.downloadGame_frame.grid_forget()

        if name == '修改器列表':
            self.TrainerList_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.TrainerList_frame.grid_forget()

    def download_button_event(self):
        self.select_frame_by_name("下载修改器")

    def TrainerList_Button_frame(self):
        self.select_frame_by_name('修改器列表')
        # 切换时刷新一下列表
        self.create_GameList()

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # ---------- 游戏修改器列表生成 -----------
    def create_GameList(self):
        # 删除按钮
        for dButton in self.List_Button:
            self.List_Button[dButton].destroy()
        print(self.OpenD)
        if self.OpenD == "on":
            self.delete_Lable.destroy()
            self.OpenD = "off"
        # 清空字典
        self.List_Button = {}
        numx = 0
        numy = 1
        save_path = fr"{self.file_Path}\\Trainer_Info.json"
        with open(save_path, "r") as f:
            data = json.load(f)
        all_keys = list(data.keys())
        # 循环输出键值
        for key in all_keys:
            # 图片地址
            img_Path = data[key]["GameImg"]
            # 游戏名称
            gameName = data[key]["GameName"]
            # 修改器地址
            TrainerPath = data[key]["TrainerPath"]
            # 检测图片和修改器记录地址是否有东西
            if os.path.exists(img_Path) and os.path.exists(TrainerPath):
                print("文件夹地址:->", TrainerPath.rsplit("/", 1)[0])
                gameList_image = customtkinter.CTkImage(
                    light_image=Image.open(img_Path), size=(140, 80))

                self.List_Button[key] = customtkinter.CTkButton(self.TrainerList_frame, image=gameList_image,
                                                                text=gameName,
                                                                height=110, anchor='nsew', compound="top",
                                                                command=lambda TPath=str(TrainerPath): threading.Thread(
                                                                    target=self.openTrainer,
                                                                    args=(TPath,),
                                                                    daemon=True).start())
                if numx >= 3:
                    numy += 1
                    # self.TrainerList_frame.grid_columnconfigure(numy,weight=1)
                    numx = 0
                self.List_Button[key].grid(row=numy, column=numx, padx=5, pady=5, sticky="nsew")
                numx += 1
            else:
                # 没有文件不删了干锤子?
                print("删除文件不存在的记录")
                del data[key]
                # 保存修改后的JSON文件
                with open(save_path, 'w') as ff:
                    json.dump(data, ff)
                # 顺带手给文件夹也扬了
                os.remove(TrainerPath.rsplit("/", 1)[0])
        return None

    # 打开修改器
    def openTrainer(self, TrainerPath):
        os.startfile(TrainerPath)

    # 删除模式
    def delete_Trainer(self):
        self.delete_Lable = customtkinter.CTkLabel(self.TrainerList_frame, text="- - - - - 删除修改器模式 - - - - -")
        self.delete_Lable.grid(row=1, column=0, padx=5, pady=5, columnspan=3, sticky="nsew")
        self.OpenD = "on"
        # 删除按钮
        for dButton in self.List_Button:
            self.List_Button[dButton].destroy()
        # 清空字典
        self.List_Button = {}
        numx = 0
        numy = 2
        save_path = fr"{self.file_Path}\\Trainer_Info.json"
        with open(save_path, "r") as f:
            data = json.load(f)
        all_keys = list(data.keys())
        # 循环输出键值
        for key in all_keys:
            # 图片地址
            img_Path = data[key]["GameImg"]
            # 游戏名称
            gameName = data[key]["GameName"]
            # 删除修改器地址
            deleteTrainerPath = data[key]["TrainerPath"].rsplit("/", 1)[0]
            gameList_image = customtkinter.CTkImage(
                light_image=Image.open(img_Path), size=(140, 80))

            self.List_Button[key] = customtkinter.CTkButton(self.TrainerList_frame, image=gameList_image,
                                                            text=gameName,
                                                            height=110, anchor='nsew', compound="top",
                                                            command=lambda DPath=str(deleteTrainerPath),
                                                                           NameKey=str(key): threading.Thread(
                                                                target=self.deleteTrainercommand,
                                                                args=(DPath, NameKey),
                                                                daemon=True).start())
            if numx >= 3:
                numy += 1
                numx = 0
            self.List_Button[key].grid(row=numy, column=numx, padx=5, pady=5, sticky="nsew")
            numx += 1
        return None

    def deleteTrainercommand(self, DeletePath, ListKey):
        save_path = fr"{self.file_Path}\\Trainer_Info.json"
        with open(save_path, "r") as f:
            data = json.load(f)
        print("删除文件记录")
        del data[ListKey]
        # 保存修改后的JSON文件
        with open(save_path, 'w') as ff:
            json.dump(data, ff, indent=2)
        # 顺带手给文件夹也扬了
        shutil.rmtree(DeletePath)
        # 刷新界面
        self.delete_Trainer()
        return None

    # ---------- 下载器 -------------
    # 搜索用线程池
    def Srarch_lock(self):
        try:
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
            print('allGameName:', allGameName)

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
                                                                     command=lambda n=game, img=game_Img_Url,
                                                                                    gurl=Gameurl: threading.Thread(
                                                                         target=self.download_Trainer,
                                                                         args=(n, gurl, img),
                                                                         daemon=True).start())
                    self.item_Button[game].grid(row=num, column=0, padx=10, pady=(10, 0), sticky="sw")
                    print('游戏名：', game.rsplit(" ", 1)[0])
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
        except Exception as e:
            # 无对应游戏弹窗
            showinfo(title='搜索结果', message=f'1未能查找到对应名称游戏 ！\n请检查名称或扩大范围搜索\n{e}')
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
    def download_Trainer(self, game_Name, game_url, game_Img):
        try:
            print('标识：', game_Name)
            print('游戏链接:', game_url)
            game_Name_split = game_Name.rsplit(" ", 1)[0]
            print('下载修改器游戏名：', game_Name.rsplit(" ", 1)[0])

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
            # ---- 将基础格式和信息写入json ----
            # ---- 保存对应游戏封面 ----
            img_Split = name.rsplit(" ", 1)[0]
            header_image_path = f"{path}{name}/{img_Split}.jpg"
            print("图片保存位置：->", header_image_path)
            print("图片下载链接：->", game_Img)
            self.Img_Path(Img_url=game_Img, File_name=header_image_path)
            # ---- 保存修改器本地地址 ----
            filePath = f"{path}{name}/"
            TrainerPath = method.find_files_with_suffix(folder_path=filePath, suffix=".exe")
            Trainer_File_Path = filePath + TrainerPath[0]
            # ---- 写入信息 ----
            self.Info_Json_append(Game_Name=game_Name_split, Img_Path=header_image_path, Trainer_Path=Trainer_File_Path,
                                  Img_Url=game_Img)
            # 下载完成弹窗
            showinfo(title='下载进度', message='下载已完成，自动解压并删除压缩包')
        except Exception as e:
            print("报错信息:->", e)
            showinfo(title='错误信息', message=f'{e}')

    # 读取保存地址信息
    def download_path_Read(self):
        DW_path_Read = f'{self.file_Path}\\Download_path.txt'
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
        DW_path = f'{self.file_Path}\\Download_path.txt'
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

    # ---- 初始化储存修改器信息 ----
    def Trainer_Info_Json(self):
        save_path = fr"{self.file_Path}\\Trainer_Info.json"
        if os.path.exists(save_path):
            print(f'文件{save_path}存在')
            return None
        else:
            data = {}
            with open(save_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print("创建初始文件json")
            return None

    # ---- 新增修改器信息 ----
    def Info_Json_append(self, Game_Name, Img_Path, Trainer_Path, Img_Url):
        '''

        :param Game_Name: 游戏名称
        :param Img_Path: 封面图片地址
        :param Trainer_Path: 修改器地址
        :param Img_Url: 图片网络地址
        :return: 蛋
        '''
        save_path = fr"{self.file_Path}\\Trainer_Info.json"
        with open(save_path, "r") as f:
            data = json.load(f)
        # 判断是否已拥有游戏信息
        allkeys = list(data.keys())
        if Game_Name in allkeys:
            # 有记录了，那只好修改咯
            print("已经拥有该游戏记录")
            data[str(Game_Name)]["GameName"] = str(Game_Name)
            data[str(Game_Name)]["GameImg"] = str(Img_Path)
            data[str(Game_Name)]["ImgUrl"] = str(Img_Url)
            data[str(Game_Name)]["TrainerPath"] = str(Trainer_Path)
            with open(save_path, "w") as ff:
                json.dump(data, ff)
            return None
        else:
            data[str(Game_Name)] = {
                "GameName": str(Game_Name),
                "GameImg": str(Img_Path),
                "ImgUrl": str(Img_Url),
                "TrainerPath": str(Trainer_Path)
            }
            with open(save_path, "w") as ff:
                json.dump(data, ff)
            return None

    # ---- 下载图片 ----
    def Img_Path(self, Img_url, File_name):
        '''

        :param Img_url: 图片网络地址
        :param File_name: 图片要保存的位置[本地地址+保存名字.jpg]
        :return: ?
        '''
        print("网络地址：->", Img_url)
        print("保存地址:->", File_name)
        # 请求头
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
        headers['Referer'] = 'https://www.baidu.com/'
        response = requests.get(Img_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(File_name, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
                print('图片下载成功！')
        else:
            print('图片下载失败！')
        return None

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
