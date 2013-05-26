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
from narro.evenement import *
from narro.boiteOutils import *
from narro.interrupteur import *
from narro.evenementConcret import *
from narro.pnj import *
from narro.constantes import *
from narro import directions
import os

class LanceurFleches(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._fleches, self._positionSources, self._nombreFlechesTotal = dict(), dict(), 0
        Horloge.initialiser(id(self), "Cooldown", 1)
        self._positionSources["Gauche"] = Rect(0, 0, 42, 11)
        self._positionSources["Droite"] = Rect(0, 11, 42, 11)
        self._positionSources["Haut"] = Rect(0, 21, 42, 42)
        self._positionSources["Bas"] = Rect(0, 63, 42, 42)

    def traiter(self):
        if self._gestionnaire.appuiTir and Horloge.sonner(id(self), "Cooldown"):
            self._nombreFlechesTotal += 1
            nomFleche, direction, sensDirection = "Fleche" + str(self._nombreFlechesTotal), self._boiteOutils.directionJoueurReelle, 1
            positionFleche = self._boiteOutils.positionCarteJoueur.copy()
            self._bougerPositionCarte(positionFleche, direction, 0, initialisation=True)
            self._jeu.carteActuelle.poserPNJ(positionFleche, self._boiteOutils.coucheJoueur-1, self._positionSources[direction], "Arrow.png", (0,0,0), nomFleche)
            tempsActuel = pygame.time.get_ticks()
            self._fleches[nomFleche] = [positionFleche, direction, tempsActuel, VITESSE_DEPLACEMENT_FLECHE]
            self._boiteOutils.jouerSon("Whip", "Whip Action Joueur", volume=VOLUME_MUSIQUE/1.5)
            Horloge.initialiser(id(self), "Cooldown", 300)
        tempsActuel = pygame.time.get_ticks()
        for nomFleche in self._fleches.keys():
            avancee, deltaTimer = self._calculerNouvellesCoordonnees(tempsActuel, self._fleches[nomFleche][2], self._fleches[nomFleche][3])
            if avancee >= 1.0:
                self._fleches[nomFleche][2], direction = tempsActuel, self._fleches[nomFleche][1]
                self._bougerPositionCarte(self._fleches[nomFleche][0], direction, avancee)
                positionFleche = self._fleches[nomFleche][0]
                self._jeu.carteActuelle.poserPNJ(positionFleche, self._boiteOutils.coucheJoueur-1, self._positionSources[direction], "Arrow.png", (0,0,0), nomFleche)

    def _calculerNouvellesCoordonnees(self, tempsActuel, tempsPrecedent, vitesseDeplacement):
        deltaTimer = (tempsActuel - tempsPrecedent) / 1000
        avancee = (vitesseDeplacement * deltaTimer)
        return (avancee, deltaTimer)

    def _bougerPositionCarte(self, positionFleche, direction, avancee, initialisation=False):
        if initialisation and (direction == "Gauche" or direction == "Droite"):
            avancee = self._positionSources["Gauche"].width
        if initialisation and (direction == "Haut" or direction == "Bas"):
            avancee = self._positionSources["Gauche"].height
        sensDirection = 1
        if direction == "Gauche" or direction == "Haut":
            sensDirection = -1
        if direction == "Gauche" or direction == "Droite":
            positionFleche.move_ip(sensDirection * self._positionSources["Gauche"].width, 0)
        elif direction == "Haut" or direction == "Bas":
            positionFleche.move_ip(0, sensDirection * self._positionSources["Haut"].height)

class Narrateur(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._penseePossible, self._etape, self._coefNoircisseur = InterrupteurInverse(self._boiteOutils.penseeAGerer), 0, 0
        self._debut = False
    
    def traiter(self):
        x, y = self._gestionnaire.xJoueur, self._gestionnaire._yJoueur
        if self._boiteOutils.nomCarte == "Clairiere":
            if self._etape == 0:
                self._coordonneesJoueur = self._boiteOutils.getCoordonneesJoueur()
                self._boiteOutils.jouerSon("sonsForet", "boucleSonsForet", nombreEcoutes=0)
                self._boiteOutils.ajouterTransformation(True, "Alpha", alpha=self._coefNoircisseur)
                Horloge.initialiser(id(self), "Alpha", 100)
                self._etape += 1
            if self._etape == 1 and Horloge.sonner(id(self), "Alpha"):
                self._coefNoircisseur += 7
                if self._coefNoircisseur > 255:
                    self._coefNoircisseur = 255
                self._boiteOutils.ajouterTransformation(True, "Alpha", alpha=self._coefNoircisseur)
                if self._coefNoircisseur == 255:
                    self._boiteOutils.retirerTransformation(True, "Alpha")
                    self._coordonneesJoueur = self._boiteOutils.getCoordonneesJoueur()
                    Horloge.initialiser(id(self), "tempsDecouverte", 20000)
                    self._etape += 1
                else:
                    Horloge.initialiser(id(self), "Alpha", 100)
            if self._etape == 2 and (Horloge.sonner(id(self), "tempsDecouverte") is True or self._boiteOutils.deplacementConsequentJoueur(self._coordonneesJoueur, 10) is True):
                self._boiteOutils.ajouterPensee("Test de la police")
                self._etape += 1
