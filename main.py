# -*-coding:utf-8 -*


#from Equipement import *

from Ville import Ville
from Utilitaire.heure import Utilitaire
from Utilitaire import Global
from Utilitaire.Global import temps
from Utilitaire.Global import meteo1
from Utilitaire.Global import meteo2
from Utilitaire.Global import meteoTest
from Utilitaire.BaseDeDonnees import BaseDeDonnees
from Utilitaire import Global
import sys


"""Import de la base de données"""

#commande main.py duree=24*6 nomdutest=0 datededébut=0
analyseur=False
if( len(sys.argv)>1):
    Global.duree=eval(sys.argv[1])
    analyseur=True
if(len(sys.argv)>2):
    Global.numtest=sys.argv[2]
if(len(sys.argv)>3):
    Global.temps=eval(sys.argv[3])
"""initialisation de la Ville dans l'objet Ville"""
ville = Ville()
numTest = Global.numtest
Global.duree += Global.temps#décalage si présence d'un offset
duree = Global.duree
    


def ind_eqpascher(liste,consigne): #pour prod MAX !! indice de l'equipement le moins cher, liste comme simulations

    i=0
    while (abs(consigne[i] - liste[i][1]) <= 0.05*consigne[i]):
        i += 1
    cout_min = liste[i][4]
    for j in range (0,len(liste)):
        if (liste[j][4] < cout_min and abs(consigne[j] - liste[j][1]) > 0.05*consigne[j]): #si moins cher et pas encore mis au max
            i=j
    return i

def ind_eqpascher2(liste,consigne): #pour prod MIN !! indice de l'equipement le moins cher, liste comme simulations
    i=0
    while (abs(consigne[i] - liste[i][0]) <= 0.05*consigne[i]):
        i += 1
    cout_min = liste[i][3]
    for j in range (0,len(liste)):
        if (liste[j][3] < cout_min and abs(consigne[j] - liste[j][0]) > 0.05*consigne[j]): #si moins cher et pas encore mis au max
            i=j
    return i

Global.db.vide_table(numTest)
Global.db.enregistrerID(ville.equipProduction, ville.equipConso, ville.equipStockage, numTest)
Global.db.enregistrerEtape(ville.equipProduction, ville.equipConso, ville.equipStockage, numTest)
Global.db.enregistrerConsigne([0 for i in range(ville.nombreEquipementProduction)], [0 for i in range(ville.nombreEquipementConso)],[0 for i in range(ville.nombreEquipementStockage)], numTest) 

while Global.temps < duree-1: #boucle principale
    prod_actuelle = sum(i.activite/100.*i.PROD_MAX for i in ville.equipProduction)
    conso_future = sum(-i.production[Global.temps + 1]/100.*i.PROD_MAX for i in ville.equipConso)

    diff = conso_future-prod_actuelle # différence conso-production actuelle
    print "diff:%s"%diff
    effacement_actuel = 0.
    
    consigne = [i.activite for i in ville.equipProduction] # liste des consignes equipements de production
    simulations = [i.simulation() for i in ville.equipProduction] #liste représentant les equipements de production pour l'etape suivante
    
    consigne_stock = [i.activite for i in ville.equipStockage] # "" de stockage
    simulations_stock=[i.simulation() for i in ville.equipStockage]
    
    consigne_conso = [0. for i in range(len(ville.equipConso))] # "" de consommation étalonné sans effacement
    simulations_conso = [i.simulation() for i in ville.equipConso]

    if diff > 0.: #on consommera plus qu'on ne produit
        max = sum(i.simulation()[1]/100.*i.PROD_MAX for i in ville.equipProduction) #capacite de production maximale à l'etat suivant
        
        if max >= conso_future: # si on peut atteindre la valeur de la consommation...
            prod_provisoire = prod_actuelle
            
            while (abs(prod_provisoire-conso_future) > 2./100.*conso_future and prod_provisoire < conso_future): #tant que ecart > 2% et prod < conso
                ind = ind_eqpascher(simulations,consigne) #indice de l'equipement le moins cher qu'on met au max
                equip = ville.equipProduction[ind]
                print ind
                
                
                if (simulations[ind][0] < simulations[ind][1]): #equipement à production laissant marge de maneuvre ex : centrale (et pas PV)
                    while (prod_provisoire < conso_future and abs(consigne[ind] - simulations[ind][1]) >= consigne[ind]*0.05):
                        consigne[ind] += (simulations[ind][1]-equip.activite)/10. #on met progressivement la production au max
                        prod_provisoire += (simulations[ind][1]-equip.activite)/100./10.*equip.PROD_MAX #maj
                        
                        #prod_provisoire = sum(consigne[i]/100.*ville.equipProduction[i].PROD_MAX for i in range(ville.nombreEquipementProduction))
                else:
                    print prod_provisoire
                    print consigne[ind]
                    print simulations[ind][1]
                    consigne[ind] = simulations[ind][1] #sinon on met à la production min = max (on n'a pas le choix)
                    prod_provisoire += (simulations[ind][1]- equip.activite)/100.*equip.PROD_MAX #maj
                    print prod_provisoire
                    #prod_provisoire = sum(consigne[i]/100.*ville.equipProduction[i].PROD_MAX for i in range(ville.nombreEquipementProduction))
        else: #on n'a pas suffisamment de production disponible
            for i in range (len(simulations)): # on met tout au max
                consigne[i] = simulations[i][1]
            print consigne
            prod_provisoire = sum(simulations[i][1]/100.*ville.equipProduction[i].PROD_MAX for i in range(len(simulations)))
            
            # il faut maintenant compenser la différence prod-conso avec du stockage et eventuellement de l'effacement
            stock_max = [simulations_stock[i][1] for i in range(len(simulations_stock))] #tous les stockages sont en mode "vidage maximal"
            while (abs(prod_provisoire-conso_future)/conso_future > 2./100. and prod_provisoire < conso_future and abs(sum(consigne_stock) - sum(stock_max)) >= sum(stock_max)*0.05):
                ind = ind_eqpascher(simulations_stock,consigne_stock) #stockage le moins cher à vider
                equip = ville.equipStockage[ind]
                print "stockage :"
                print ind
                
                print "conso future :"
                print conso_future
                while (abs(prod_provisoire-conso_future)/conso_future > 2./100. and prod_provisoire < conso_future and abs(consigne_stock[ind] - stock_max[ind]) >= 0.05*consigne_stock[ind]):
                    print "e"
                    consigne_stock[ind] += (simulations_stock[ind][1] - equip.activite)/10.
                    prod_provisoire += (simulations_stock[ind][1] - equip.activite)/100./10.*equip.PROD_MAX
                    #prod_provisoire = sum(simulations[i][1]/100.*ville.equipProduction[i].PROD_MAX for i in range(len(simulations)))
            conso_min = [(i.simulation()[1]-i.activite)*(i.PROD_MAX)/i.EFFA_MAX for i in ville.equipConso]
            '''production = - consommation ; 
               prod_min = - conso_max = conso sans effacement ;
               prod_max = - conso_min = conso avec effacement ; => cout_max = cout pour effacer
               effacement = prod_max - prod_min 
               attention prod_min  = -conso
            '''
            if (abs(sum(stock_max)-sum(consigne_stock)) <= sum(stock_max)*0.05):
                ind_boucle = len(ville.equipConso)
                while (abs(prod_provisoire-conso_future) > 2./100.*conso_future and prod_provisoire < conso_future and abs(sum(consigne_conso) - sum(conso_min)) >= sum(conso_min)*0.05):
                    ind = ind_eqpascher(simulations_conso, consigne_conso)
                    print ind
                    equip = ville.equipConso[ind]
                    consigne_conso[ind] = (simulations_conso[ind][1]-equip.activite)*(equip.PROD_MAX)/equip.EFFA_MAX #attention cette consigne est un effacement
                    effacement_actuel += (simulations_conso[ind][1]-equip.activite)/100.*equip.PROD_MAX
                    conso_future -= simulations_conso[ind][1]-equip.activite/100.*(equip.PROD_MAX) #on retire à conso_future l'effacement
                    print "consofuture : %s" %conso_future
                    print "consigne_conso[ind] : %s" %consigne_conso[ind]
            
    else:
        
        min=sum(i.simulation()[0]/100.*i.PROD_MAX for i in ville.equipProduction) #capacite de production minimale à l'etat suivant

        if min <= conso_future: # si on peut atteindre la valeur de la consommation...
            prod_provisoire = prod_actuelle

            while (abs(prod_provisoire-conso_future) > 0.02*conso_future and prod_provisoire > conso_future): #tant que ecart > 2% et prod > conso
                ind = ind_eqpascher2(simulations,consigne) #indice de l'equipement le moins cher qu'on met au min
                equip = ville.equipProduction[ind]
                
                if (simulations[ind][0] < simulations[ind][1]): #equipement à production laissant marge de maneuvre ex : centrale (et pas PV)
                    while (prod_provisoire > conso_future and abs(consigne[ind]-simulations[ind][0]) >= simulations[ind][0]*0.05):
                        consigne[ind] -= (equip.activite-simulations[ind][0])/10. #on met progressivement la production au min
                        prod_provisoire -= (equip.activite-simulations[ind][0])/100./10.*equip.PROD_MAX #maj
                else:
                    consigne[ind] = simulations[ind][0] #sinon on met à la production min = max (on n'a pas le choix)
                    prod_provisoire -= (equip.activite-simulations[ind][0])/100.*equip.PROD_MAX #maj

        else: #on ne peut pas baisser suffisamment la production
            for i in range (len(simulations)): # on met tout au min
                consigne[i] = simulations[i][0]
            prod_provisoire = sum(simulations[i][0]/100.*ville.equipProduction[i].PROD_MAX for i in range(len(simulations)))

            # il faut maintenant compenser la différence prod-conso avec du stockage
            stock_min = [simulations_stock[i][0] for i in range(len(simulations_stock))] #tous les stockages sont en mode "remplissage maximal"
            while (abs(prod_provisoire-conso_future) > 2./100.*conso_future and prod_provisoire > conso_future and abs(sum(consigne_stock)-sum(stock_min)) >= sum(stock_min)*0.05):
                ind = ind_eqpascher2(simulations_stock,consigne_stock) #stockage le moins cher à remplir
                equip = ville.equipStockage[ind]
                
                while (abs(prod_provisoire-conso_future) > 2./100.*conso_future and prod_provisoire > conso_future and abs(consigne_stock[ind]-stock_min[ind]) >= stock_min[ind]*0.05):
                    consigne_stock[ind] -= (equip.activite - simulations_stock[ind][0])/10.
                    prod_provisoire -= (equip.activite - simulations_stock[ind][0])/100./10.*equip.PROD_MAX
                    
    ecart = conso_future-prod_provisoire # ecart qui sera de l'import/export
    ville.equipProduction[0].effacement = ecart
    ''' print effacement_actuel'''
    '''envoie des consignes et effacements pour la prochaine étape :) '''

    for i in range(len(consigne)):
       
        ville.equipProduction[i].etatSuivant(consigne[i],0.)
    
    for i in range(len(consigne_stock)):
       
        ville.equipStockage[i].etatSuivant(consigne_stock[i],0.)
    
    for i in range(len(consigne_conso)):
        
        ville.equipConso[i].etatSuivant(0.,consigne_conso[i])
    
    Global.db.enregistrerConsigne(consigne, consigne_conso, consigne_stock, numTest)
    Global.db.enregistrerEtape(ville.equipProduction, ville.equipConso, ville.equipStockage, numTest)        
    Global.tempsinc()#temps+=1
    print Global.temps
    

print "ok!"
if(analyseur):
    execfile("analyseur.py")
