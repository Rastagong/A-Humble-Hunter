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
        return ["Test"]

    def _getVariables(self):
        return [("squirrelsTues", 0)]

    def _initialiserEvenements(self):
        self._evenements["concrets"]["Clairiere"] = OrderedDict()
        if NOM_CARTE_LANCEMENT == "Clairiere":
            self._evenements["concrets"]["Clairiere"]["Joueur"] = [ Joueur(self._jeu, self, 21, 39, 2, fichier="Chasseur.png"), (21, 39), "Bas"]
        j, self._positionJoueur = self._jeu.joueur, None
        self._xJoueur, self._yJoueur, self._cJoueur, self._directionJoueur, self._appuiValidationJoueur = j.x/32, j.y/32, j.c, j.direction, j.appuiValidation
        self._evenements["abstraits"]["Divers"] = dict()
        self._evenements["abstraits"]["Divers"]["Narrateur"] = Narrateur(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["ModulateurMusique"] = ModulateurMusique(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["AnimateurToucheAction"] = AnimateurToucheAction(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["LanceurFleches"] = LanceurFleches(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["GestionnaireAnimaux"] = GestionnaireAnimaux(self._jeu, self)

    def chargerEvenements(self, nomCarte):
        if nomCarte == "Clairiere":
            #self._evenements["concrets"]["LD26-Ferme"]["Mere"] = [ Mere(self._jeu, self), (13, 9), "Bas"]
            pass
