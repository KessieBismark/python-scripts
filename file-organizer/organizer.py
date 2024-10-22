import os
import shutil

pathDir = input("Enter your path: ")


files = os.listdir(pathDir)


for file in files:
    filename, extension = os.path.splitext(file)
    
    
    extension = extension[1:]


    if os.path.exists(pathDir + '/' + extension):
        shutil.move(pathDir + '/' + file, pathDir + '/' + extension + '/' + file)
    else:
        os.makedirs(pathDir + '/' + extension)
        shutil.move(pathDir + '/' + file, pathDir + '/' + extension + '/' + file)
