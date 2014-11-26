# -*-coding:utf-8 -

'''    Fonctionnement :

- une batterie débite un courant donnée par activité*PROD_MAX tout comme les autres équipements
NB : si ce courant est négatif c'est que la batterie est en train de stocker
- pour demander à une batterie de produire de l'énergie envoyez lui une consigne positive en %,
si c'est possible la puissance débitée sera de consigne/100 * PROD_MAX
- pour lui demander de stocker vous lui donnez une consigne NEGATIVE (toujours en %)
si c'est possible elle stockera gentiment une puissance de abs(consigne)/100 * PROD_MAX

        Les impossibilités rencontrées par les batteries sont :

- la surtension (dégradation de la batterie = très cher)
- la sous tension extensive (destruction de la batterie, rendu impossible par le modèle)
- le manque de capacité pour stocker/le manque de stock à déstocker'''

#chocolatine

class ParcBatterieLithiumion:
    
    def __init__(self, nom="un petit parc", nombre = 10, prop = 1/2, activite=0):
        self.nom=nom
        '''nombre de batterie dans le parc'''
        self.nombre = nombre
        '''capacité en kWh'''
        self.capacite = 6.5*self.nombre
        '''énergie stockée dans le parc en kWh'''
        self.reste = self.capacite*prop #pas un pourcentage
        '''production maximale en kW'''
        self.PROD_MAX = 23
        self.COUT_MAX = 0.8
        '''production normale en kW'''
        self.PROD_NOR = 20
        self.COUT_NOR = 0.2
        '''production minimale en kW'''
        self.PROD_MIN = 17
        self.COUT_MIN = 0.2
        '''Les prix sont en €/kWh'''
        
        self.activite = activite
        '''les compteurs permet d'éviter une trop longue mise en surtension. Au bout
        de 2 pas la batterie se voit obliger d'arrêter le plein régime pour 8 pas de repos'''
        self.compteur_surtension = 0
        self.compteur_pause = 0
        
    def etat_suivant(self, consigne=0.): #consigne*prod = puissance envoyée de la batterie vers les clients
        self.activite = prevision(consigne)[0]
        self.reste += self.activite*self.PROD_MAX/6
        
    def prevision(self,consigne=0.):
        puissance = self.reste - consigne/100*self.capacite
        prix = self.cout*abs(puissance)
        return (puissance/self.capacite*100, prix)
    
    def simulation_destockage(self):
    
        if self.compteur_surtension == 2 or self.compteur_pause <= 8:
            '''cas où la batterie commence ou continue une pause due à une surtension'''
            prod_min=0
            prod_max=0
            prix_min=0
            prix_max=0
            prix_normal=0
            
        elif self.reste>=self.PROD_MAX*self.nombre/6:
            '''cas idéal où il reste assez pour décharger à volonté'''
            prix_min = self.COUT_MIN*self.PROD_MIN/6
            prod_min = self.PROD_MIN/self.PROD_MAX
            prix_max = self.COUT_MAX*self.PROD_MAX*self.nombre/6
            prod_max = self.nombre
            if abs(self.activite)*self.PROD_MAX > self.PROD_NOR:
                prix_normal = 10000*(1-1/self.activite)/1700 + self.COUT_NOR
            else:
                prix_normal = self.COUT_NOR*self.activite*self.PROD_MAX/6

        else:
            '''cas où il faut prendre en compte le reste'''
            prix_min = self.COUT_MIN*self.PROD_MIN/6
            prod_min = self.PROD_MIN/self.PROD_MAX
            activite_maximum = self.reste/(self.PROD_MAX/6)
            if activite_maximum > abs(self.activite):
                prod_max = self.nombre*activite_maximum
                if activite_maximum*self.PROD_MAX > self.PROD_NOR:
                    prix_max = 10000*(1-1/activite_maximum)/1700 + self.COUT_NOR
                else:
                    prix_max = self.COUT_NOR*activite_maximum*self.PROD_MAX/6
                if abs(self.activite)*self.PROD_MAX > self.PROD_NOR:
                    prix_normal = 10000*(1-1/abs(self.activite))/1700 + self.COUT_NOR
                else:
                    prix_normal = self.COUT_NOR*abs(self.activite)*self.PROD_MAX/6
            else:
                prod_max = self.nombre*activite_maximum
                if activite_maximum*self.PROD_MAX > self.PROD_NOR:
                    prix_max = 10000*(1-1/activite_maximum)/1700 + self.COUT_NOR
                    prix_normal = prix_max
                else:
                    prix_max = self.COUT_NOR*activite_maximum*self.PROD_MAX/6
                    prix_normal = prix_max
        return (prod_min,prod_max, prix_min, prix_normal, prix_max)
    
    def simulation_stockage(self):
    
        if self.compteur_surtension == 2 or self.compteur_pause <= 8:
            '''cas où la batterie commence ou continue une pause due à une surtension'''
            prod_min=0
            prod_max=0
            prix_min=0
            prix_max=0
            prix_normal=0
            
        elif self.capacite-self.reste>=self.PROD_MAX*self.nombre/6:
            '''cas idéal où il reste assez pour charger à volonté'''
            prix_min = self.COUT_MIN*self.PROD_MIN/6
            prod_min = self.PROD_MIN/self.PROD_MAX
            prix_max = self.COUT_MAX*self.PROD_MAX*self.nombre/6
            prod_max = self.nombre
            if abs(self.activite)*self.PROD_MAX > self.PROD_NOR:
                prix_normal = 10000*(1-1/self.activite)/1700 + self.COUT_NOR
            else:
                prix_normal = self.COUT_NOR*self.activite*self.PROD_MAX/6

        else:
            '''cas où il faut prendre en compte le reste'''
            prix_min = self.COUT_MIN*self.PROD_MIN/6
            prod_min = self.PROD_MIN/self.PROD_MAX
            activite_maximum = (self.capacite-self.reste)/(self.PROD_MAX/6)
            if activite_maximum > abs(self.activite):
                prod_max = self.nombre*activite_maximum
                if activite_maximum*self.PROD_MAX > self.PROD_NOR:
                    prix_max = 10000*(1-1/activite_maximum)/1700 + self.COUT_NOR
                else:
                    prix_max = self.COUT_NOR*activite_maximum*self.PROD_MAX/6
                if abs(self.activite)*self.PROD_MAX > self.PROD_NOR:
                    prix_normal = 10000*(1-1/abs(self.activite))/1700 + self.COUT_NOR
                else:
                    prix_normal = self.COUT_NOR*abs(self.activite)*self.PROD_MAX/6
            else:
                prod_max = self.nombre*activite_maximum
                if activite_maximum*self.PROD_MAX > self.PROD_NOR:
                    prix_max = 10000*(1-1/activite_maximum)/1700 + self.COUT_NOR
                    prix_normal = prix_max
                else:
                    prix_max = self.COUT_NOR*activite_maximum*self.PROD_MAX/6
                    prix_normal = prix_max
        return (-prod_min, -prod_max, prix_min, prix_normal, prix_max)    
    
    def contraintes(self,consigne):
        '''si la puissance demandée (à produire comme à stocker) est 
        - supérieure à celle possible à fournir par tout le parc
        - inférieure à la minimale pour une seule batterie
        ça ne marche pas'''
        if abs(consigne) > self.nombre or abs(consigne) < self.PROD_MIN/self.PROD_MAX:
            return False
        else:
            '''s'il n'y a plus assez d'énergie dans le parc on ne peut pas produire '''
            if consigne > 0 and consigne*self.PROD_MAX > self.reste:
                return False
            '''s'il ne reste pas assez de place dans les batteries pour stocker ça ne fonctionnera pas non plus'''
            if consigne < 0 and consigne*self.PROD_MAX < self.capacite - self.reste:
                return False
            else:
                return True

'''vous êtes arrivé au bout félicitations !'''

    #pour les tests
if __name__=='__main__':
    a = ParcBatterieLithiumion()
    print(a.simulation_stockage())