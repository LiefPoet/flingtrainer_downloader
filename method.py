import os
import zipfile
import rarfile
import requests
from bs4 import BeautifulSoup

import frozen_dir


#获取对应游戏名称
def Srarch_GameName(GameName):
    #游戏名称列表
    gameNameList = []
    # 主要网址
    main_url = f'https://flingtrainer.com/?s='+GameName
    # 请求头
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
    headers['Referer'] = 'https://www.baidu.com/'
    # 访问网站
    main_req = requests.request(url=main_url, headers=headers, method='GET')
    # 开始解析网站
    soup = BeautifulSoup(main_req.text, 'html.parser')
    # 获取全部对应标签内游戏名称
    find_mainRul = soup.find_all(rel="bookmark")
    for gameName in find_mainRul:
        a = gameName.text
        gameNameList.append(a)
    #返回游戏名称
    return gameNameList

#获取对应游戏链接
def Srarch_GameURl(GameName):
    #游戏链接列表
    gameURLList = []
    # 主要网址
    main_url = f'https://flingtrainer.com/?s='+GameName
    # 请求头
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
    headers['Referer'] = 'https://www.baidu.com/'
    # 访问网站
    main_req = requests.request(url=main_url, headers=headers, method='GET')
    # 开始解析网站
    soup = BeautifulSoup(main_req.text, 'html.parser')
    # 获取全部对应标签内游戏名称
    find_mainRul = soup.find_all(rel="bookmark")
    #获取游戏链接
    for gameURL in find_mainRul:
        a = gameURL['href']
        gameURLList.append(a)
    #返回游戏链接
    return gameURLList

#下载文件
def download_file(url, local_path):

    # 请求头
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
    headers['Referer'] = 'https://www.baidu.com/'
    try:
        res = requests.get(url,headers=headers)
        #获取文件名称
        fileName = res.url.split("/")[-1]
        #res.raise_for_status()
        with open(local_path+f'/{fileName}',"wb") as file:
            file.write(res.content)
            file.flush()
        print("ok")
        print(fileName)
    except requests.exceptions.RequestException as e:
        print("no")



#解压修改器压缩包
def zip_decompress(file_path, new_path,gameMenuName):
    """支持中文的解压缩程序
    file_path：原压缩包文件路径
    new_path：新文件夹路径
    gameMenuName:游戏名字
 """
    if file_path.split('.')[-1] == 'zip':
        #利用游戏名字创建文件夹
        gameMenu_folder(gameMenuName)
        z = zipfile.ZipFile(file_path, 'r')
        #将解压地址改为新创建文件夹内
        newName_path = new_path + f"{gameMenuName}/"
        z.extractall(path=newName_path)
    else:
        #rarfile解压
        #重新定义unrar文件位置
        rarfile.UNRAR_TOOL = frozen_dir.app_path()+"/Set/unrar"
        # 利用游戏名字创建文件夹
        gameMenu_folder(gameMenuName)
        #除开名字跟zipfile一样的操作
        z = rarfile.RarFile(file_path, 'r')
        # 将解压地址改为新创建文件夹内
        rarnewName_path = new_path + f"{gameMenuName}/"
        z.extractall(path=rarnewName_path)

# 本地根目录创建文件夹
def gameMenu_folder(gameName):
    save_path = frozen_dir.app_path() + fr"/Download/{gameName}/"
    if os.path.exists(save_path):
        print(f'文件{save_path}存在')
    else:
        print(f'文件{save_path}不存在')
        os.mkdir(save_path)