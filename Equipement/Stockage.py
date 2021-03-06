# -*-coding:utf-8 -
from Equipement import Equipement
class Stockage(Equipement):

	def __init__(self,nom="Stockage", capacite = 1000., prop = 1./2., cout=2., prod = 200.):
		self.capacite = capacite
		self.reste = self.capacite*prop #pas un pourcentage
		self.cout = cout
		self.PROD_MAX=prod
		self.activite = 0.
		self.EFFA_MAX = capacite    # /!\ on stocke la capacité max dans EFFA_MAX pour l'enregistrer en base de données
		self.effacement = self.reste  # /!\ on stocke la capacité dans EFFA_MAX pour l'enregistrer en base de données
		self.nom = nom

	def etatSuivant(self, consigne=0., effacement=0.):
		self.activite = consigne
                if abs(self.activite) < 10.**(-3):
                    self.activite = 0.
		self.reste = max(0., self.reste - self.activite/100.*self.PROD_MAX/6.) # on retire la puissance dégagée / 6 (10 min = 1h / 6)
		self.effacement = self.reste

	def simulation(self):
		if self.reste > self.PROD_MAX/6.: # si on a assez d'énergie pour débiter à fond...
			prod_max=100.
		else:
			prod_max= self.reste*100./(self.PROD_MAX/6.) 
                        if prod_max < 10.**(-3):
                            prod_max =0.
		if self.reste+self.PROD_MAX/6.>self.capacite:
			prod_min= (self.reste - self.capacite)*100./(self.PROD_MAX/6.)
		else:
			prod_min=-100.
		prix_min = prod_min/100.*self.PROD_MAX*self.cout
		prix_stable = self.activite/100.*self.cout*self.PROD_MAX
		prix_max = prod_max/100.*self.PROD_MAX*self.cout
		return (prod_min,prod_max,prix_min,prix_stable,prix_max)
	
if __name__ == "__main__":
    stockage = Stockage()
    print stockage.capacite
    print stockage.reste
    s = stockage.simulation()
    print s
    stockage.etatSuivant(s[0], 0.)
    print stockage.reste
    s = stockage.simulation()
    print s
    stockage.etatSuivant(s[0], 0.)
    print stockage.reste
    s = stockage.simulation()
    print s
    stockage.etatSuivant(s[0], 0.)
    print stockage.reste
    s = stockage.simulation()
    print s
    stockage.etatSuivant(s[0], 0.)
    print stockage.reste
    s = stockage.simulation()
    print s
    stockage.etatSuivant(s[0], 0.)
    
