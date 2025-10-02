import os
import zipfile
import rarfile
import requests
from bs4 import BeautifulSoup

#获取对应游戏名称
def Srarch_GameName(GameName):
    #游戏名称列表
    gameNameList = []
    gameImgList = []
    # 游戏链接列表
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
    #查看是否有对应游戏
    No_Game =soup.find('h1')
    No_Game_Text = '0 Search results'
    if No_Game_Text in No_Game.text:
        return None
    else:
        # 获取全部对应标签内游戏名称
        find_mainRul = soup.find_all(rel="bookmark")
        # 获取图片
        find_mainimg = soup.find_all('img', width="200", height="200")

        for link in find_mainimg:
            gameImgList.append(link['src'])
        for gameName in find_mainRul:
            a = gameName.text
            gameNameList.append(a)
        # 获取游戏链接
        for gameURL in find_mainRul:
            a = gameURL['href']
            gameURLList.append(a)
        # 合并字典
        game_List = dict(zip(gameNameList, gameImgList))
        # 修改器对应网址
        gameRul_List = dict(zip(gameNameList, gameURLList))
        print("图片地址:",game_List)
        # 返回游戏信息
        return game_List, gameRul_List, gameNameList


#下载文件
def download_file(url, local_path,game_name):
    '''

    :param url:
    :param local_path:
    :return:
    '''

    # 请求头
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
    headers['Referer'] = 'https://www.baidu.com/'
    try:
        print("下载链接原始地址：",url)
        res = requests.get(url,headers=headers)
        print("下载链接：",res)

        # 判断有无名字
        content_disposition = res.headers.get("Content-Disposition")
        print('文件类型:', content_disposition)
        filename = ""
        if content_disposition:
            filename = content_disposition.split("filename=")[-1].strip("\"'")
        if not filename:
            filename = "unknown_file"
        # 获取后缀名
        filename_extension = filename.split(".")[-1]

        # 保存路径
        save_path = local_path
        print("保存路径:->",save_path)
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path+game_name, filename)
        print("文件存储地址:->",file_path)

        # 判断能否解压
        if filename_extension == 'zip' or filename_extension == 'rar':
            # 下载文件
            print(" --------- 进入下载文件 ----------")
            file_path_zip = os.path.join(save_path, filename)
            with open(file_path_zip, "wb") as file:
                file.write(res.content)
            #解压程序
            zip_decompress(file_path=file_path_zip,new_path=local_path,gameMenuName=game_name)
            print(" --------- 执行完解压程序 ----------")
            # 删除原压缩包
            package_File = content_disposition.split("filename=")[-1].strip("\"'")
            if os.path.exists(local_path+package_File):  # 检查文件是否存在
                os.remove(local_path+package_File)
            print(" --------- 执行完删除原压缩包 ----------")
        else:
            # 创建对应文件夹
            gameMenu_folder(gameName=game_name, newpath=local_path)
            print(" --------- 创建完对应文件夹 ----------")
            exe_File_path = local_path + game_name
            # 下载文件
            # 很好，这辈子没想到是因为多加了个 / 导致报错
            with open(file_path, "wb") as file:
                file.write(res.content)
            print(" --------- 下载完对应文件 ----------")
        #获取文件名称
        #fileName = res.url.split("/")[-1]
        #res.raise_for_status()
        print("ok")
        print(game_name)
        print("file_path:->",file_path)
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
        gameMenu_folder(gameMenuName,newpath=new_path)
        z = zipfile.ZipFile(file_path, 'r')
        #将解压地址改为新创建文件夹内
        newName_path = new_path + f"/{gameMenuName}/"
        z.extractall(path=newName_path)
    elif file_path.split('.')[-1] == 'rar' :
        #rarfile解压
        #重新定义unrar文件位置
        file_Path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        rarfile.UNRAR_TOOL = f"{file_Path}\\unrar"
        # 利用游戏名字创建文件夹
        gameMenu_folder(gameMenuName,newpath=new_path)
        #除开名字跟zipfile一样的操作
        z = rarfile.RarFile(file_path, 'r')
        # 将解压地址改为新创建文件夹内
        rarnewName_path = new_path + f"/{gameMenuName}/"
        z.extractall(path=rarnewName_path)

# 本地根目录创建文件夹
def gameMenu_folder(gameName,newpath):
    '''

    :param gameName: 游戏名称
    :param newpath: 新建地址
    :return:
    '''
    save_path = newpath + fr"{gameName}/"
    if os.path.exists(save_path):
        print(f'文件{save_path}存在')
    else:
        print(f'文件{save_path}不存在')
        os.mkdir(save_path)

# 读取文件夹指定类型文件
def find_files_with_suffix(folder_path, suffix):
   '''

   :param folder_path: 文件路径
   :param suffix: 指定后缀名
   :return: ？
   '''
   # 使用os.listdir获取文件夹中所有文件的路径
   all_files = os.listdir(folder_path)
   # 筛选出以指定后缀结尾的文件
   filtered_files = [file for file in all_files if file.endswith(suffix)]
   return filtered_files

#download_file('https://flingtrainer.com/downloads/JxkH0y_ocORjmJnS_Z2DTA','D:\Python项目\FLYY_new/Download/')