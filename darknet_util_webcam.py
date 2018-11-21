# !/usr/bin/env python
# -*- coding: utf-8 -*-

# Código escrito por José Paulo Oliveira Filho 
# Última edição: 21/11/2018
# Objetivo: Automatizar processo de captura de imagem e deteccao/classificacao de objetos usando a biblioteca Darknet (https://github.com/AlexeyAB/darknet)
# Obs.: Essa é uma variação do código original, visando viabilizar a captura de imagens utilizando uma webcam comum ao invés de uma PiCamera.

# Requer a biblioteca pytz (pip install pytz)
# Requer a biblioteca pygame (pip install pygame)
# Requer ser executado a partir da pasta de instalacao do Darknet

# ----- DEFINIÇÕES INICIAIS ----- #

# bibliotecas de manipulação do sistema
import errno, os, subprocess
# criação de timestamp
from datetime import datetime
from pytz import timezone
# bpygame
import pygame
import pygame.camera
# sleep
from time import sleep

# hardcode do caminho das imagens
caminho = "/home/agharium/Desktop/snapshots/"
try:
  os.makedirs(caminho)
except OSError as e:
  if e.errno != errno.EEXIST:
    raise

# definição da PiCamera
pygame.camera.init()
camera = pygame.camera.Camera("/dev/video0",(640,480))
camera.start()
    
# ----- CLASSE IMAGEM E SUAS FUNÇÕES ----- #

class Imagem(object):
  # construtor
  def __init__(self):
    # define os nomes da imagem e do diretório da imagem (que são o timestamp atual)
    self.imgNome = getTimestamp()
    self.diretorio = caminho + self.imgNome + "/"
    # armazena o caminho absoluto da imagem
    self.imgCaminhoAbsoluto = self.diretorio + self.imgNome + ".jpg"
    # captura a imagem
    self.capturaImagem()
    # processa a imagem com o darknet e armazena os objetos encontrados
    self.objetos = self.processaImagem()
    
  # captura uma imagem
  def capturaImagem(self):
    os.makedirs(self.diretorio)

    img = cam.get_image()
    pygame.image.save(img, self.imgCaminhoAbsoluto)

  # processa a imagem com o Darknet, armazenando lista de elementos encontrados na imagem
  def processaImagem(self):
    print("Capturando imagem e processando imagem...")

    p1 = subprocess.Popen('./darknet detect cfg/yolov3-tiny.cfg yolov3-tiny.weights \"' + self.imgCaminhoAbsoluto + '\"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p1.communicate()
    stdout = stdout.split("\n")

    # variável de retorno
    objetos = {}

    for line in stdout:
      if '%' in line:
        nomeObjeto = line.split(': ')[0]
        #print("OBJETO: " + nomeObjeto
        #print("CERTEZA: " + line.split(': ')[1])
        #print("-------")
        
        qtdObjeto = objetos.get(nomeObjeto, 0)
        objetos[nomeObjeto] = qtdObjeto + 1
        sleep(1)
        p2 = subprocess.Popen('mv predictions.png \"' + self.diretorio + self.imgNome + '.png\"', shell=True)
        p2.wait()
    p1.wait()

    return objetos
      
# ----- FUNÇÕES AUXILIARES ----- #
  
# retorna o timestamp atual
def getTimestamp():
  horaLocal = timezone('America/Sao_Paulo')
  timestamp = datetime.now()
  timestamp = horaLocal.localize(timestamp)
  return timestamp.strftime('%Y-%m-%d %H:%M:%S')

# compara objetos recebendo dois objetos do tipo Imagem
def comparaObjetos(img1, img2):
  for objeto in img1.objetos:
    if (objeto not in img2.objetos):
      n = img1.objetos[objeto]
      print(n, objeto, ("desapareceram!" if n > 1 else "desapareceu!"))
    else:
      objQtd1 = img1.objetos[objeto]
      objQtd2 = img2.objetos[objeto]
      if (objQtd1 != objQtd2):
        diferenca = objQtd1 - objQtd2
        if (diferenca > 0):
          print(str(diferenca) + " " + objeto + (" desapareceram!" if diferenca > 1 else " desapareceu!"))
        else:
          diferenca = diferenca*(-1)
          print(str(diferenca) + " " + objeto + (" apareceram!" if diferenca > 1 else " apareceu!"))
      else:
        print ("Não houve nenhuma diferença em relação ao objeto " +  objeto + ".")
      
  for objeto in img2.objetos:
    if (objeto not in img1.objetos):
      n = img2.objetos[objeto]
      print(str(n) + " " + objeto + (" apareceram!" if n > 1 else " apareceu!"))

# ----- EXECUÇÃO DO PROGRAMA ----- #

imagem1 = Imagem()
print("\nOBJETOS ENCONTRADOS NA IMAGEM:" + str(imagem1.objetos) + "\n-------")

while True:
  imagem2 = Imagem()
  print("\nOBJETOS ENCONTRADOS NA IMAGEM:" + str(imagem2.objetos) + "\n-------")
  sleep(5)

  print("COMPARAÇÃO DE OBJETOS:")
  comparaObjetos(imagem1, imagem2)
  print("-------")

  imagem1 = imagem2
