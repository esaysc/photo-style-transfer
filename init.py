import subprocess
import os
from pathlib import Path
import time  
import sys
import json
 

# .py, .qml, .qrc, .ts, .ui
suffixList = ['.py', '.qml', '.qrc', '.ts', '.ui']
# 获取当前脚本文件的绝对路径
current_file = os.path.abspath(sys.argv[0]).replace("\\","/")
# 获取当前脚本文件所在的目录
current_directory = os.path.dirname(current_file)
# 文件夹路径
basePath = current_directory
appPath = basePath + "/app/"
commonPath = basePath + "/app/common/"
resourcePath = basePath + "/app/resource/"
i18nPath = basePath + "/app/resource/i18n/"

# 文件路径
resourcePy = commonPath + "resource.py"
resourceQrc = resourcePath + "resource.qrc"
galleryPro = basePath + "/gallery.pro"

# 相对于当前脚本文件所在目录的相对路径
relative_path = './sub_directory/file.txt'

# 解析相对路径为绝对路径
absolute_path = os.path.join(current_directory, relative_path)

def alter(file,old_str,new_str):
    """
    将替换的字符串写到一个新的文件中，然后将原文件删除，新文件改为原来文件的名字
    :param file: 文件路径
    :param old_str: 需要替换的字符串
    :param new_str: 替换的字符串
    :return: None
    """
    with open(file, "r", encoding="utf-8") as f1,open("%s.bak" % file, "w", encoding="utf-8") as f2:
        for line in f1:
            if old_str in line:
                print(line)
                line = line.replace(old_str, new_str)
            f2.write(line)
    os.remove(file)
    os.rename("%s.bak" % file, file)

def pylupdate6(name):
    os.system("cd " + basePath + " && pylupdate6 ./app -ts ./app/resource/i18n/" + name + ".ts")

def pylupdate6_noobsolate(name):
    os.system("cd " + basePath + " && pylupdate6 --no-obsolete ./app -ts ./app/resource/i18n/" + name + ".ts")

def lrelease(name):
    os.system("cd " + basePath + " && pyside6-lrelease ./app/resource/i18n/" + name + ".ts" + " -qm ./app/resource/i18n/" + name + ".qm") 
def lupdate(name):
    
    pathlist = Path(appPath).glob("**/*.py")
    for path in pathlist:
        if(os.path.basename(str(path)).find("resource")) != -1:
          continue
        # print(path)
        print(os.path.basename(str(path)))
        # os.system("cd " + basePath + " && pyside6-lupdate " + str(path) + " -ts ./app/resource/i18n/"+ name)
        return
def update_pyproject():
    article_info = {}
    data = json.loads(json.dumps(article_info))
    files = []
    
    for suffix in suffixList:
        pathlist = Path(basePath).glob("**/*" + suffix)
        for path in pathlist:
            pathStr = str(path).replace("\\","/")
            if (os.path.basename(str(pathStr)).find("init")) != -1:
                continue
            item = pathStr.replace(basePath, ".")
            files.append(item)
    data['files'] = files
    article = json.dumps(data, ensure_ascii=False)

    # 写入文件
    with open('photo-style-transfer.pyproject', 'w', encoding='utf-8') as f:
        f.write(article)
# 未完成
def update_pro():
     # 写入文件
    with open('gallery.pro', 'w', encoding='utf-8') as f:
        for suffix in suffixList:
            pathlist = Path(appPath).glob("**/*.py")
            for path in pathlist:
                pathStr = str(path).replace("\\","/")
                item = pathStr.replace(basePath, ".")
        # f.write(article)
def projectRun():
    os.system("pyside6-project run ")

# os.system("dir")
# projectRun()
# update_pro()
# update_pyproject()
# # 翻译文件
# pylupdate6("gallery.zh_CN")
# # 编译翻译文件为二进制文件 提供给运行时程序
# lrelease("gallery.zh_CN")
# rcc = os.system("cd " + resourcePath + " && pyside6-rcc -o ../common/resource.py resource.qrc") # 使用a接收返回值
# print(rcc)
os.system("pip freeze > requirements.txt")