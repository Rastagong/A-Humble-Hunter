# -*-coding:utf-8 -*
#    A Humble Hunter, a short interactive story written by @Rastagong (http://rastagong.net)
#    Copyright (C) 2013 Rastagong
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


try: #If needed, the _path module must add the path to the Narro directory to sys.path so that the Narro Engine can be imported as a package
    import _path
except:
    pass
from constantes import *
from narro.gestionnairevenements import *
from narro.constantes import *
import listeEvenements
from listeEvenements import *

class MonGestionnaireEvenements(GestionnaireEvenements):

    def _getInterrupteurs(self):
        a = ["DecouverteSquirrels", "MusiqueForet", "Rires", "finChasse1", "JoueurEntre", "JoueurEntre2", "JoueurEntre3", "squirrelPose", "BeliaSortie","discussionEtang"]
        b = ["BeliaRentree", "TomEtage", "ElieEtage", "ConversationEnfants", "TomHungry", "nutsOnTable", "escalierLibre", "fogRises", "JoueurVuWizards", "Wizards disappear"]
        c = ["RetourDuckGod", "RetourMaisonDream","DébutConversation", "JoueurSonneMaisonGods", "MusiqueThe"]
        return a + b + c

    def _getVariables(self):
        return [("sceneChasse", 0), ("SquirrelChasses", 0), ("LapinChasses", 0), ("CartesForet", ["Clairiere","CheminClairiere"]), ("NombreGlands", 0)]

    def _initialiserEvenements(self):
        self._evenements["concrets"]["Clairiere"] = OrderedDict()
        self._evenements["concrets"]["CheminClairiere"] = OrderedDict()
        self._evenements["concrets"]["Maison"] = OrderedDict()
        self._evenements["concrets"]["InterieurMaison"] = OrderedDict()
        self._evenements["concrets"]["EtageMaison"] = OrderedDict()
        self._evenements["concrets"]["Maison Dream"] = OrderedDict()
        self._evenements["concrets"]["Entree Maison Gods"] = OrderedDict()
        self._evenements["concrets"]["Maison Gods"] = OrderedDict()
        if NOM_CARTE_LANCEMENT == "Clairiere":
            self._evenements["concrets"]["Clairiere"]["Joueur"] = [ Joueur(self._jeu, self, 21, 39, 2, fichier="Chasseur.png"), (21, 39), "Bas", 2]
        elif NOM_CARTE_LANCEMENT == "CheminClairiere":
            self._evenements["concrets"]["CheminClairiere"]["Joueur"] = [ Joueur(self._jeu, self, 34, 2, 2, fichier="Chasseur.png"), (34, 2), "Gauche", 2]
        elif NOM_CARTE_LANCEMENT == "Maison":
            self._evenements["concrets"]["Maison"]["Joueur"] = [ Joueur(self._jeu, self, 14, 0, 2, fichier="Chasseur.png"), (14, 0), "Bas", 2]
        elif NOM_CARTE_LANCEMENT == "InterieurMaison":
            self._evenements["concrets"]["InterieurMaison"]["Joueur"] = [ Joueur(self._jeu, self, 1, 4, 2, fichier="Chasseur.png"), (7, 13), "Haut", 2]
        elif NOM_CARTE_LANCEMENT == "EtageMaison":
            self._evenements["concrets"]["EtageMaison"]["Joueur"] = [Joueur(self._jeu, self, 3, 5, 2, fichier="Chasseur.png"), (3,5), "Bas", 2]
        elif NOM_CARTE_LANCEMENT == "Maison Dream":
            #self._evenements["concrets"]["Maison Dream"]["Joueur"] = [ Joueur(self._jeu, self, 10, 18, 2, fichier="Chasseur.png"), (5,6), "Bas", 2]
            self._evenements["concrets"]["Maison Dream"]["Joueur"] = [ Joueur(self._jeu, self, 169, 37, 2, fichier="Chasseur.png"), (5,6), "Bas", 2]
            self._evenements["concrets"]["Maison Dream"]["DuckGod"] = [DuckGod(self._jeu, self, 63, 6, 2, "Bas"), (3, 5), "Bas"] #Starting point instruction
        elif NOM_CARTE_LANCEMENT == "Entree Maison Gods":
            self._evenements["concrets"]["Entree Maison Gods"]["Joueur"] = [ Joueur(self._jeu, self, 9, 9, 2, fichier="Chasseur.png"), (9,9), "Haut", 2 ]
            self._evenements["concrets"]["Entree Maison Gods"]["DuckGod"] = [DuckGod(self._jeu, self, 9, 5, 2, "Droite"), (9, 5), "Bas"] #Starting point instruction
        j, self._positionJoueur = self._jeu.joueur, None
        self.registerPositionInitialeJoueur(NOM_CARTE_LANCEMENT)
        self._evenements["abstraits"]["Divers"] = OrderedDict()
        self._evenements["abstraits"]["Divers"]["ModulateurMusique"] = ModulateurMusique(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["LanceurMusique"] = LanceurMusique(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["AnimateurToucheAction"] = AnimateurToucheAction(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["LanceurFleches"] = LanceurFleches(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["Narrateur"] = Narrateur(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["GestionnaireAnimaux"] = GestionnaireAnimaux(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["SignaleurJoueur"] = SignaleurJoueur(self._jeu, self)
        #self._evenements["abstraits"]["Divers"]["BruiteurPasJoueur"] = BruiteurPasJoueur(self._jeu, self)

    def chargerEvenements(self, nomCarte):
        if nomCarte == "Clairiere" and nomCarte not in self._cartesChargees:
            self._evenements["concrets"]["Clairiere"]["Sortie1"] = [Teleporteur(self._jeu, self, "CheminClairiere", 34, 2, 2, "Gauche", condition="finChasse1"), (0, 47), "Aucune"]
            self._evenements["concrets"]["Clairiere"]["Sortie2"] = [Teleporteur(self._jeu, self, "CheminClairiere", 34, 3, 2, "Gauche", condition="finChasse1"), (0, 48), "Aucune"]
        elif nomCarte == "CheminClairiere"  and nomCarte not in self._cartesChargees:
            self._evenements["concrets"]["CheminClairiere"]["SortieClairiere1"] = [Teleporteur(self._jeu, self, "Clairiere", 0, 47, 2, "Droite"), (34, 2), "Aucune"]
            self._evenements["concrets"]["CheminClairiere"]["SortieClairiere2"] = [Teleporteur(self._jeu, self, "Clairiere", 0, 48, 2, "Droite"), (34, 3), "Aucune"]
            self._evenements["concrets"]["CheminClairiere"]["SortieMaison1"] = [Teleporteur(self._jeu, self, "Maison", 14, 0, 2, "Bas"), (3, 29), "Aucune"]
            self._evenements["concrets"]["CheminClairiere"]["SortieMaison2"] = [Teleporteur(self._jeu, self, "Maison", 15, 0, 2, "Bas"), (4, 29), "Aucune"]
        elif nomCarte == "Maison"  and nomCarte not in self._cartesChargees:
            self._evenements["concrets"]["Maison"]["SortieCheminClairiere1"] = [Teleporteur(self._jeu, self, "CheminClairiere", 3, 29, 2, "Haut"), (14, 0), "Aucune"]
            self._evenements["concrets"]["Maison"]["SortieCheminClairiere2"] = [Teleporteur(self._jeu, self, "CheminClairiere", 4, 29, 2, "Haut"), (15, 0), "Aucune"]
            self._evenements["concrets"]["Maison"]["SortieInterieurMaison"] = [Porte(self._jeu, self, "InterieurMaison", False, "HyptosisMaison.png", (64, 64, 32, 32), (64, 0, 32, 32), 3, 4, 2, 13, 3, 2, "Haut"), (3, 4), "Aucune"]
        elif nomCarte == "InterieurMaison"  and nomCarte not in self._cartesChargees:
            self._evenements["concrets"]["InterieurMaison"]["SortieExterieur"] = [Teleporteur(self._jeu, self, "Maison", 3, 5, 2, "Bas"), (13, 3), "Aucune"]
            self._evenements["concrets"]["InterieurMaison"]["SortieEtage"] = [Teleporteur(self._jeu, self, "EtageMaison", 1, 3, 2, "Bas"), (1, 3), "Aucune"]
            self._evenements["concrets"]["InterieurMaison"]["Belia"] = [MembreFamille(Belia(self._jeu, self)), (7,6), "Bas"]
            self._evenements["concrets"]["InterieurMaison"]["Tom"] = [MembreFamille(Enfant(self._jeu, self, "Tom", 1, 4, 2)), (1, 4), "Bas"]
            self._evenements["concrets"]["InterieurMaison"]["Elie"] = [MembreFamille(Enfant(self._jeu, self, "Elie", 1, 8, 2)), (1, 8), "Bas"]
            self._evenements["concrets"]["InterieurMaison"]["TableSquirrel"] = [TableSquirrel(self._jeu, self), (5, 5), "Aucune"]
            self._evenements["concrets"]["InterieurMaison"]["TableNuts"] = [TableNuts(self._jeu, self, 7, 12), (7, 12), "Aucune"]
            self._evenements["concrets"]["InterieurMaison"]["TableNuts2"] = [TableNuts(self._jeu, self, 7, 13), (7, 13), "Aucune"]
        elif nomCarte == "EtageMaison" and nomCarte not in self._cartesChargees:
            self._evenements["concrets"]["EtageMaison"]["Sortie"] = [Teleporteur(self._jeu, self, "InterieurMaison", 1, 3, 2, "Bas", condition="escalierLibre"), (1,3), "Aucune" ]
        elif nomCarte == "Maison Dream" and nomCarte not in self._cartesChargees:
            self._evenements["concrets"]["Maison Dream"]["Feu"] = [Feu(self._jeu, self, 169, 34, 3), (169, 34), "Bas"]
            self._evenements["concrets"]["Maison Dream"]["VersMaisonGods"] = [Teleporteur(self._jeu, self, "Entree Maison Gods", 9, 9, 2, fonctionApres=annulerFog), (285,21), "Aucune"]
            self._evenements["concrets"]["Maison Dream"]["RetourMaisonDream"] = [RetourMaisonDream(self._jeu, self), (285,22), "Aucune"]
            i, listeWizards = 0, [(167,29,"Bas"),(168,29,"Bas"),(169,29,"Bas"),(170,29,"Bas"),(171,29,"Bas"),(167,30,"Bas"),(167,31,"Bas"),(171,30,"Bas"),(171,31,"Bas"),(167,32,"Bas"),(168,32,"Bas"),(169,32,"Bas"),(170,32,"Bas"),(171,32,"Bas"),(173,34,"Gauche"),(168,38,"Haut"),(169,38,"Haut"),(170,38,"Haut"),(165,34,"Droite")]
            while i < len(listeWizards):
                nom, x, y, directionDepart = "WizardForest"+str(i), listeWizards[i][0], listeWizards[i][1], listeWizards[i][2]
                self._evenements["concrets"]["Maison Dream"][nom] = [WizardForest(self._jeu, self, x, y, 2, directionDepart, nom), (x,y), directionDepart]
                i += 1
        elif nomCarte == "Entree Maison Gods" and nomCarte not in self._cartesChargees:
            self._evenements["concrets"]["Entree Maison Gods"]["VersDream"] =  [Teleporteur(self._jeu, self, "Maison Dream", 285, 22, 2, fonctionApres=retourMaisonDream), (9,9), "Aucune"]
            self._evenements["concrets"]["Entree Maison Gods"]["Trou"] =  [Teleporteur(self._jeu, self, "Maison Gods", 3, 4, 2, fonctionApres=sautMaisonGods, joueurBloque=True), (3,5), "Aucune"]
        elif nomCarte == "Maison Gods" and nomCarte not in self._cartesChargees:
            self._evenements["concrets"]["Maison Gods"]["DuckGod"] = [God(self._jeu, self, 69, 42, 2, "Droite", "DuckGod", "DuckGod.png"), (69,42), "Droite"]
            self._evenements["concrets"]["Maison Gods"]["CrowGod"] = [God(self._jeu, self, 73, 42, 2, "Gauche", "CrowGod", "Crow.png"), (73,42), "Gauche"]
            self._evenements["concrets"]["Maison Gods"]["WizardGod"] = [God(self._jeu, self, 77, 36, 2, "Gauche", "WizardGod", "WizardGod.png"), (77,36), "Haut"]
            self._evenements["concrets"]["Maison Gods"]["Bruiteur"] = [Bruiteur(self._jeu, self), (0,0), "Aucune"]
            self._evenements["concrets"]["Maison Gods"]["Panneau"] = [Panneau(self._jeu, self, "It reads: ring the skull bell", "Haut", splashTexte=True, tailleTexte=24), (64,38), "Aucune"]
            self._evenements["concrets"]["Maison Gods"]["SkullRing"] = [SkullRing(self._jeu, self), (61,39), "Aucune"]
        if nomCarte not in self._cartesChargees:
            self._cartesChargees.append(nomCarte)

    def _recharger(self):
        pass
