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
from listeEvenements import *

class MonGestionnaireEvenements(GestionnaireEvenements):

    def _getInterrupteurs(self):
        return ["MusiqueForet", "finChasse1"]

    def _getVariables(self):
        return [("sceneChasse", 0), ("SquirrelChasses", 0), ("LapinChasses", 0), ("CartesForet", ["Clairiere","CheminClairiere"])]

    def _initialiserEvenements(self):
        self._evenements["concrets"]["Clairiere"] = OrderedDict()
        self._evenements["concrets"]["CheminClairiere"] = OrderedDict()
        self._evenements["concrets"]["Maison"] = OrderedDict()
        self._evenements["concrets"]["InterieurMaison"] = OrderedDict()
        if NOM_CARTE_LANCEMENT == "Clairiere":
            self._evenements["concrets"]["Clairiere"]["Joueur"] = [ Joueur(self._jeu, self, 21, 39, 2, fichier="Chasseur.png"), (21, 39), "Bas"]
        elif NOM_CARTE_LANCEMENT == "CheminClairiere":
            self._evenements["concrets"]["CheminClairiere"]["Joueur"] = [ Joueur(self._jeu, self, 34, 2, 2, fichier="Chasseur.png"), (34, 2), "Gauche"]
        elif NOM_CARTE_LANCEMENT == "Maison":
            self._evenements["concrets"]["Maison"]["Joueur"] = [ Joueur(self._jeu, self, 14, 0, 2, fichier="Chasseur.png"), (14, 0), "Bas"]
        elif NOM_CARTE_LANCEMENT == "InterieurMaison":
            self._evenements["concrets"]["InterieurMaison"]["Joueur"] = [ Joueur(self._jeu, self, 13, 3, 2, fichier="Chasseur.png"), (7, 13), "Haut"]
        j, self._positionJoueur = self._jeu.joueur, None
        self._xJoueur, self._yJoueur, self._cJoueur, self._directionJoueur, self._appuiValidationJoueur = j.x/32, j.y/32, j.c, j.direction, j.appuiValidation
        self._evenements["abstraits"]["Divers"] = OrderedDict()
        self._evenements["abstraits"]["Divers"]["ModulateurMusique"] = ModulateurMusique(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["LanceurMusique"] = LanceurMusique(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["AnimateurToucheAction"] = AnimateurToucheAction(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["LanceurFleches"] = LanceurFleches(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["Narrateur"] = Narrateur(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["GestionnaireAnimaux"] = GestionnaireAnimaux(self._jeu, self)

    def chargerEvenements(self, nomCarte):
        if nomCarte == "Clairiere":
            self._evenements["concrets"]["Clairiere"]["Sortie1"] = [Teleporteur(self._jeu, self, "CheminClairiere", 34, 2, 2, "Gauche", condition="finChasse1"), (0, 47), "Aucune"]
            self._evenements["concrets"]["Clairiere"]["Sortie2"] = [Teleporteur(self._jeu, self, "CheminClairiere", 34, 3, 2, "Gauche", condition="finChasse1"), (0, 48), "Aucune"]
        elif nomCarte == "CheminClairiere":
            self._evenements["concrets"]["CheminClairiere"]["SortieClairiere1"] = [Teleporteur(self._jeu, self, "Clairiere", 0, 47, 2, "Droite"), (34, 2), "Aucune"]
            self._evenements["concrets"]["CheminClairiere"]["SortieClairiere2"] = [Teleporteur(self._jeu, self, "Clairiere", 0, 48, 2, "Droite"), (34, 3), "Aucune"]
            self._evenements["concrets"]["CheminClairiere"]["SortieMaison1"] = [Teleporteur(self._jeu, self, "Maison", 14, 0, 2, "Bas"), (3, 29), "Aucune"]
            self._evenements["concrets"]["CheminClairiere"]["SortieMaison2"] = [Teleporteur(self._jeu, self, "Maison", 15, 0, 2, "Bas"), (4, 29), "Aucune"]
        elif nomCarte == "Maison":
            self._evenements["concrets"]["Maison"]["SortieCheminClairiere1"] = [Teleporteur(self._jeu, self, "CheminClairiere", 3, 29, 2, "Haut"), (14, 0), "Aucune"]
            self._evenements["concrets"]["Maison"]["SortieCheminClairiere2"] = [Teleporteur(self._jeu, self, "CheminClairiere", 4, 29, 2, "Haut"), (15, 0), "Aucune"]
            self._evenements["concrets"]["Maison"]["SortieInterieurMaison"] = [Porte(self._jeu, self, "InterieurMaison", False, "HyptosisMaison.png", (64, 64, 32, 32), (64, 0, 32, 32), 3, 4, 2, 13, 3, 2, "Haut"), (3, 4), "Aucune"]
        elif nomCarte == "InterieurMaison":
            self._evenements["concrets"]["InterieurMaison"]["Sortie"] = [Teleporteur(self._jeu, self, "Maison", 3, 5, 2, "Bas"), (13, 3), "Aucune"]
            self._evenements["concrets"]["InterieurMaison"]["Belia"] = [MembreFamille(Belia(self._jeu, self)), (7,6), "Bas"]
            self._evenements["concrets"]["InterieurMaison"]["Tom"] = [MembreFamille(Enfant(self._jeu, self, "Tom", 4, 10, 2)), (4, 10), "Bas"]
            self._evenements["concrets"]["InterieurMaison"]["Elie"] = [MembreFamille(Enfant(self._jeu, self, "Elie", 4, 13, 2)), (4, 13), "Bas"]
