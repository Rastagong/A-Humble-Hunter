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
import os, random

class LanceurFleches(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._fleches, self._positionSources, self._nombreFlechesTotal = dict(), dict(), 0
        Horloge.initialiser(id(self), "Cooldown", 1)
        self._positionSources["Gauche"] = Rect(0, 0, 42, 11)
        self._positionSources["Droite"] = Rect(0, 11, 42, 11)
        self._positionSources["Haut"] = Rect(13, 21, 13, 42)
        self._positionSources["Bas"] = Rect(13, 63, 13, 42)

    def traiter(self):
        tempsActuel = pygame.time.get_ticks()
        if self._gestionnaire.appuiTir and Horloge.sonner(id(self), "Cooldown", arretApresSonnerie=False):
            self._nombreFlechesTotal += 1
            nomFleche, direction, sensDirection = "Fleche" + str(self._nombreFlechesTotal), self._boiteOutils.directionJoueurReelle, 1
            positionFleche = self._boiteOutils.positionCarteJoueur.copy()
            positionCollision, positionVisible = Rect(0, 0, 0, 0), Rect(0, 0, 0, 0)
            if "Gauche" in direction or "Droite" in direction:
                positionCollision.width, positionCollision.height, positionCollision.left, positionCollision.top = 32, 32, 0, 0 
            elif "Haut" in direction or "Bas" in direction:
                positionCollision.width, positionCollision.height, positionCollision.left, positionCollision.top = 32, 42, 0, 0 
            if "Gauche" in direction or "Droite" in direction:
                positionVisible.top = 12
            elif "Haut" in direction or "Bas" in direction:
                positionVisible.left = 10
            self._bougerPositionCarte(positionFleche, direction, 0, initialisation=True, positionCollision=positionCollision)
            if self._jeu.carteActuelle.deplacementPossible(positionFleche, self._boiteOutils.coucheJoueur, nomFleche, positionCollision=positionCollision, positionVisible=positionVisible, verifPrecise=True, ecranVisible=True, exclusionCollision=["Joueur"], collisionEffective=True):
                self._fleches[nomFleche] = [positionFleche, direction, tempsActuel, VITESSE_DEPLACEMENT_FLECHE, positionCollision, positionVisible]
                self._jeu.carteActuelle.poserPNJ(positionFleche, self._boiteOutils.coucheJoueur, self._positionSources[direction], "Arrow.png", (0,0,0), nomFleche, positionCollision=positionCollision, positionVisible=positionVisible)
                self._boiteOutils.jouerSon("Whip", "Whip Action Joueur", volume=VOLUME_MUSIQUE/1.5)
                Horloge.arreterSonnerie(id(self), "Cooldown")
                Horloge.initialiser(id(self), "Cooldown", 300)
        flechesASupprimer = []
        for nomFleche in self._fleches.keys():
            avancee, deltaTimer = self._calculerNouvellesCoordonnees(tempsActuel, self._fleches[nomFleche][2], self._fleches[nomFleche][3])
            if avancee >= 1.0:
                self._fleches[nomFleche][2], direction = tempsActuel, self._fleches[nomFleche][1]
                self._bougerPositionCarte(self._fleches[nomFleche][0], direction, avancee)
                positionFleche, positionCollision, positionVisible = self._fleches[nomFleche][0], self._fleches[nomFleche][4], self._fleches[nomFleche][5]
                carte = self._jeu.carteActuelle
                if carte.deplacementPossible(positionFleche, self._boiteOutils.coucheJoueur, nomFleche, positionCollision=positionCollision, positionVisible=positionVisible, verifPrecise=True, ecranVisible=True, exclusionCollision=["Joueur"], collisionEffective=True):
                    self._jeu.carteActuelle.poserPNJ(positionFleche, self._boiteOutils.coucheJoueur, self._positionSources[direction], "Arrow.png", (0,0,0), nomFleche)
                else:
                    print(nomFleche,"collid")
                    self._jeu.carteActuelle.supprimerPNJ(nomFleche, self._boiteOutils.coucheJoueur)
                    flechesASupprimer.append(nomFleche)
        for nomFleche in flechesASupprimer:
            self._fleches.pop(nomFleche)
        del flechesASupprimer[:]

    def _calculerNouvellesCoordonnees(self, tempsActuel, tempsPrecedent, vitesseDeplacement):
        deltaTimer = (tempsActuel - tempsPrecedent) / 1000
        avancee = (vitesseDeplacement * deltaTimer)
        return (avancee, deltaTimer)

    def _bougerPositionCarte(self, positionFleche, direction, avancee, initialisation=False, positionCollision=False):
        if initialisation and ("Gauche" in direction or "Droite" in direction):
            avancee = 0
        elif initialisation and ("Haut" in direction or "Bas" in direction):
            avancee = 0
        sensDirection = 1
        if direction == "Gauche" or direction == "Haut":
            sensDirection = -1
        if direction == "Gauche" or direction == "Droite":
            positionFleche.move_ip(sensDirection * avancee, 0)
        elif direction == "Haut" or direction == "Bas":
            positionFleche.move_ip(0, sensDirection * avancee)

class Narrateur(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._penseePossible, self._etape, self._coefNoircisseur, self._alpha = InterrupteurInverse(self._boiteOutils.penseeAGerer), 0, 0, 255
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
                self._boiteOutils.ajouterTransformation(True, "SplashText Arrow", texte="Press X to shoot an arrow", antialias=True, couleurTexte=(255,255,255), position=(10, 10), taille=30, alpha=self._alpha)
                Horloge.initialiser(id(self), "Alpha transition", 100)
                self._etape += 1

class GestionnaireAnimaux(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._etape = 0
        self._nombreSquirrels, self._nombreSquirrelsMinimal = 10, 6
        self._nombreSquirrelsTotal = self._nombreSquirrels

    def traiter(self):
        if self._etape == 0:
            x, y, positionsArbres = 0, 0, []
            while x < self._jeu.carteActuelle.longueur:
                y = 0
                while y < self._jeu.carteActuelle.largeur:
                    tile = self._jeu.carteActuelle.tiles[x][y].bloc[2]
                    if not tile.vide:
                        if tile.nomTileset == "base_out_atlas.png" and tile.positionSource == (832, 672, 32, 32):
                            positionsArbres.append((x,y))
                    y += 1
                x += 1
            position, x, y, longueur, largeur = -1, -1, -1, self._jeu.carteActuelle.longueur, self._jeu.carteActuelle.largeur
            i, positionsDepart, self._c = 1, [], 2
            i = 1
            while i <= self._nombreSquirrels:
                while position in positionsDepart or (x,y) == (-1,-1) or self._jeu.carteActuelle.tilePraticable(x,y,self._c) is False or len([positionActuelle for positionActuelle in positionsDepart if self._boiteOutils.tileProcheDe(position, positionActuelle, 10) is True]) > 0:
                    position = (random.randint(0, self._jeu.carteActuelle.longueur), random.randint(0, self._jeu.carteActuelle.largeur))
                    x,y = position[0], position[1]
                positionsDepart.append(position)
                objetSquirrel = Squirrel(self._jeu, self._gestionnaire, x, y, self._c, i, positionsArbres, self)
                self._gestionnaire.evenements["concrets"][self._jeu.carteActuelle.nom]["Squirrel"+str(i)] = [objetSquirrel, (x,y), "Bas"]
                print("Parmi les squirrels d'origine, il y a Squirrel{0}".format(i))
                i += 1
            self._positionsArbres = positionsArbres
            self._etape += 1
        if self._etape == 1:
            if self._nombreSquirrels < self._nombreSquirrelsMinimal:
                self._nombreSquirrelsTotal += 1
                self._nombreSquirrels += 1
                positionCarte, nomSquirrel = Rect(0, 0, 32, 32), "Squirrel"+str(self._nombreSquirrelsTotal)
                while (positionCarte.left,positionCarte.top) == (0,0) or self._jeu.carteActuelle.deplacementPossible(positionCarte, self._c, nomSquirrel) is False or self._jeu.carteActuelle._ecranVisible.contains(positionCarte) is True:
                    positionCarte.left, positionCarte.top = random.randint(0, self._jeu.carteActuelle.longueur*32), random.randint(0, self._jeu.carteActuelle.largeur*32)
                objetSquirrel = Squirrel(self._jeu, self._gestionnaire, positionCarte.left/32, positionCarte.top/32, self._c, self._nombreSquirrelsTotal, self._positionsArbres, self)
                self._gestionnaire.evenements["concrets"][self._jeu.carteActuelle.nom][nomSquirrel] = [objetSquirrel, (positionCarte.left/32, positionCarte.top/32), "Bas"]
                print("Plus assez de squirrels, on ajoute {0}".format(nomSquirrel))

    def onMortAnimal(self, nom):
        if "Squirrel" in nom:
            self._nombreSquirrels -= 1
            print("{0} est mort".format(nom))

class Squirrel(PNJ):
    def __init__(self, jeu, gestionnaire, x, y, c, numero, positionsArbres, gestionnaireAnimaux):
        fichier, couleurTransparente, persoCharset, vitesseDeplacement = "SquirrelMoving.png", (0,0,0), (0,0), 150
        repetitionActions, directionDepart, listeActions = False, "Bas", []
        super().__init__(jeu, gestionnaire, "Squirrel"+str(numero), x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement, fuyard=True, dureeAnimationSP=160)
        self._penseePossible, self._surPlace = InterrupteurInverse(self._boiteOutils.penseeAGerer), False
        self._nomTilesetMouvement, self._nomTilesetSurPlace, self._vie, self._fuite, self._positionsArbres = fichier, "SquirrelEating.png", 3, False, positionsArbres
        self._xArrivee, self._yArrivee, self._vulnerable, self._monteeArbre, self._gestionnaireAnimaux = -1, -1, True, False, gestionnaireAnimaux
        Horloge.initialiser(id(self), "Rouge clignotant", 1)

    def _gererEtape(self):
        if self._fuite is False and self._deplacementBoucle is False:
            self._genererLancerTrajetAleatoire(4, 8)
        elif self._fuite:
            if self._etapeTraitement == 1 and Horloge.sonner(id(self), "Rouge clignotant"):
                self._boiteOutils.ajouterTransformation(False, "Rouge/"+self._nom, nom=self._nom)
                Horloge.initialiser(id(self), "Rouge clignotant", 200)
                self._etapeTraitement += 1
            if self._etapeTraitement == 2 and Horloge.sonner(id(self), "Rouge clignotant"):
                self._boiteOutils.retirerTransformation(False, "Rouge/"+self._nom)
                if Horloge.sonner(id(self), "Fin clignotant"):
                    self._etapeTraitement += 1
                else:
                    Horloge.initialiser(id(self), "Rouge clignotant", 200)
                    self._etapeTraitement -= 1
            if self._deplacementBoucle is False and self._xTile == self._xArrivee and self._yTile == self._yArrivee:
                self._vulnerable = False
                self._lancerTrajet("Haut","Haut",False, deplacementLibre=True)
                self._boiteOutils.retirerTransformation(False, "Rouge/"+self._nom)
                self._monteeArbre = True
        if self._monteeArbre:
            if self._deplacementBoucle is False:
                self._boiteOutils.supprimerPNJ(self._nom, self._c)
                self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, self._nom)
                self._gestionnaireAnimaux.onMortAnimal(self._nom)

    def onCollision(self, nomPNJ, positionCarte):
        super().onCollision(nomPNJ, positionCarte)
        if "Fleche" in nomPNJ and self._vulnerable:
            self._vie -= 1
            print(self._nom, self._vie + 1, self._vie)
            self._etapeTraitement = 1
            Horloge.initialiser(id(self), "Fin clignotant", 2000)
            Horloge.initialiser(id(self), "Rouge clignotant", 1)
            if not self._fuite:
                self._positionsArbres = sorted(self._positionsArbres, key=lambda position: self._boiteOutils.estimationDistanceRestante((self._xTile, self._yTile), position))
                i, positionIdealeTrouvee = 0, False
                while i < len(self._positionsArbres) and not positionIdealeTrouvee:
                    positionJoueur = (self._gestionnaire.xJoueur, self._gestionnaire.yJoueur)
                    distanceArbreJoueur = self._boiteOutils.estimationDistanceRestante(positionJoueur, self._positionsArbres[i])
                    distanceArbreSquirrel = self._boiteOutils.estimationDistanceRestante((self._xTile, self._yTile), self._positionsArbres[i])
                    if self._boiteOutils.tileProcheDe(self._positionsArbres[i], positionJoueur, 3) is False and distanceArbreSquirrel <= distanceArbreJoueur:
                        self._finirDeplacementSP()
                        self._xArrivee, self._yArrivee = self._positionsArbres[i]
                        self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._positionsArbres[i][0], self._positionsArbres[i][1])
                        positionIdealeTrouvee = True
                    i += 1
                self._fuite = True
        if self._vie == 0:
            self._boiteOutils.retirerTransformation(False, "Rouge/"+self._nom)
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, self._nom)
            self._gestionnaireAnimaux.onMortAnimal(self._nom)

    def _genererLancerTrajetAleatoire(self, longueurMin, longueurMax):
        self._longueurMin, self._longueurMax, i, actions = longueurMin, longueurMax, 0, []
        longueurTrajet, direction1, direction2 = random.randint(longueurMin, longueurMax), self._boiteOutils.getDirectionAuHasard(), self._boiteOutils.getDirectionAuHasard()
        while direction2 == directions.directionContraire(direction1):
            direction2 = self._boiteOutils.getDirectionAuHasard()
        seuilDirection = int(longueurTrajet/2)
        while i < longueurTrajet:
            if i < seuilDirection:
                actions.append(direction1)
            else:
                actions.append(direction2)
            i += 1
        i, nombreRegards, directionRegard = 0, random.randint(1,2), actions[len(actions)-1]
        while i < nombreRegards:
            while directionRegard == actions[len(actions)-1]:
                directionRegard = "V" + self._boiteOutils.getDirectionAuHasard() + str(2500)
            actions.append(directionRegard)
            i += 1
        self._listeActions, self._etapeAction, self._pixelsParcourus, self._repetitionActions, self._deplacementBoucle = actions, 0, 0, False, True
        Horloge.initialiser(id(self), 1, 1)

    def _determinerAnimation(self, surPlace=False):
        """Adapte le pied actuel et le fait d'être en marche à l'étape d'animation actuelle s'il est temps de changer d'animation (selon l'horloge n°2). 
        <surPlace> doit valoir <True> quand on est en animation sur place.
        Retourne <True> quand un changement d'animation est nécessaire."""
        if surPlace != self._surPlace:
            self._surPlace = surPlace
            self._etapeAnimation, self._sensAnimation = 1, 1
        if Horloge.sonner(id(self), 2) is True and self._surPlace is False:
            if self._etapeAnimation <= 1:
                self._etapeAnimation, self._sensAnimation = 1, 1
            elif self._etapeAnimation >= 3:
                self._etapeAnimation, self._sensAnimation = 3, -1
            self._etapeAnimation += self._sensAnimation
            Horloge.initialiser(id(self), 2, self._dureeAnimation)
            return True
        elif self._surPlace is True:
            self._surPlace = True
            self._etapeAnimation += self._sensAnimation
            if self._etapeAnimation >= 8:
                self._sensAnimation = -1
            if self._etapeAnimation <= 1:
                self._sensAnimation = 1
        else:
            return False

    def _ajusterPositionSource(self, enMarche, direction):
        """Donne la position source du PNJ en marche ou en fin de parcours, en fonction de la direction"""
        hauteurTile = self._jeu.carteActuelle.hauteurTile
        if not self._surPlace:
            self._nomTileset = self._nomTilesetMouvement
            self._positionSource.left, self._positionSource.top = 0, 0
            self._positionSource.move_ip(self._persoCharset[0] * self._positionSource.width * 3, self._persoCharset[1] * self._positionSource.height * 4)
            if "Bas" in direction:
                pass
            elif "Gauche" in direction:
                self._positionSource.move_ip(0, 1 * self._positionSource.height)
            elif "Droite" in direction:
                self._positionSource.move_ip(0, 2 * self._positionSource.height)
            elif "Haut" in direction:
                self._positionSource.move_ip(0, 3 * self._positionSource.height)
            self._positionSource.move_ip(32 * (self._etapeAnimation-1), 0)
            if direction[0] == "V" or direction[0] == "R":
                direction = direction[1:]
            self._directionRegard = str(direction)  
        else:
            self._nomTileset, avanceeSelonDirection = self._nomTilesetSurPlace, {"Droite":0, "Gauche":32, "Bas":64, "Haut":96}
            self._positionSource.left, self._positionSource.top = 0, 0
            self._positionSource.move_ip(0, avanceeSelonDirection[self._boiteOutils.getDirectionBase(direction)])
            self._positionSource.move_ip(32 * (self._etapeAnimation - 1), 0)
