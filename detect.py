# -*- coding: UTF-8 -*-
import numpy as np
import cv2
import sys, getopt
import os
import time
import glob


def printHelp():
    print('python detect.py --min_similaridade <minimo de similaridade> --max_size <tamanho da lista de resultados> QUERY DIRETORIO')
    print('\nOnde query é uma imagem ou video e diretorio é uma pasta para com imagens ou videos.')
    print('\nOs parâmetros min_similaridade e max_size são opcionais. Caso não informe, um valor default será definido.')

def isImgOrVideo(fileName):
    if(fileName.endswith(".jpg") or fileName.endswith(".png")):
        return 0
    if(fileName.endswith(".mp4") or fileName.endswith(".avi")):
        return 1
    return -1
    
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["min_similaridade=", "max_size="])
except getopt.GetoptError:
    printHelp
    
if len(args) != 2:
    printHelp

min_similaridade = 0.75       # similaridade padrão
max_size = 10000               # 10k default
query = args[0]
diretorio = args[1]


arquivosSimilares = []


for opt, arg in opts:
    if(opt == "-h" or opt == "--h"):
        printHelp()
        quit();
    
    if(opt == "--min_similaridade"):
        try:
            min_similaridade = float(arg)
            if(min_similaridade > 1 or min_similaridade < 0):
                print("--min_similaridade deve ser um numero entre 0.0 e 1")
        except ValueError:
            print("--min_similaridade deve ser um número entre 0.0 e 1")
            quit()
    if(opt == "--max_size"):
        try:
            max_size = int(arg)
        except ValueError:
            print("--max_size deve ser um numero")
            quit()

#print("min_similaridade: " + str(min_similaridade))
#print("max_size: " + str(max_size))
#print("query: " + args[0])
#print("dir: " + args[1])

imgOrVideo = isImgOrVideo(query)
if(imgOrVideo == -1):
    print("Query deve ser uma imagem ou um video")
    quit()

if(imgOrVideo == 0):
    print("Carregando query: " + query)
    frame = cv2.imread(query)
    
cap = 0
if(imgOrVideo == 1):
    cap = cv2.VideoCapture(query)

cont = 0
flag = 0

arquivos=glob.glob(diretorio+"/*.png")
arquivos.extend(glob.glob(diretorio+"/*.jpg"))
arquivos.extend(glob.glob(diretorio+"/*.mp4"))
arquivos.extend(glob.glob(diretorio+"/*.avi"))

# arquivos = arquivos do diretorio
# capArquivo = captura do video do arquivo do diretorio

# frame = frame da query
# cap = captura do video da query

for arquivo in arquivos:
    tipoArquivoAtual = isImgOrVideo(arquivo)
    print("Analisando o arquivo: " + arquivo + " = > " + str(tipoArquivoAtual))

    if tipoArquivoAtual == 0:
        frameArquivo = cv2.imread(arquivo)
        
    capArquivo = 0
    if tipoArquivoAtual == 1:
        capArquivo=cv2.VideoCapture(arquivo)


    simArquivo = []


    while((capArquivo != 0 and capArquivo.isOpened()) or tipoArquivoAtual == 0):
        if tipoArquivoAtual == 1:
            retArquivo, frameArquivo = capArquivo.read()
        if(capArquivo == 0 or retArquivo==True):
            if(cap!=0):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            while((cap != 0 and cap.isOpened()) or imgOrVideo == 0):
                flag = flag+1
                if imgOrVideo == 1:
                    ret, frame = cap.read()
                if cap==0 or ret==True:
                    img = frame
                    
                    try:
                        #cv2.imshow("Query", frame)
                        #cv2.imshow("Arquivo", frameArquivo)
                        #cv2.waitKey(1)
                        res = cv2.matchTemplate(img, frameArquivo, cv2.TM_CCOEFF_NORMED) # verifica a similiaridade
                        min_val, similaridade, min_loc, max_loc = cv2.minMaxLoc(res)

                        if similaridade >= min_similaridade: # está dentro
                            print("Encontrou: " + str(similaridade))
                            simArquivo.append(similaridade)
                        else:
                            print("Nao encontrado: " + str(similaridade))
                    except Exception as exp:
                        print("ERROR AO ANALISAR")
                        print(exp)
                        if imgOrVideo == 0:
                            break;
                        continue
                else:
                    break
                
                if imgOrVideo == 0:     # não tem while se for apenas uma imagem
                    break;
        else:
            break;
        if tipoArquivoAtual == 0:       # não tem while se for apenas uma imagem
            break;
    simArquivo = np.array(simArquivo)
    if simArquivo.size > 0:
        mediaSimilaridade = simArquivo.mean()
        arquivosSimilares.append((arquivo, mediaSimilaridade))
            


if len(arquivosSimilares) > 0 and max_size > 0:
    arquivosSimilares.sort(key=lambda x:x[1], reverse=True) # ordena a lista
    print("Arquivos Similares: ")
    count = 1
    for arquivoSimilar in arquivosSimilares:
        print(str(count) + " - " + arquivoSimilar[0] + ": " + str(round(arquivoSimilar[1]*100, 2)) + "%")
        count=count+1
        if count > max_size:
            break;
else:
    print("Nenhum arquivo similar encontrado.")
cv2.destroyAllWindows()