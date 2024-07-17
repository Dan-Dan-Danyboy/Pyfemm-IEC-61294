#Imported libraries
import femm
from PIL import Image
import os
import numpy as np
from matplotlib import pyplot as plt

class standard:
  def __init__(self,document,voltage,dielectric_permitivity,conductivity):
    self.document = document #document is the path to the .FEC document
    self.voltage = voltage
    self.dielectric_permitivity = dielectric_permitivity
    self.conductivity = conductivity

  #The following function calculares the total current flow in the circuit based on Kirchhofs laws
  #The coordinates are chosen to match the .FEC document
  def calculate_current(x1=2228*100,x2=2268*100,y=1120):
    q = 0
    for x in range(x1,x2,100):
      x = x/100
      Jx,Jy = femm.co_getpointvalues(x,y)[1:3]
      J = ((abs(Jx))**2+(abs(Jy))**2)**(1/2)
      q += J/100
    return J

  def 
  
