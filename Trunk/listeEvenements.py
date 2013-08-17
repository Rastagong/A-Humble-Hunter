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

class LanceurMusique(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        Horloge.initialiser(id(self), "Attente Musique Foret", 1)
        Horloge.initialiser(id(self), "Attente Rires", 1)

    def traiter(self):
        if self._boiteOutils.interrupteurs["MusiqueForet"].voir() and Horloge.sonner(id(self), "Attente Musique Foret", arretApresSonnerie=False):
            self._boiteOutils.jouerSon("Lost In The Meadows", "Musique forêt meadows", volume=VOLUME_LONGUE_MUSIQUE)
            Horloge.initialiser(id(self), "Attente Musique Foret", self._boiteOutils.getDureeInstanceSon("Musique forêt meadows") +  random.randint(120000, 4* 60000))
        if self._boiteOutils.interrupteurs["Rires"].voir() and Horloge.sonner(id(self), "Attente Rires", arretApresSonnerie=False):
            self._boiteOutils.jouerSon("Laugh", "Rires")
            Horloge.initialiser(id(self), "Attente Rires", self._boiteOutils.getDureeInstanceSon("Rires") +  random.randint(10000, 20000))
        if self._boiteOutils.interrupteurs["MusiqueForet"].voir() is True and self._jeu.carteActuelle.nom not in self._boiteOutils.variables["CartesForet"]:
            self._boiteOutils.interrupteurs["MusiqueForet"].desactiver()

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
            if self._jeu.carteActuelle.deplacementPossible(positionFleche, self._boiteOutils.coucheJoueur, nomFleche, positionCollision=positionCollision, positionVisible=positionVisible, verifPrecise=True, ecranVisible=True, exclusionCollision=["Joueur"], collisionEffective=True, axeTiles=False):
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
                if carte.deplacementPossible(positionFleche, self._boiteOutils.coucheJoueur, nomFleche, positionCollision=positionCollision, positionVisible=positionVisible, verifPrecise=True, ecranVisible=True, exclusionCollision=["Joueur"], collisionEffective=True, axeTiles=False):
                    self._jeu.carteActuelle.poserPNJ(positionFleche, self._boiteOutils.coucheJoueur, self._positionSources[direction], "Arrow.png", (0,0,0), nomFleche)
                else:
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
        self._messageBoutonInteraction, self._premiereMortChasse = False, False
    
    def traiter(self):
        x, y = self._gestionnaire.xJoueur, self._gestionnaire._yJoueur
        if self._boiteOutils.nomCarte == "Clairiere":
            if self._etape == 0:
                self._boiteOutils.jouerSon("sonsForet", "boucleSonsForet", nombreEcoutes=0, volume=VOLUME_MUSIQUE/5)
                self._boiteOutils.ajouterPensee("It was early spring in the woods and the snow had melted, at last. I could hunt again.")
                self._boiteOutils.ajouterPensee("It was more than time. Winter had been harsh. No more food, no more money.")
                self._boiteOutils.ajouterPensee("We were almost starving.")
                self._boiteOutils.ajouterTransformation(True, "Alpha", alpha=self._coefNoircisseur)
                self._coordonneesJoueur = self._boiteOutils.getCoordonneesJoueur()
                Horloge.initialiser(id(self), "TempsDecouverte", 20000)
                Horloge.initialiser(id(self), "Alpha", 100)
                self._etape += 1
            if self._etape == 1 and Horloge.sonner(id(self), "Alpha"):
                self._coefNoircisseur += 7
                if self._coefNoircisseur > 255:
                    self._coefNoircisseur = 255
                self._boiteOutils.ajouterTransformation(True, "Alpha", alpha=self._coefNoircisseur)
                if self._coefNoircisseur == 255:
                    self._boiteOutils.retirerTransformation(True, "Alpha")
                    self._etape += 1
                else:
                    Horloge.initialiser(id(self), "Alpha", 100)
            if self._etape == 2:
                if self._boiteOutils.interrupteurs["DecouverteSquirrels"].voir():
                    Horloge.initialiser(id(self), "SplashArrow", 3000)
                    self._etape += 1
            if self._etape == 3 and Horloge.sonner(id(self), "SplashArrow"):
                self._boiteOutils.ajouterTransformation(True, "SplashText Arrow", texte="Press X to shoot an arrow", antialias=True, couleurTexte=(255,255,255), position=(10, 10), taille=30, alpha=self._alpha)
                self._etape += 1
            if self._etape > 3 and self._etape < 7:
                if self._messageBoutonInteraction is False and self._premiereMortChasse is True:
                    self._messageBoutonInteraction = True
                    self._boiteOutils.retirerTransformation(True, "SplashText Arrow")
                    self._boiteOutils.ajouterTransformation(True, "SplashText Interaction1", texte="Press Z to interact", antialias=True, couleurTexte=(255,255,255), position=(10, 10), taille=30, alpha=self._alpha)
                    self._boiteOutils.ajouterTransformation(True, "SplashText Interaction2", texte="Or W on an AZERTY keyboard", antialias=True, couleurTexte=(255,255,255), position=(10, 40), taille=20, alpha=self._alpha)
                    self._gestionnaire.evenements["abstraits"]["Divers"]["GestionnaireAnimaux"].nombre["SquirrelMinimal"] = 0 #On ne restaure plus les écureuils...
                    self._gestionnaire.evenements["abstraits"]["Divers"]["GestionnaireAnimaux"].restaurerMortsParFuite = True #Sauf quand ils meurent par fuite
                if Horloge.sonner(id(self), "Début SplashText Titre"):
                    Horloge.initialiser(id(self), "Fin SplashText Titre", 5000)
                    self._boiteOutils.ajouterTransformation(True, "SplashText Titre1", texte="A", antialias=True, couleurTexte=(255,255,255), position=(10, 0))
                    self._boiteOutils.ajouterTransformation(True, "SplashText Titre2", texte="Humble", antialias=True, couleurTexte=(255,255,255), position=(10, FENETRE["largeurFenetre"]/4))
                    self._boiteOutils.ajouterTransformation(True, "SplashText Titre3", texte="Hunter", antialias=True, couleurTexte=(255,255,255), position=(10, FENETRE["largeurFenetre"]/2))
                if Horloge.sonner(id(self), "Fin SplashText Titre"):
                    self._boiteOutils.retirerTransformation(True, "SplashText Titre1")
                    self._boiteOutils.retirerTransformation(True, "SplashText Titre2")
                    self._boiteOutils.retirerTransformation(True, "SplashText Titre3")
                if self._boiteOutils.variables["SquirrelChasses"] == 1 and self._etape == 4:
                    self._boiteOutils.ajouterPensee("A squirrel... I won't feed anyone with that. I can merely sell its coat.")
                    self._boiteOutils.retirerTransformation(True, "SplashText Interaction1")
                    self._boiteOutils.retirerTransformation(True, "SplashText Interaction2")
                    Horloge.initialiser(id(self), "Début SplashText Titre", 12000)
                    self._boiteOutils.interrupteurs["MusiqueForet"].activer()
                    self._etape += 1
                if self._boiteOutils.variables["SquirrelChasses"] == 2 and self._etape == 5:
                    self._boiteOutils.ajouterPensee("Truly, the gods haven't been fair with the humble hunter I am....")
                    Horloge.initialiser(id(self), "tempsFinChasse", 20000)
                    self._coordonneesJoueur = self._boiteOutils.getCoordonneesJoueur()
                    self._etape += 2
            if self._etape == 7 and (Horloge.sonner(id(self), "tempsFinChasse") or self._boiteOutils.deplacementConsequentJoueur(self._coordonneesJoueur, 20)):
                self._boiteOutils.ajouterPensee("It seems we won't eat tonight either, there's nothing left to hunt. I should go home.")
                self._boiteOutils.interrupteurs["finChasse1"].activer()
                self._etape += 1
        if self._boiteOutils.nomCarte == "InterieurMaison":
            if self._etape < 8:
                self._etape = 8
            if self._etape == 8 and self._boiteOutils.getCoordonneesJoueur() == (13,3):
                self._boiteOutils.arreterSonEnFondu("boucleSonsForet", 3000)
                self._boiteOutils.interrupteurs["Rires"].activer()
                self._etape += 1
            if self._etape == 9 and (self._boiteOutils.getCoordonneesJoueur() == (11,13) or self._boiteOutils.getCoordonneesJoueur() == (11,14)):
                self._boiteOutils.interrupteurs["Rires"].desactiver()
                self._boiteOutils.ajouterPensee("They froze when they saw me. They wanted to see what I'd caught.")
                self._boiteOutils.interrupteurs["JoueurEntre"].activer()
                self._gestionnaire.evenements["abstraits"]["Divers"]["SignaleurJoueur"].ajouterSignaleur("InterieurMaison", "JoueurEntre2", (10,4))
                self._gestionnaire.evenements["abstraits"]["Divers"]["SignaleurJoueur"].ajouterSignaleur("InterieurMaison", "JoueurEntre3", (6,4))
                Horloge.initialiser(id(self), "Attente squirrelPose", 15000)
                self._etape += 1
            if self._etape == 10 and Horloge.sonner(id(self), "Attente squirrelPose") and not self._boiteOutils.interrupteurs["squirrelPose"].voir():
                self._boiteOutils.ajouterTransformation(True, "SplashText InteractionTable1", texte="Press Z to interact with the table", antialias=True, couleurTexte=(255,255,255), position=(10, 10), taille=30, alpha=self._alpha)
                self._boiteOutils.ajouterTransformation(True, "SplashText InteractionTable2", texte="Or W on an AZERTY keyboard", antialias=True, couleurTexte=(255,255,255), position=(10, 40), taille=20, alpha=self._alpha)
            if self._etape == 10 and self._boiteOutils.interrupteurs["squirrelPose"].voir() is True:
                self._boiteOutils.ajouterPensee("I'm sorry... I only got squirrels...", faceset="Chasseur.png")
                self._boiteOutils.ajouterPensee("Tom, Elie, go play upstairs.", nom="thoughtUpstairs", faceset="Belia.png")
                self._boiteOutils.ajouterPensee("Let's talk outside. I must wash some clothes anyway.", nom="thoughtOutside", faceset="Belia.png")
                self._boiteOutils.jouerSon("Osare Unrest Middle", "Thème familier", volume=VOLUME_LONGUE_MUSIQUE, nombreEcoutes=0)
                self._boiteOutils.retirerTransformation(True, "SplashText InteractionTable1")
                self._boiteOutils.retirerTransformation(True, "SplashText InteractionTable2")
                Horloge.initialiser(id(self), "Rires Upstairs", 6000)
                self._etape += 1
            if self._etape == 11 and Horloge.sonner(id(self), "Rires Upstairs"):
                self._boiteOutils.jouerSon("Laugh", "Rires")
                self._etape += 1
        if self._boiteOutils.nomCarte == "Maison":
            if self._etape < 12:
                self._etape = 12
            if self._etape == 12 and self._boiteOutils.interrupteurs["discussionEtang"].voir():
                self._boiteOutils.ajouterPensee("We'll have to fetch some nuts for the children,", faceset="Belia.png")
                self._boiteOutils.ajouterPensee("you should shake down the oak trees.", faceset="Belia.png")
                i, positions = 0, [(12,2),(7,4),(5,9),(20,10),(23,12),(19,14),(7,15),(15,17),(7,19)]
                while i < 9:
                    self._gestionnaire.evenements["concrets"]["Maison"]["Chene"+str(i)]=[Chene(self._jeu, self._gestionnaire, positions[i][0], positions[i][1], i), positions[i], "Aucune"]
                    i += 1
                self._etape += 1
            if self._etape == 13 and self._boiteOutils.penseeAGerer.voir() is False:
                Horloge.initialiser(id(self), "Discussion attente", 15000)
                self._etape += 1
            if self._etape == 14 and Horloge.sonner(id(self), "Discussion attente"):
                self._boiteOutils.ajouterPensee("How many hares have you seen today?", faceset="Belia.png")
                self._boiteOutils.ajouterPensee("None. These woods are almost inhabited.", faceset="Chasseur.png")
                self._boiteOutils.ajouterPensee("I don't know what to do. We can't even harvest our crops yet.", faceset="Belia.png")
                self._etape += 1
            if self._etape == 15 and self._boiteOutils.penseeAGerer.voir() is False:
                Horloge.initialiser(id(self), "Discussion attente", 15000)
                self._etape += 1
            if self._etape == 16 and Horloge.sonner(id(self), "Discussion attente"):
                self._boiteOutils.ajouterPensee("The other day, I saw Doug, the forest warden... And he told me that...", faceset="Chasseur.png")
                self._boiteOutils.ajouterPensee("...that the heart of the forest conceals the most extraordinary game.", faceset="Chasseur.png")
                self._boiteOutils.ajouterPensee("It might be dangerous, but it sure could feed us for days.", faceset="Chasseur.png")
                self._boiteOutils.ajouterPensee("No one enters the heart of the forest. Not even the prince. Forget it.", faceset="Belia.png")
                self._boiteOutils.ajouterPensee("But we will starve if we do nothing.", faceset="Chasseur.png")
                self._boiteOutils.ajouterPensee("Pray the gods. It could be worse. We're still alive, for now.", faceset="Belia.png")
                self._etape += 1
            if self._etape == 17 and self._boiteOutils.interrupteurs["BeliaRentree"].voir():
                self._boiteOutils.ajouterPensee("Praying the gods? Praying the gods?")
                self._boiteOutils.ajouterPensee("I've been praying them for years... What did they grant me?")
                self._boiteOutils.ajouterPensee("I had to go to sleep. Now.")
                self._etape += 1
                """self._coefNoircisseur = 1
                self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
                self._boiteOutils.joueurLibre.desactiver()
                Horloge.initialiser(id(self), "Transition Noir", 1000)
                self._etape += 1
            if self._etape == 10 and Horloge.sonner(id(self), "Transition Noir"):
                self._coefNoircisseur += 1
                self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
                if self._coefNoircisseur >= 12:
                    self._etape += 1
                    Horloge.initialiser(id(self), "Transition Scene Interieur", 3000)
                else:
                    Horloge.initialiser(id(self), "Transition Noir", 100)
            if self._etape == 11 and Horloge.sonner(id(self), "Transition Scene Interieur"):
                self._boiteOutils.retirerTransformation(True, "Noir")
                self._boiteOutils.teleporterSurCarte("EtageMaison", 9, 3, 2, "Bas")
                self._coefNoircisseur = 12
                self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
                Horloge.initialiser(id(self), "Transition Noir", 100)
                self._boiteOutils.joueurLibre.activer()
                self._boiteOutils.ajouterPensee("I woke up at dawn. I had only one thing to do. Go hunting.")
                self._etape += 1
            if self._etape == 12 and Horloge.sonner(id(self), "Transition Noir"):
                self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
                self._coefNoircisseur -= 1
                if self._coefNoircisseur == 1:
                    self._boiteOutils.retirerTransformation(True, "Noir")
                else:
                    Horloge.initialiser(id(self), "Transition Noir", 100)"""
                
    def onMortAnimal(self, typeAnimal, viaChasse=False):
        if viaChasse and not self._premiereMortChasse:
            self._premiereMortChasse = True

class GestionnaireAnimaux(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._etape, self._restaurerMortsParFuite, self._morts = 0, False, []

    def _genererPositionsCachettes(self, nomTileset, couche, positionSource):
        x, y, positionsCachettes = 0, 0, []
        while x < self._jeu.carteActuelle.longueur:
            y = 0
            while y < self._jeu.carteActuelle.largeur:
                tile = self._jeu.carteActuelle.tiles[x][y].bloc[couche]
                if not tile.vide:
                    if tile.nomTileset == nomTileset:
                        if tile.positionSource == positionSource:
                            positionsCachettes.append((x,y))
                y += 1
            x += 1
        return positionsCachettes

    def _genererAnimauxDepart(self, longueurMin=0, longueurMax=-1, largeurMin=0, largeurMax=-1, verifProximite=True):
        position, x, y,= -1, -1, -1
        if longueurMax == -1:
            longueurMax = self._jeu.carteActuelle.longueur
        if largeurMax == -1:
            largeurMax = self._jeu.carteActuelle.largeur
        i, numeroTypeActuel, typeActuel, positionsDepart = 1, 0, "", []
        while numeroTypeActuel < len(self._typesAnimaux):
            typeActuel, animauxDeCeType = self._typesAnimaux[numeroTypeActuel], 1
            while animauxDeCeType <= self._nombre[typeActuel]:
                while position in positionsDepart or (x,y) == (-1,-1) or self._jeu.carteActuelle.tilePraticable(x,y,self._c) is False or len([positionActuelle for positionActuelle in positionsDepart if (self._boiteOutils.tileProcheDe(position, positionActuelle, 10) is True and verifProximite is True)]) > 0:
                    position = (random.randint(longueurMin, longueurMax), random.randint(largeurMin, largeurMax))
                    x,y = position[0], position[1]
                positionsDepart.append(position)
                objetAnimal = self._parametresGeneration[typeActuel]["classe"](self._jeu, self._gestionnaire, x, y, self._c, animauxDeCeType, self, **self._parametresGeneration[typeActuel])
                self._gestionnaire.evenements["concrets"][self._jeu.carteActuelle.nom][typeActuel+str(animauxDeCeType)] = [objetAnimal, (x,y), "Bas"]
                print("Au depart", self._parametresGeneration[typeActuel]["typeAnimal"]+str(animauxDeCeType), (x,y))
                animauxDeCeType += 1
                i += 1
            numeroTypeActuel += 1

    def traiter(self):
        if self._etape == 0 and self._boiteOutils.variables["sceneChasse"] == 0:
            if self._jeu.carteActuelle.nom == "Clairiere":
                self._c = 2
                self._nombre = {"Squirrel":5, "SquirrelMinimal":0}
                self._typesAnimaux = ["Squirrel"]
                self._parametresGeneration = dict()
                positionsArbres = self._genererPositionsCachettes("base_out_atlas.png", 2, (832, 672, 32, 32))
                positionsSapins = self._genererPositionsCachettes("base_out_atlas.png", 2, (800, 544, 32, 32))
                self._parametresGeneration["Squirrel"] = {"typeAnimal":"Squirrel", "classe":Squirrel, "positionsCachettes":positionsArbres, "longueurSprite":32, "largeurSprite":32, "vitesseDeplacement":250, "mobilite":False, "peur":True}
                self._parametresGeneration["Lapin"] = {"typeAnimal":"Lapin", "classe":Lapin, "positionsCachettes":positionsSapins, "longueurSprite":32, "largeurSprite":32, "vitesseDeplacement":100, "arretAvant":True, "coucheMonteeArbre":1}
                for typeAnimal in self._typesAnimaux:
                    self._nombre[typeAnimal+"Total"] = self._nombre[typeAnimal]
                    Horloge.initialiser(id(self), "SonEating" + typeAnimal, 1)
                self._genererAnimauxDepart(longueurMin=0, largeurMin=44, longueurMax=4, largeurMax=48, verifProximite=False)
                self._etape += 1
        if self._etape == 0 and self._boiteOutils.variables["sceneChasse"] == 1:
            if self._jeu.carteActuelle.nom == "Clairiere":
                self._typesAnimaux = ["Squirrel"]
                self._nombre = {"Squirrel":3, "SquirrelMinimal":3}
                self._parametresGeneration = dict()
                positionsArbres = self._genererPositionsCachettes("base_out_atlas.png", 2, (832, 672, 32, 32))
                positionsSapins = self._genererPositionsCachettes("base_out_atlas.png", 2, (800, 544, 32, 32))
                self._parametresGeneration["Squirrel"] = {"typeAnimal":"Squirrel", "classe":Squirrel, "positionsCachettes":positionsArbres, "longueurSprite":32, "largeurSprite":32, "vitesseDeplacement":150}
                self._parametresGeneration["Lapin"] = {"typeAnimal":"Lapin", "classe":Lapin, "positionsCachettes":positionsSapins, "longueurSprite":32, "largeurSprite":32, "vitesseDeplacement":100, "arretAvant":True, "coucheMonteeArbre":1}
            for typeAnimal in self._typesAnimaux:
                self._nombre[typeAnimal+"Total"] = self._nombre[typeAnimal]
                Horloge.initialiser(id(self), "SonEating" + typeAnimal, 1)
            self._genererAnimauxDepart()
            self._etape += 1
        if self._etape == 1:
            for (typeAnimal, viaChasse) in self._morts:
                if self._nombre[typeAnimal] < self._nombre[typeAnimal+"Minimal"] or (viaChasse is False and self._restaurerMortsParFuite is True):
                    self._regenererAnimaux(typeAnimal, self._parametresGeneration[typeAnimal]["classe"])
            del self._morts[:]
            if self._boiteOutils.variables["sceneChasse"] == 0 and self._nombre["Squirrel"] == 0:
                self._boiteOutils.variables["sceneChasse"] = 1
                self._nombre["SquirrelMinimal"] = 2
                positionsArbres = self._genererPositionsCachettes("base_out_atlas.png", 2, (832, 672, 32, 32))
                positionsSapins = self._genererPositionsCachettes("base_out_atlas.png", 2, (800, 544, 32, 32))
                self._parametresGeneration["Squirrel"] = {"typeAnimal":"Squirrel", "classe":Squirrel, "positionsCachettes":positionsArbres, "longueurSprite":32, "largeurSprite":32, "vitesseDeplacement":150}
                self._morts = [("Squirrel", False)]*3
    
    def _regenererAnimaux(self, typeAnimal, classe):
        self._nombre[typeAnimal+"Total"] += 1
        self._nombre[typeAnimal] += 1
        positionCarte, nom = Rect(0, 0, 32, 32), typeAnimal + str(self._nombre[typeAnimal+"Total"])
        while (positionCarte.left,positionCarte.top) == (0,0) or self._jeu.carteActuelle.deplacementPossible(positionCarte, self._c, nom) is False or (self._jeu.carteActuelle._ecranVisible.contains(positionCarte) or self._jeu.carteActuelle._ecranVisible.colliderect(positionCarte)):
            positionCarte.left, positionCarte.top = random.randrange(0, self._jeu.carteActuelle.longueur*32, 32), random.randrange(0, self._jeu.carteActuelle.largeur*32, 32)
        objet = classe(self._jeu, self._gestionnaire, positionCarte.left/32, positionCarte.top/32, self._c, self._nombre[typeAnimal+"Total"], self, **self._parametresGeneration[typeAnimal])
        self._gestionnaire.evenements["concrets"][self._jeu.carteActuelle.nom][nom] = [objet, (positionCarte.left/32, positionCarte.top/32), "Bas"]
        print("Ajout de", nom, (int(positionCarte.left/32), int(positionCarte.top/32)) )

    def onMortAnimal(self, typeAnimal, viaChasse=False):
        self._nombre[typeAnimal] -= 1
        self._morts.append((typeAnimal, viaChasse))

    def _getNombre(self):
        return self._nombre

    def _setNombre(self, nouveauNombre):
        self._nombre = nouveauNombre

    def _getRestaurerMortsParFuite(self):
        return self._restaurerMortsParFuite
    
    def _setRestaurerMortsParFuite(self, val):
        self._restaurerMortsParFuite = val

    nombre = property(_getNombre, _setNombre)
    restaurerMortsParFuite = property(_getRestaurerMortsParFuite, _setRestaurerMortsParFuite)

class Gibier(PNJ):
    def __init__(self, jeu, gestionnaire, x, y, c, numero, gestionnaireAnimaux, positionsCachettes=[], typeAnimal="", longueurSprite=-1, largeurSprite=-1, vitesseDeplacement=-1, arretAvant=False, coucheMonteeArbre=False, classe=None, mobilite=True, peur=False):
        fichier, couleurTransparente, persoCharset, vitesseDeplacement = typeAnimal+"Moving.png", (0,0,0), (0,0), vitesseDeplacement
        repetitionActions, directionDepart, listeActions = False, "Bas", []
        super().__init__(jeu, gestionnaire, typeAnimal+str(numero), x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement, fuyard=True, dureeAnimationSP=160, longueurSprite=longueurSprite, largeurSprite=largeurSprite)
        self._penseePossible, self._surPlace = InterrupteurInverse(self._boiteOutils.penseeAGerer), False
        self._nomTilesetMouvement, self._nomTilesetSurPlace, self._vie, self._fuite, self._positionsCachettes, self._cadavreEnPlace = fichier, typeAnimal+"Eating.png", 3, False, positionsCachettes, False
        self._xArrivee, self._yArrivee, self._vulnerable, self._monteeArbre, self._gestionnaireAnimaux, self._animationMort = -1, -1, True, False, gestionnaireAnimaux, False
        self._sonMange, self._typeAnimal, self._arretAvant, self._mobilite, self._peur, self._blessure = False, typeAnimal, arretAvant, mobilite, peur, False
        self._coucheMonteeArbre = coucheMonteeArbre if coucheMonteeArbre is not False else self._c
        Horloge.initialiser(id(self), "Rouge clignotant", 1)

    def _gererEtape(self):
        if self._peur is True and self._fuite is False and self._animationMort is False and self._monteeArbre is False:
            if self._boiteOutils.tileProcheDe((self._xTile,self._yTile), self._boiteOutils.getCoordonneesJoueur(), 4) or self._boiteOutils.interrupteurs["DecouverteSquirrels"].voir():
                self._finirDeplacementSP()
                self._boiteOutils.interrupteurs["DecouverteSquirrels"].activer()
                self._lancerFuite()
        if self._fuite is False and self._deplacementBoucle is False and self._animationMort is False and self._monteeArbre is False:
            self._genererLancerTrajetAleatoire(4, 8)
            self._sonMange = False
        elif self._fuite is False and self._deplacementBoucle is True and self._animationMort is False and self._sonMange is False and self._etapeAction < len(self._listeActions) and isinstance(self._listeActions[self._etapeAction],str) and self._listeActions[self._etapeAction][0] == "V" and Horloge.sonner(id(self._gestionnaireAnimaux), "SonEating"+self._typeAnimal, arretApresSonnerie=False) and self._monteeArbre is False:
            print("1")
            self._boiteOutils.jouerSon(self._typeAnimal+"Eating", self._nom + "eating", fixe=True, evenementFixe=self._nom, volume=VOLUME_MUSIQUE/3)
            Horloge.initialiser(id(self._gestionnaireAnimaux), "SonEating"+self._typeAnimal, 1000) 
            self._sonMange = True
        elif self._fuite:
            if self._blessure is True and self._etapeTraitement == 1 and Horloge.sonner(id(self), "Rouge clignotant"):
                self._boiteOutils.ajouterTransformation(False, "Rouge/"+self._nom, nom=self._nom)
                Horloge.initialiser(id(self), "Rouge clignotant", 200)
                self._etapeTraitement += 1
            if self._blessure is True and self._etapeTraitement == 2 and Horloge.sonner(id(self), "Rouge clignotant"):
                self._boiteOutils.retirerTransformation(False, "Rouge/"+self._nom)
                if Horloge.sonner(id(self), "Fin clignotant"):
                    self._etapeTraitement += 1
                else:
                    Horloge.initialiser(id(self), "Rouge clignotant", 200)
                    self._etapeTraitement -= 1
            if self._deplacementBoucle is False and ( (self._arretAvant is False and self._xTile == self._xArrivee and self._yTile == self._yArrivee) or (self._arretAvant is True and self._boiteOutils.tileProcheDe((self._xTile,self._yTile), (self._xArrivee, self._yArrivee), 1) is True) ):
                self._vulnerable = False
                if self._c != self._coucheMonteeArbre:
                    self._changerCouche(self._coucheMonteeArbre)
                self._lancerTrajet("Haut","Haut",False, deplacementLibre=True)
                self._boiteOutils.retirerTransformation(False, "Rouge/"+self._nom)
                print("2")
                self._boiteOutils.jouerSon(self._typeAnimal+"Fuite", self._nom + "fuite", fixe=True, xFixe=self._xTile, yFixe=self._yTile)
                self._monteeArbre, self._fuite = True, False
        if self._monteeArbre:
            if self._deplacementBoucle is False:
                self._boiteOutils.supprimerPNJ(self._nom, self._c)
                self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, self._nom)
                self._gestionnaireAnimaux.onMortAnimal(self._typeAnimal)
                self._gestionnaire.evenements["abstraits"]["Divers"]["Narrateur"].onMortAnimal(self._typeAnimal)
        if self._animationMort is True and self._xTile == self._tileCadavre[0] and self._yTile == self._tileCadavre[1] and self._cadavreEnPlace is False:
            self._cadavreEnPlace = True

    def onCollision(self, nomPNJ, positionCarte):
        super().onCollision(nomPNJ, positionCarte)
        if "Fleche" in nomPNJ and self._vulnerable:
            self._vie -= 1
            self._etapeTraitement, self._intelligence, self._courage, self._fuyard, self._blessure = 1, True, True, False, True
            print("3")
            self._boiteOutils.jouerSon(self._typeAnimal+"Blesse", self._nom + "blesse", fixe=True, evenementFixe=self._nom)
            Horloge.initialiser(id(self), "Fin clignotant", 2000)
            Horloge.initialiser(id(self), "Rouge clignotant", 1)
            self._lancerFuite()
        if self._vie == 0 and self._animationMort is False:
            self._finirDeplacementSP()
            self._trouverTileCadavre()
            self._gestionnaireAnimaux.onMortAnimal(self._typeAnimal, viaChasse=True)
            self._gestionnaire.evenements["abstraits"]["Divers"]["Narrateur"].onMortAnimal(self._typeAnimal, viaChasse=True)
            self._changerCouche(self._c-1)
            self._lancerTrajet(Rect(self._tileCadavre[0]*32, self._tileCadavre[1]*32, 32, 32), False, deplacementLibre=True)
            self._vulnerable, self._fuite, self._animationMort = False, False, True
            self._boiteOutils.retirerTransformation(False, "Rouge/"+self._nom)

    def _lancerFuite(self):
        if not self._fuite:
            self._positionsCachettes = sorted(self._positionsCachettes, key=lambda position: self._boiteOutils.estimationDistanceRestante((self._xTile, self._yTile), position))
            i, positionIdealeTrouvee = 0, False
            while i < len(self._positionsCachettes) and not positionIdealeTrouvee:
                positionJoueur = (self._gestionnaire.xJoueur, self._gestionnaire.yJoueur)
                distanceArbreJoueur = self._boiteOutils.estimationDistanceRestante(positionJoueur, self._positionsCachettes[i])
                distanceArbreSquirrel = self._boiteOutils.estimationDistanceRestante((self._xTile, self._yTile), self._positionsCachettes[i])
                if self._boiteOutils.tileProcheDe(self._positionsCachettes[i], positionJoueur, 3) is False and (distanceArbreSquirrel <= distanceArbreJoueur or distanceArbreSquirrel > 10):
                    self._finirDeplacementSP()
                    self._xArrivee, self._yArrivee = self._positionsCachettes[i]
                    self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xArrivee, self._yArrivee, arretAvant=self._arretAvant)
                    positionIdealeTrouvee = True
                i += 1
            self._fuite, self._fuyard = True, False

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._cadavreEnPlace is True:
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._boiteOutils.variables[self._typeAnimal+"Chasses"] += 1
            self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, self._nom)

    def _trouverTileCadavre(self):
        tilesVisites = [(self._xTile,self._yTile)]
        tiles = self._ajouterPositionsAdjacentes((self._xTile,self._yTile), tilesVisites)
        positionCarte, self._tileCadavre = Rect(0,0,32,32), False
        while self._tileCadavre is False:
            for tile in tiles:
                positionCarte.left, positionCarte.top = tile[0]*32, tile[1]*32
                if self._jeu.carteActuelle.tilePraticable(tile[0],tile[1],self._c) and self._jeu.carteActuelle.tiles[tile[0]][tile[1]].bloc[self._c+1].vide is True and self._jeu.carteActuelle.deplacementPossible(positionCarte, self._c, self._nom) and tile not in tilesVisites:
                    self._tileCadavre = tile
                    break
                else:
                    tilesVisites.append(tile)
                    tiles += self._ajouterPositionsAdjacentes(tile, tilesVisites)
            x, y = 0, 0

    def _ajouterPositionsAdjacentes(self, tileCentral, tilesVisites):
        x,y, tiles = -1, -1, []
        while x <= 1:
            y = -1
            while y <= 1:
                tileActuel = (tileCentral[0] + x, tileCentral[1] + y)
                if self._jeu.carteActuelle.tileExistant(*tileActuel) and tileActuel not in tilesVisites:
                    tiles.append(tileActuel)
                y += 1
            x += 1
        return tiles

    def _genererRegards(self, actions):
        i, nombreRegards= 0, random.randint(1,2)
        if len(actions) > 0:
            directionRegard = actions[len(actions)-1]
        else:
            directionRegard = "V" + self._boiteOutils.getDirectionAuHasard() + str(2500)
            actions.append(directionRegard)
        while i < nombreRegards:
            while directionRegard == actions[len(actions)-1]:
                directionRegard = "V" + self._boiteOutils.getDirectionAuHasard() + str(2500)
            actions.append(directionRegard)
            i += 1
        return actions

    def _genererLancerTrajetAleatoire(self, longueurMin, longueurMax, regards=True):
        self._longueurMin, self._longueurMax, i, actions = longueurMin, longueurMax, 0, []
        if self._mobilite is True:
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
        if regards:
            actions = self._genererRegards(actions)
        self._lancerTrajet(actions, False)
        Horloge.initialiser(id(self), 1, 1)

class Squirrel(Gibier):
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
        if self._animationMort:
            self._nomTileset, self._positionSource.left, self._positionSource.top, self._positionSource.width, self._positionSource.height = "SquirrelDead.png", 0, 0, 32, 32
        else:
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

class Lapin(Gibier):
    def _genererRegards(self, actions):
        i, nombreRegards, directionRegard = 0, random.randint(1,2), actions[len(actions)-1]
        while i < nombreRegards:
            while directionRegard == actions[len(actions)-1] or "Haut" in directionRegard or "Bas" in directionRegard:
                directionRegard = "V" + self._boiteOutils.getDirectionAuHasard() + str(2500)
            actions.append(directionRegard)
            i += 1
        return actions

    def _determinerAnimation(self, surPlace=False):
        """Adapte le pied actuel et le fait d'être en marche à l'étape d'animation actuelle s'il est temps de changer d'animation (selon l'horloge n°2). 
        <surPlace> doit valoir <True> quand on est en animation sur place.
        Retourne <True> quand un changement d'animation est nécessaire."""
        if surPlace != self._surPlace:
            self._surPlace = surPlace
            self._etapeAnimation = 0
        if Horloge.sonner(id(self), 2) is True and self._surPlace is False:
            if self._etapeAnimation < 1 or self._etapeAnimation >= 3:
                self._etapeAnimation = 0
            self._etapeAnimation += 1
            Horloge.initialiser(id(self), 2, self._dureeAnimation)
            return True
        elif self._surPlace is True:
            self._surPlace = True
            self._etapeAnimation += 1
            if self._etapeAnimation <= 1 or self._etapeAnimation >= 4:
                self._etapeAnimation = 1
        else:
            return False

    def _ajusterPositionSource(self, enMarche, direction):
        """Donne la position source du PNJ en marche ou en fin de parcours, en fonction de la direction"""
        hauteurTile = self._jeu.carteActuelle.hauteurTile
        if self._animationMort:
            self._nomTileset, self._positionSource.left, self._positionSource.top, self._positionSource.width, self._positionSource.height = "LapinDead.png", 0, 0, 32, 32
        else:
            self._nomTileset = self._nomTilesetMouvement
            self._positionSource.left, self._positionSource.top = self._positionSource.width * 1, 0
            if "Bas" in direction:
                pass
            elif "Haut" in direction:
                self._positionSource.move_ip(0, 1 * self._positionSource.height)
            elif "Droite" in direction:
                self._positionSource.move_ip(0, 2 * self._positionSource.height)
            elif "Gauche" in direction:
                self._positionSource.move_ip(0, 3 * self._positionSource.height)
            if self._surPlace:
                self._positionSource.move_ip(self._positionSource.width * 3, 0)
                self._positionSource.move_ip(self._positionSource.width * (self._etapeAnimation-1), 0)
            else:
                self._positionSource.move_ip(self._positionSource.width * (self._etapeAnimation-1), 0)
                if direction[0] == "V" or direction[0] == "R":
                    direction = direction[1:]
                self._directionRegard = str(direction)  


class Belia(PNJ):
    def __init__(self, jeu, gestionnaire):
        x, y, c = 7, 6, 2
        fichier, couleurTransparente, persoCharset, vitesseDeplacement = "Belia.png", (0,0,0), (0,0), 150
        repetitionActions, directionDepart = True, "Gauche"
        listeActions = ["Haut","Haut","Gauche","Gauche","Gauche","VHaut2500","Droite","Droite","Droite","VHaut2500","Droite","Droite","Droite","VHaut2500","Gauche","Gauche","Gauche","Bas","Bas","VGauche2500"]
        super().__init__(jeu, gestionnaire, "Belia", x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement)
        self._listeSons, self._etapeSon = [("Sack",5,1), ("Cupboard",9,1), ("Cupboard",13,1), ("Knife",18,3)], 0
        if self._boiteOutils.interrupteurs["squirrelPose"].voir() is True and self._boiteOutils.interrupteurs["BeliaRentree"].voir() is False:
            print("indeed")
            self._poseDepart = False

    def _gererEtape(self):
        if self._etapeTraitement == 1:
                self._gererSons()
        if self._etapeTraitement == 2 and self._deplacementBoucle is False:
            self._finirDeplacementSP()
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 5, 3, regardFinal="Bas", arretAvant=False)
            self._comportementParticulier = True
            self._etapeTraitement += 1
        if self._etapeTraitement == 3 and self._deplacementBoucle is False and self._xTile == 5 and self._yTile == 3 and self._comportementParticulier is True:
            self._comportementParticulier = False
        if self._etapeTraitement == 3 and self._boiteOutils.getNomPensee() == "thoughtOutside":
            self._comportementParticulier = True
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 7, 6, regardFinal="Droite")
            self._etapeTraitement += 1
        if self._etapeTraitement == 4 and self._xTile == 7 and self._yTile == 6 and self._deplacementBoucle is False:
            self._lancerTrajet("VDroite1500", False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(8, 5, 2, "base_out_atlas.png", (576, 448, 32, 32), (0,0,0), False, permanente=True, nomModif="Retrait tonneaux1")
            self._boiteOutils.changerBloc(9, 5, 2, "base_out_atlas.png", (608, 448, 32, 32), (0,0,0), False, permanente=True, nomModif="Retrait tonneaux2")
            self._boiteOutils.changerBloc(8, 6, 2, "base_out_atlas.png", (576, 480, 32, 32), (0,0,0), False, permanente=True, nomModif="Retrait tonneaux3")
            self._boiteOutils.changerBloc(9, 6, 2, "base_out_atlas.png", (608, 480, 32, 32), (0,0,0), False, permanente=True, nomModif="Retrait tonneaux4")
            self._boiteOutils.jouerSon("Barrel", "Taking it for laundry", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 13, 3)
            self._etapeTraitement += 1
        if self._etapeTraitement == 6 and self._deplacementBoucle is False and self._xTile == 13 and self._yTile == 3:
            self._boiteOutils.interrupteurs["BeliaSortie"].activer()
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._gestionnaire.ajouterEvenementATuer("concrets", "InterieurMaison", self._nom)
            self._etapeTraitement += 1

    def _gererSons(self):
        if self._etapeAction == self._listeSons[self._etapeSon][1]:
            self._boiteOutils.jouerSon(self._listeSons[self._etapeSon][0], "Cusisine"+str(self._etapeSon), fixe=True, evenementFixe="Belia", duree=2500, nombreEcoutes=self._listeSons[self._etapeSon][2])
            self._etapeSon += 1
            if self._etapeSon == 4:
                self._etapeSon = 0

class Chene(EvenementConcret):
    def __init__(self, jeu, gestionnaire, x, y, numero):
        super().__init__(jeu,gestionnaire)
        self._periodeAgitation, self._niveauAgitation, self._niveauGland, self._numero, self._glandTombe = False, 0, random.randint(20,25), str(numero), Interrupteur(False)
        self._tilesGlands, self._tileFeuilles = [(x+1,y+1), (x-1,y+1), (x+1,y), (x-1,y), (x,y-1)], (x,y-1)
        Horloge.initialiser(id(self), "Attente son", 1)

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if not self._periodeAgitation:
            Horloge.initialiser(id(self), "Deadline agitation", 20000)
        if Horloge.sonner(id(self), "Attente son"):
            self._boiteOutils.jouerSon("lapinFuite", "Chene secoue", fixe=True, xFixe=self._tileFeuilles[0], yFixe=self._tileFeuilles[1])
            Horloge.initialiser(id(self), "Attente son", 1000)
        self._periodeAgitation, self._niveauAgitation = True, self._niveauAgitation + 1

    def traiter(self):
        if self._niveauAgitation >= self._niveauGland and self._glandTombe.voir() is False:
            (x,y), i = self._tilesGlands[0], 0
            while (not self._jeu.carteActuelle.tileExistant(x,y) or not self._jeu.carteActuelle.tilePraticable(x, y, 2)) and i < len(self._tilesGlands):
                i += 1
                (x,y) = self._tilesGlands[i]
            self._gestionnaire.evenements["concrets"][self._jeu.carteActuelle.nom]["Gland"+self._numero] = [Gland(self._jeu, self._gestionnaire, self._tileFeuilles, x, y, self._numero), self._tileFeuilles, "Aucune"]
            self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, "Chene"+self._numero)
            self._glandTombe.activer()
        if Horloge.sonner(id(self), "Deadline agitation") and self._glandTombe.voir() is False:
            self._periodeAgitation, self._niveauAgitation = False, 0

class Gland(PNJ):
    def __init__(self, jeu, gestionnaire, tileFeuilles, xArrivee, yArrivee, numero):
        fichier, couleurTransparente, persoCharset = "Gland.png", (0,0,0), (0,0)
        (x,y), self._xArrivee, self._yArrivee = tileFeuilles, xArrivee, yArrivee
        repetitionActions, listeActions = False, ["Aucune"]
        super().__init__(jeu, gestionnaire, "Gland"+numero, x, y, 2, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, deplacementLibre=True, vitesseDeplacement=100)
        self._positionSource, self._glandPris = Rect(0,0,32,32), False

    def _ajusterPositionSource(self, enMarche, direction):
        pass

    def _gererEtape(self):
        if self._etapeTraitement == 1:
            self._tempsPrecedent = pygame.time.get_ticks()
            self._lancerTrajet(Rect(self._xArrivee*32,self._yArrivee*32,32,32), False, deplacementLibre=True)
            self._boiteOutils.jouerSon("lapinFuite", "Chene secoue", fixe=True, xFixe=self._xTile, yFixe=self._yTile)
            self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._xTile == self._xArrivee and self._yTile == self._yArrivee:
            self._changerCouche(self._c-1)
            self._etapeTraitement += 1

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if not self._glandPris:
            self._glandPris, self._boiteOutils.variables["NombreGlands"] = True, self._boiteOutils.variables["NombreGlands"] + 1
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, self._nom)

class Belia2(PNJ):
    def __init__(self, jeu, gestionnaire, x, y, poseDepart):
        fichier, couleurTransparente, persoCharset, vitesseDeplacement = "Belia.png", (0,0,0), (0,0), 150
        repetitionActions, directionDepart = False, "Bas"
        listeActions = ["Aucune"]
        super().__init__(jeu, gestionnaire, "Belia2", x, y, 2, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement, poseDepart=poseDepart)
        Horloge.initialiser(id(self), "Attente départ", 3000)
        self._sons, self._poseAutorisee = dict(), True
        self._sons[0] = [["Wateragitation", "Washing clothe"], {"fixe":True, "evenementFixe":self._nom}, True]
        self._sons[9], self._sons[18] = list(self._sons[0]), list(self._sons[0])
        self._sons[4] = [["Barrel", "Taking clothe"], {"fixe":True, "evenementFixe":self._nom}, True]
        self._sons[13], self._sons[22] = list(self._sons[4]), list(self._sons[4])
        self._sons[8] = [["Washing", "Washing clothe"], {"fixe":True, "evenementFixe":self._nom}, True]
        self._sons[17], self._sons[26] = list(self._sons[8]), list(self._sons[8])
        self._porteRefermee = False
        if not self._boiteOutils.interrupteurs["BeliaSortie"].voir() or not self._boiteOutils.interrupteurs["squirrelPose"].voir():
            self._poseAutorisee = False

    def _gererEtape(self):
        if self._etapeTraitement == 0 and self._poseAutorisee is True:
            coordonneesJoueur = self._boiteOutils.getCoordonneesJoueur()
            if self._boiteOutils.tileProcheDe((3,5), coordonneesJoueur, 3) is False or (Horloge.sonner(id(self), "Attente départ", arretApresSonnerie=False) and coordonneesJoueur != (3,5)):
                if self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].getPorteOuverte() is False:
                    self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].ouvrirOuFermerPorte()
                self._poseDepart = True
        if self._etapeTraitement == 1:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 14, arretAvant=True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._porteRefermee is False and self._boiteOutils.tileProcheDe((self._xTile,self._yTile),(3,4), 4) is False:
            if self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].getPorteOuverte():
                self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].ouvrirOuFermerPorte()
                self._porteRefermee = True
        if self._etapeTraitement == 2 and self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(15, 14, self._nom):
            self._boiteOutils.interrupteurs["discussionEtang"].activer()
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(15,14))+"1500",False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 3 and self._boiteOutils.getCoordonneesJoueur() != (15,14) and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(15, 14, 2, "base_out_atlas.png", (480, 448, 32, 32), (0,0,0), False)
            self._boiteOutils.jouerSon("Barrel", "Setting it up", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 17, 11, arretAvant=True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 4 and self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(17, 11, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(17,11))+"1500",False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and self._boiteOutils.getCoordonneesJoueur() != (17,11) and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(17, 10, 3, "base_out_atlas.png", (608, 448, 32, 32), (0,0,0), False)
            self._boiteOutils.changerBloc(17, 11, 2, "base_out_atlas.png", (608, 480, 32, 32), (0,0,0), False)
            self._boiteOutils.jouerSon("Barrel", "Setting it up2", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 13, regardFinal="Droite")
            self._etapeTraitement += 1
        if self._etapeTraitement == 6 and self._xTile == 15 and self._yTile == 13 and self._deplacementBoucle is False:
            self._lancerTrajet(["VDroite2500", "Haut", "Haut", "Droite", "VDroite2500","Gauche","Bas","Bas","VBas1500"]*3, False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 7:
            if self._deplacementBoucle is False:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 12, arretAvant=True)
                self._etapeTraitement += 1
            else:
                self._gererSons()
                if self._etapeAction == 17:
                    self._boiteOutils.changerBloc(15, 14, 2, "base_out_atlas.png", (480, 480, 32, 32), (0,0,0), False)
        if self._etapeTraitement == 8 and self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(15, 12, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(15,12))+"1500",False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 9 and self._boiteOutils.getCoordonneesJoueur() != (15,12) and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(15, 12, 2, "base_out_atlas.png", (480, 448, 32, 32), (0,0,0), False)
            self._boiteOutils.jouerSon("Barrel", "Setting it up3", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 13, regardFinal="Droite")
            self._etapeTraitement += 1
        if self._etapeTraitement == 10 and self._xTile == 15 and self._yTile == 13 and self._deplacementBoucle is False:
            self._majSons()
            self._lancerTrajet(["VDroite2500", "Gauche","Haut", "Haut", "Droite", "Droite", "VDroite2500","Gauche", "VBas1500", "Gauche", "Bas", "Bas", "Droite", "VBas1500"]*3, False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 11:
            if self._deplacementBoucle is False:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 17, 11, arretAvant=True)
                self._etapeTraitement += 1
            else:
                self._gererSons()
                if self._etapeAction == 22:
                    self._boiteOutils.changerBloc(15, 12, 2, "base_out_atlas.png", (480, 480, 32, 32), (0,0,0), False)
        if self._etapeTraitement == 12 and self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(17, 11, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(17,11))+"1500",False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 13 and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(17,11,2, -1,-1,-1,-1, vide=True )
            self._boiteOutils.changerBloc(17,10,3, -1,-1,-1,-1, vide=True )
            self._boiteOutils.jouerSon("Barrel", "Setting it up4", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 12, arretAvant=True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 14 and self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(15, 12, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(15,12))+"1500",False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 15 and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(15,12,2, -1,-1,-1,-1, vide=True )
            self._boiteOutils.jouerSon("Barrel", "Setting it up5", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 14, arretAvant=True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 16 and self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(15, 14, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(15,14))+"1500",False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 17 and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(15,14,2, -1,-1,-1,-1, vide=True )
            self._boiteOutils.jouerSon("Barrel", "Setting it up6", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 3, 5, regardFinal="Haut")
            self._etapeTraitement += 1
        if self._etapeTraitement == 18 and self._deplacementBoucle is False and self._xTile == 3 and self._yTile == 5:
            self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].ouvrirOuFermerPorte()
            self._lancerTrajet("Haut",False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 19 and self._deplacementBoucle is False and self._xTile == 3 and self._yTile == 4:
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].ouvrirOuFermerPorte()
            self._gestionnaire.ajouterEvenementATuer("concrets", "Maison", self._nom)
            self._boiteOutils.interrupteurs["BeliaRentree"].activer()
            self._etapeTraitement += 1

    def _gererSons(self):
        if self._etapeAction in self._sons.keys():
            if self._sons[self._etapeAction][2] is True:
                self._boiteOutils.jouerSon(*self._sons[self._etapeAction][0], **self._sons[self._etapeAction][1])
                self._sons[self._etapeAction][2] = False

    def _majSons(self):
        self._sons = dict()
        self._sons[0] = [["Wateragitation", "Washing clothe"], {"fixe":True, "evenementFixe":self._nom}, True]
        self._sons[14], self._sons[28] = list(self._sons[0]), list(self._sons[0])
        self._sons[6] = [["Barrel", "Taking clothe"], {"fixe":True, "evenementFixe":self._nom}, True]
        self._sons[20], self._sons[34] = list(self._sons[6]), list(self._sons[6])
        self._sons[8] = [["Washing", "Washing barrel"], {"fixe":True, "evenementFixe":self._nom}, True]
        self._sons[22], self._sons[36] = list(self._sons[8]), list(self._sons[8])
        self._sons[13], self._sons[27], self._sons[41] = list(self._sons[8]), list(self._sons[8]), list(self._sons[8])
    
class Enfant(PNJ):
    def __init__(self, jeu, gestionnaire, nom, x, y, c):
        fichier, couleurTransparente, persoCharset, vitesseDeplacement, self._nom = nom + ".png", (0,0,0), (0,0), 150, nom
        repetitionActions, directionDepart, poseDepart = True, "Gauche", True
        listeActions = ["Droite","Bas","Bas","Bas","Bas","Bas","Bas","Bas","Droite","Droite","Droite","Bas","Gauche","Gauche","Gauche","Gauche","Haut","Haut","Haut","Haut","Haut","Haut","Haut","Haut"]
        super().__init__(jeu, gestionnaire, nom, x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement, poseDepart=poseDepart)
        if self._jeu.carteActuelle.nom == "InterieurMaison" and self._boiteOutils.interrupteurs["squirrelPose"].voir() and not self._boiteOutils.interrupteurs["BeliaRentree"].voir():
            self._poseDepart = False
        elif self._jeu.carteActuelle.nom == "EtageMaison" and not self._boiteOutils.interrupteurs[self._nom+"Etage"].voir():
            self._poseDepart = False
        if y == 8:
            self._etapeAction = 20
        self._positionsSuivi, self._etapeSuivi = {"Tom":[(10,7),(7,6)], "Elie":[(10,9),(7,5)]}, 0
        self._xArrivee, self._yArrivee = -1, -1

    def _gererEtape(self):
        if self._jeu.carteActuelle.nom == "InterieurMaison":
            self._gererEtapeRDC()
        elif self._jeu.carteActuelle.nom == "EtageMaison":
            self._gererEtapeEtage()

    def _gererEtapeRDC(self):
        if self._etapeTraitement == 2 and self._deplacementBoucle is False and self._boiteOutils.interrupteurs["JoueurEntre2"].voir() is True:
            (self._xArrivee, self._yArrivee) = self._positionsSuivi[self._nom][self._etapeSuivi]
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xArrivee, self._yArrivee)
            self._comportementParticulier = True
            self._etapeTraitement += 1
            self._etapeSuivi += 1
        if self._etapeTraitement == 3 and self._deplacementBoucle is False and self._boiteOutils.interrupteurs["JoueurEntre3"].voir() is True:
            (self._xArrivee, self._yArrivee) = self._positionsSuivi[self._nom][self._etapeSuivi]
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xArrivee, self._yArrivee, regardFinal="Gauche")
            self._comportementParticulier = True
            self._etapeSuivi += 1
            self._etapeTraitement += 1
        if (self._etapeTraitement == 3 or self._etapeTraitement == 2) and self._boiteOutils.getNomPensee() == "thoughtUpstairs" and self._etapeMarche == 1:
            self._etapeTraitement = 4
            self._finirDeplacementSP()
        if (self._etapeTraitement == 2 or self._etapeTraitement == 3) and self._comportementParticulier is True and self._xTile == self._xArrivee and self._yTile == self._yArrivee and self._deplacementBoucle is False:
            self._finirDeplacementSP()
            self._comportementParticulier = False
        if self._etapeTraitement == 4 and self._etapeMarche == 1 and self._boiteOutils.getNomPensee() == "thoughtUpstairs":
            self._comportementParticulier = True
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 1, 3)
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and self._deplacementBoucle is False and self._xTile == 1 and self._yTile == 3:
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._boiteOutils.interrupteurs[self._nom+"Etage"].activer()
            self._gestionnaire.ajouterEvenementATuer("concrets", "InterieurMaison", self._nom)
            self._etapeTraitement += 1

    def _gererEtapeEtage(self):
        if self._etapeTraitement == 0 and self._jeu.carteActuelle.deplacementPossible(Rect(1*32, 3*32, 32, 32), self._c, self._nom) and self._boiteOutils.interrupteurs["squirrelPose"].voir():
            self._modifierPositionInitiale(1,3,2,"Bas")
            self._poseDepart = True
        if self._etapeTraitement == 1:
            (self._xArrivee,self._yArrivee) = (3,11) if self._nom == "Tom" else (3,10)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xArrivee, self._yArrivee)
            self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._xTile == self._xArrivee and self._yTile == self._yArrivee and self._deplacementBoucle is False:
            self._lancerTrajet(500,False)
            self._fuyard = True
            self._etapeTraitement += 1
        if self._etapeTraitement == 3 and self._deplacementBoucle is False:
            self._genererLancerTrajetAleatoire(2,2)
            if self._boiteOutils.interrupteurs["ConversationEnfants"].voir() is False and self._boiteOutils.penseeAGerer.voir() is False:
                self._boiteOutils.ajouterPensee("Are we havin' nuts for dinner tonight? Will I ever taste some meat again?", faceset="Tom.png")
                self._boiteOutils.ajouterPensee("Shhh, not so loud... He's here!", faceset="Elie.png")
                self._boiteOutils.interrupteurs["ConversationEnfants"].activer()

    def _genererRegards(self, actions):
        directions, i = [actions[len(actions)-1], self._boiteOutils.getDirectionAuHasard()], 1
        while i < len(directions):
            while directions[i] == directions[i-1]:
                directions[i] = self._boiteOutils.getDirectionAuHasard()
            i += 1
        directions = directions[1:]
        directions = [f(direction) for direction in directions for f in (lambda direction: 500, lambda direction: "R"+direction)] + [500]
        return actions + directions

    def _genererLancerTrajetAleatoire(self, longueurMin, longueurMax, regards=True):
        i, actions = 0, []
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
        if regards:
            actions = self._genererRegards(actions)
        self._lancerTrajet(actions, False)
        Horloge.initialiser(id(self), 1, 1)

class MembreFamille(PNJ):
    """Pattern decorator pour tous les membres de la famille : quelques comportements communs."""
    def __init__(self, pnj):
        self._pnj, self._comportementParticulier = pnj, False

    def __setattr__(self, attribut, valeur):
        if attribut == "_pnj":
            self.__dict__[attribut] = valeur
        else:
            self._pnj.__dict__[attribut] = valeur

    def __getattr__(self, attribut):
        if attribut == "_pnj":
            return self.__dict__[attribut]
        else:
            return getattr(self._pnj, attribut)

    def _gererEtape(self):
        if self._etapeTraitement == 1 and (self._etapeMarche == 1 or "V" in self._listeActions[self._etapeAction]) and self._boiteOutils.interrupteurs["JoueurEntre"].voir() is True:
            self._finirDeplacementSP()
            self._lancerTrajet(self._boiteOutils.regardVersPnj("Joueur",-1,-1,evenementReference=self._nom),False)
            self._etapeTraitement += 1
        if (self._etapeTraitement == 2 or self._etapeTraitement == 3) and self._comportementParticulier is False:
            self._majInfosJoueur()
            if self._joueurBouge[0] is True:
                self._lancerTrajet(self._boiteOutils.regardVersPnj("Joueur",-1,-1,evenementReference=self._nom),False)
        self._pnj._gererEtape()

class TableSquirrel(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._ecureuilPose = False

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._ecureuilPose is False:
            self._ecureuilPose = True
            self._jeu.carteActuelle.poserPNJ(Rect(5 * 32, 5 * 32, 32, 32), 3, Rect(0,0,32,32),  "squirrelDead.png", (0,0,0), "tableSquirrel")
            self._boiteOutils.interrupteurs["squirrelPose"].activer()

class SignaleurJoueur(Evenement):
    def __init__(self, jeu, gestionnaire, *parametres):
        Evenement.__init__(self, jeu, gestionnaire)
        self._signaleurs = dict()
        for parametre in parametres:
            self.ajouterSignaleur(parametre[0], parametre[1], parametre[2])

    def ajouterSignaleur(self, carte, interrupteur, position):
        if carte not in self._signaleurs.keys():
            self._signaleurs[carte] = dict()
        self._signaleurs[carte][position] = interrupteur

    def traiter(self):
        self._majInfosJoueur()
        if self._jeu.carteActuelle.nom in self._signaleurs.keys():
            if self._joueurBouge[0] and (self._xJoueur[0], self._yJoueur[0]) in self._signaleurs[self._jeu.carteActuelle.nom].keys():
                nomInterrupteur = self._signaleurs[self._jeu.carteActuelle.nom][self._xJoueur[0], self._yJoueur[0]]
                self._boiteOutils.interrupteurs[nomInterrupteur].activer()
                print(nomInterrupteur)
                self._signaleurs[self._jeu.carteActuelle.nom].pop((self._xJoueur[0], self._yJoueur[0]))

