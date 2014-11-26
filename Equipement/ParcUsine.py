# -*-coding:Utf-8 -*
from Equipement import Equipement
from Utilitaire.heure import Utilitaire
from Utilitaire import Global
from math import *

class ParcMaison (Utilitaire) : 
    def __init__(self, nom, production = 1, nombre = 0): #consommation moyenne de environ 1kW/maison -->heure basse 0,7kW/maison
       self.nombre=nombre      
       self.production = production # en kW/maison
       self.production_totale = 0.0
       self.production = 0
       self.PROD_MAX=2.0*nombre  # consommation de 2kW par maison (pic)
       self.effacement=0.0 # en %
       self.activite=50.0
       self.EFFA_MAX = 0.1 # en kWglobal

    def ajouterMaison(self,nombre_maisons):
        self.nombre += nombre_maisons
        print("{0} maisons dans le parc".format(self.nombre))
        
    def consommation_maison(self):
        temps=Global.temps
        if temps>720 and temps<=1008:
            self.production = -1-cos(pi/72*(temps-792))
        else :
            self.production = -1 - cos(pi/144.0*(temps+30.0))*cos(3.0*(pi/144.0*(temps+30)))
        return self.production
    
    def production_elec_totale(self):
        self.production_totale = self.production * self.nombre
        return self.production_totale
        

    def donner_conso(self):
        temps=Global.temps
        print ("{0} minutes , total production : {1}  kW").format(temps*10, self.production_elec_totale())

    def effacement_maison(self, pourcentage=0):  
        self.effacement_absolu =  pourcentage*self.consommation_maison()/100.0
        if self.effacement_absolu< self.EFFA_MAX :
            self.production_totale=(100-pourcentage)*self.production_totale/100
            self.effacement = pourcentage
        else : 
            print("effacement maximum depasse")    
        return self.production_totale
    
    def etatSuivant(self,consigne=0,effacement=0):
        p=self.production[Global.temps]
        if p>=effacement*self.EFFA_MAX/self.PROD_MAX:
            self.effacement=effacement
            self.activite=p-effacement*self.EFFA_MAX/self.PROD_MAX
        else:
            self.effacement=self.activite
            self.activite=0.0
        self.cout=self.effacement/100.0*self.EFFA_MAX*(80/1000/6)*self.nombre
        
    def prevision(self,consigne=0,effacement=0):
        p=self.production[(Global.temps+1)%1008]
        if p>=effacement*self.EFFA_MAX/self.PROD_MAX:
            return (p-effacement*self.EFFA_MAX/self.PROD_MAX,effacement/100.0*self.EFFA_MAX*(80/1000/6)*self.nombre)
        else :
            return (0,p/100.0*self.PROD_MAX*(80/1000/6)*self.nombre)
    
    def simulation(self):
        (prod_min,cout_min)=self.prevision(0,0)  
        (prod_max,cout_max)=self.prevision(0,100) 
        return(prod_min,prod_max,cout_min,self.cout,cout_max)      
