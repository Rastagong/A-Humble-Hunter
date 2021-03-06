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
if SESSION_DEBUG:
    import pdb

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
        self._messageBoutonInteraction, self._premiereMortChasse, self._traitement, etapeMax, i = False, False, dict(), 55, 0 
        self._penseeMaisonGods = False
        while i <= etapeMax:
            self._traitement[i] = getattr(self, "_traiter"+str(i)) #On référence les fonctions de traitement dans un dico : elles ont pour nom _traiter0, _traiter1...
            i += 1
        ###
        if LANCEMENT_ULTERIEUR:
            etapeLancementUlterieur = {"EtageMaison":23, "Entree Maison Gods":35, "Last Dream":49}
            self._setDepart, self._etape = False, etapeLancementUlterieur[NOM_CARTE_LANCEMENT]

    def traiter(self):
        etapeActuelle = self._etape
        self._traitement[self._etape]()
        while etapeActuelle < self._etape:
            etapeActuelle = self._etape
            self._traitement[self._etape]()

    def _traiter0(self):
        self._boiteOutils.jouerSon("sonsForet", "boucleSonsForet", nombreEcoutes=0, volume=VOLUME_MUSIQUE/5)
        self._boiteOutils.ajouterPensee("It was early spring in the woods and the snow had melted, at last. I could hunt again.")
        self._boiteOutils.ajouterPensee("It was more than time. Winter had been harsh. No more food, no more money.")
        self._boiteOutils.ajouterPensee("We were almost starving.")
        self._boiteOutils.ajouterTransformation(True, "Alpha", alpha=self._coefNoircisseur)
        self._coordonneesJoueur = self._boiteOutils.getCoordonneesJoueur()
        Horloge.initialiser(id(self), "TempsDecouverte", 20000)
        Horloge.initialiser(id(self), "Alpha", 100)
        self._etape += 1

    def _traiter1(self):
        if Horloge.sonner(id(self), "Alpha"):
            self._coefNoircisseur += 7
            if self._coefNoircisseur > 255:
                self._coefNoircisseur = 255
            self._boiteOutils.ajouterTransformation(True, "Alpha", alpha=self._coefNoircisseur)
            if self._coefNoircisseur == 255:
                self._boiteOutils.retirerTransformation(True, "Alpha")
                self._etape += 1
            else:
                Horloge.initialiser(id(self), "Alpha", 100)

    def _traiter2(self):
        if self._boiteOutils.interrupteurs["DecouverteSquirrels"].voir():
            Horloge.initialiser(id(self), "SplashArrow", 3000)
            self._etape += 1

    def _traiter3(self):
        if Horloge.sonner(id(self), "SplashArrow"):
            self._boiteOutils.ajouterTransformation(True, "SplashText Arrow", texte="Press X to shoot an arrow", antialias=True, couleurTexte=(255,255,255), position=(10, 10), taille=30, alpha=self._alpha)
            self._etape += 1

    def _traiter4(self):
        if self._messageBoutonInteraction is False and self._premiereMortChasse is True:
            self._messageBoutonInteraction = True
            self._boiteOutils.retirerTransformation(True, "SplashText Arrow")
            self._boiteOutils.ajouterTransformation(True, "SplashText Interaction1", texte="Press Z to interact", antialias=True, couleurTexte=(255,255,255), position=(10, 10), taille=30, alpha=self._alpha)
            self._boiteOutils.ajouterTransformation(True, "SplashText Interaction2", texte="Or W on an AZERTY keyboard", antialias=True, couleurTexte=(255,255,255), position=(10, 40), taille=20, alpha=self._alpha)
            self._gestionnaire.evenements["abstraits"]["GestionnaireAnimaux"].nombre["SquirrelMinimal"] = 0 #On ne restaure plus les écureuils...
            self._gestionnaire.evenements["abstraits"]["GestionnaireAnimaux"].restaurerMortsParFuite = True #Sauf quand ils meurent par fuite
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
            self._boiteOutils.ajouterPensee("I've never had any luck in these woods. Never.")
            self._etape += 1
        if self._boiteOutils.variables["SquirrelChasses"] == 3 and self._etape == 6:
            self._boiteOutils.ajouterPensee("Truly, the gods haven't been fair with the humble hunter I am...")
            Horloge.initialiser(id(self), "tempsFinChasse", 20000)
            self._coordonneesJoueur = self._boiteOutils.getCoordonneesJoueur()
            self._etape += 1

    def _traiter5(self):
        self._traiter4()

    def _traiter6(self):
        self._traiter4()

    def _traiter7(self):
        if Horloge.sonner(id(self), "tempsFinChasse") or self._boiteOutils.deplacementConsequentJoueur(self._coordonneesJoueur, 20):
            self._boiteOutils.ajouterPensee("It seems we won't eat tonight either, there's nothing left to hunt. I should go home.")
            self._boiteOutils.interrupteurs["finChasse1"].activer()
            self._etape += 1

    def _traiter8(self):
        if self._boiteOutils.getCoordonneesJoueur() == (13,3):
            self._boiteOutils.arreterSonEnFondu("boucleSonsForet", 3000)
            self._boiteOutils.interrupteurs["escalierLibre"].activer()
            self._boiteOutils.arreterSonEnFondu("Musique forêt meadows", 3000)
            self._boiteOutils.interrupteurs["Rires"].activer()
            self._etape += 1

    def _traiter9(self):
        if self._boiteOutils.getCoordonneesJoueur() == (11,13) or self._boiteOutils.getCoordonneesJoueur() == (11,14):
            self._boiteOutils.interrupteurs["Rires"].desactiver()
            self._boiteOutils.ajouterPensee("They froze when they saw me. They wanted to see what I'd caught.")
            self._boiteOutils.interrupteurs["JoueurEntre"].activer()
            self._gestionnaire.evenements["abstraits"]["SignaleurJoueur"].ajouterSignaleur("InterieurMaison", "JoueurEntre2", (10,4))
            self._gestionnaire.evenements["abstraits"]["SignaleurJoueur"].ajouterSignaleur("InterieurMaison", "JoueurEntre3", (6,4))
            Horloge.initialiser(id(self), "Attente squirrelPose", 15000)
            self._etape += 1

    def _traiter10(self):
        if Horloge.sonner(id(self), "Attente squirrelPose") and not self._boiteOutils.interrupteurs["squirrelPose"].voir():
            self._boiteOutils.ajouterTransformation(True, "SplashText InteractionTable1", texte="Press Z to interact with the table", antialias=True, couleurTexte=(255,255,255), position=(10, 10), taille=30, alpha=self._alpha)
            self._boiteOutils.ajouterTransformation(True, "SplashText InteractionTable2", texte="Or W on an AZERTY keyboard", antialias=True, couleurTexte=(255,255,255), position=(10, 40), taille=20, alpha=self._alpha)
        if self._boiteOutils.interrupteurs["squirrelPose"].voir() is True:
            self._boiteOutils.ajouterPensee("I'm sorry... I only got squirrels...", faceset="Chasseur.png")
            self._boiteOutils.ajouterPensee("Tom, Elie, go play upstairs.", nom="thoughtUpstairs", faceset="Belia.png")
            self._boiteOutils.ajouterPensee("Let's talk outside. I must wash some clothes anyway.", nom="thoughtOutside", faceset="Belia.png")
            self._boiteOutils.jouerSon("Osare Unrest Middle", "Thème familier", volume=VOLUME_LONGUE_MUSIQUE, nombreEcoutes=0)
            self._boiteOutils.retirerTransformation(True, "SplashText InteractionTable1")
            self._boiteOutils.retirerTransformation(True, "SplashText InteractionTable2")
            Horloge.initialiser(id(self), "Rires Upstairs", 6000)
            self._etape += 1

    def _traiter11(self):
        if Horloge.sonner(id(self), "Rires Upstairs"):
            self._boiteOutils.jouerSon("Laugh", "Rires")
            self._etape += 1

    def _traiter12(self):
        if self._boiteOutils.interrupteurs["discussionEtang"].voir():
            self._boiteOutils.ajouterPensee("We'll have to fetch some nuts for the children,", faceset="Belia.png")
            self._boiteOutils.ajouterPensee("you should shake down the oak trees.", faceset="Belia.png")
            i, positions = 0, [(12,2),(7,4),(5,9),(20,10),(23,12),(19,14),(7,15),(15,17),(7,19)]
            while i < 9:
                self._gestionnaire.evenements["concrets"]["Maison"]["Chene"+str(i)]=[Chene(self._jeu, self._gestionnaire, positions[i][0], positions[i][1], i), positions[i], "Aucune"]
                i += 1
            self._etape += 1

    def _traiter13(self):
        if self._boiteOutils.penseeAGerer.voir() is False:
            Horloge.initialiser(id(self), "Discussion attente", 15000)
            self._etape += 1

    def _traiter14(self):
        if Horloge.sonner(id(self), "Discussion attente"):
            self._boiteOutils.ajouterPensee("How many hares have you seen today?", faceset="Belia.png")
            self._boiteOutils.ajouterPensee("None. These woods are almost inhabited.", faceset="Chasseur.png")
            self._boiteOutils.ajouterPensee("I don't know what to do. We can't even harvest our crops yet.", faceset="Belia.png")
            self._etape += 1

    def _traiter15(self):
        if self._penseePossible.voir():
            Horloge.initialiser(id(self), "Discussion attente", 15000)
            self._etape += 1

    def _traiter16(self):
        if Horloge.sonner(id(self), "Discussion attente"):
            self._boiteOutils.ajouterPensee("There might be one solution, but I dread to think of it..", faceset="Chasseur.png")
            self._boiteOutils.ajouterPensee("I've never been in the heart of the forest. The path is long,", faceset="Chasseur.png")
            self._boiteOutils.ajouterPensee("the Old Door is locked, but who knows what kind of game I could find there.", faceset="Chasseur.png")
            self._boiteOutils.ajouterPensee("Don't you think about it. No man, hunter or prince, dares to enter there.", faceset="Belia.png")
            self._boiteOutils.ajouterPensee("But I could try. At least to know whether the old tales are true.", faceset="Chasseur.png")
            self._boiteOutils.ajouterPensee("Things will get better, we shouldn't complain. Be thankful and pray the gods.", faceset="Belia.png")
            self._etape += 1

    def _traiter17(self):
        if self._boiteOutils.interrupteurs["BeliaRentree"].voir():
            self._boiteOutils.ajouterPensee("Praying the gods? Praying the gods?")
            self._boiteOutils.ajouterPensee("I'd been praying them for years... What had they granted me?")
            self._etape += 1

    def _traiter18(self):
        self._etape += 1

    def _traiter19(self):
        if self._boiteOutils.interrupteurs["nutsOnTable"].voir():
            self._boiteOutils.ajouterPensee("I threw the nuts on the table and I went straight to bed.")
            self._etape += 1

    def _traiter20(self):
        if self._boiteOutils.getCoordonneesJoueur() in [(7,3), (8,3), (9,3)]:
            self._coefNoircisseur = 1
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
            self._boiteOutils.joueurLibre.desactiver()
            self._boiteOutils.arreterSonEnFondu("Thème familier", 3000)
            Horloge.initialiser(id(self), "Transition Noir", 1)
            self._etape += 1

    def _traiter21(self):
        if Horloge.sonner(id(self), "Transition Noir"):
            self._coefNoircisseur += 1
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
            if self._coefNoircisseur == 12:
                self._etape += 1
                self._boiteOutils.ajouterPensee("Truly, the gods haven't been fair with the humble hunter I am...", vitesse=60)
                self._boiteOutils.arreterSonEnFondu("Osare Unrest Middle", 3000)
                self._boiteOutils.interrupteurs["escalierLibre"].desactiver()
            else:
                Horloge.initialiser(id(self), "Transition Noir", 100)

    def _traiter22(self):
        self._gestionnaire.envoyerNotificationEvenement("Narrateur", "Belia", "InterieurMaison", "Nuit étage", x=9, y=3)
        self._gestionnaire.envoyerNotificationEvenement("Narrateur", "Tom", "InterieurMaison", "Nuit étage", x=13, y=3)
        self._gestionnaire.envoyerNotificationEvenement("Narrateur", "Elie", "InterieurMaison", "Nuit étage", x=13, y=7)
        self._etape += 1

    def _traiter23(self):
        if LANCEMENT_ULTERIEUR:
            self._coefNoircisseur = 12
        if self._penseePossible.voir():
            self._boiteOutils.teleporterJoueurSurPosition(7, 3, "Bas")
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur, permanente=True)
            self._boiteOutils.jouerSon("Forest Night", "It's the night", nombreEcoutes=0, volume=0.7)
            Horloge.initialiser(id(self), "Transition Noir", 1000)
            self._boiteOutils.joueurLibre.activer()
            self._etape += 1

    def _traiter24(self):
        if Horloge.sonner(id(self), "Transition Noir"):
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur, permanente=True)
            self._coefNoircisseur -= 1
            if self._coefNoircisseur == 8:
                self._etape += 1
                Horloge.initialiser(id(self), "Door creak", 700)
            else:
                Horloge.initialiser(id(self), "Transition Noir", 1000)

    def _traiter25(self):
        if Horloge.sonner(id(self), "Door creak"):
            self._boiteOutils.jouerSon("DoorCreak", "Someone enters")
            Horloge.initialiser(id(self), "Someone enters", 5000)
            self._etape += 2

    def _traiter26(self):
        if Horloge.sonner(id(self), "Someone walks"):
            #self._boiteOutils.jouerSon("WoodenSteps", "Someone walks", nombreEcoutes=3)
            self._etape += 1

    def _traiter27(self):
        if Horloge.sonner(id(self), "Someone enters") and self._jeu.carteActuelle.nom == "EtageMaison":
            self._gestionnaire.evenements["concrets"]["EtageMaison"]["DuckGod"] = [DuckGod(self._jeu, self._gestionnaire, 1, 3, 2, "Bas"), (1,3), "Bas"]
            self._gestionnaire.ajouterChangementCarteANotifier("InterieurMaison", "Maison Dream", "Narrateur", "abstrait")
            self._etape += 1

    def _traiter28(self):
        if self._gestionnaire.nomCarte == "Maison Dream":
            self._boiteOutils.ajouterTransformation(True, "Fog", permanente=True)
            self._boiteOutils.jouerSon("Eerie", "Morning Dream", nombreEcoutes=0, volume=0.4)
            Horloge.initialiser(id(self), "fogRises", 1)
            self._alphaFog = 150
            self._etape += 1

    def _traiter29(self):
        if self._boiteOutils.interrupteurs["fogRises"].voir() and Horloge.sonner(id(self), "fogRises"):
            self._alphaFog += 1
            self._boiteOutils.ajouterTransformation(True, "Fog", permanente=True, alpha=self._alphaFog, minorChange=True)
            Horloge.initialiser(id(self), "fogRises", 10)
            if self._alphaFog == 250:
                self._boiteOutils.interrupteurs["fogRises"].desactiver()
                Horloge.initialiser(id(self), "Full fog", 5000)
                self._etape += 1

    def _traiter30(self):
        if Horloge.sonner(id(self), "Full fog"):
            self._alphaFog -= 1
            self._boiteOutils.ajouterTransformation(True, "Fog", permanente=True, alpha=self._alphaFog, minorChange=True)
            Horloge.initialiser(id(self), "Full fog", 10)
            if self._alphaFog == 150:
                Horloge.initialiser(id(self), "Player lost", 10000)
                self._etape += 1

    def _traiter31(self):
        if Horloge.sonner(id(self), "Player lost"):
            self._gestionnaire.evenements["concrets"]["Maison Dream"]["Crow"] = [Crow(self._jeu, self._gestionnaire, 83, 10, 2, "Bas"), (0,0), "Bas"]
            self._etape += 1

    def _traiter32(self):
        if self._gestionnaire.xJoueur == 166 and self._gestionnaire.yJoueur == 34:
            self._boiteOutils.interrupteurs["JoueurVuWizards"].activer()
            Horloge.initialiser(id(self), "Wizards disappear", 2000)
            self._boiteOutils.jouerSon("WoodenHit", "WoodenHit")
            self._etape += 1

    def _traiter33(self):
        if Horloge.sonner(id(self), "Wizards disappear"):
            Horloge.initialiser(id(self), "Fog change", 1)
            self._boiteOutils.jouerSon("Woosh", "Woosh wizards disappear", volume=0.75)
            self._fogChange, self._alphaFog = 1, 150
            self._etape += 1

    def _traiter34(self):
        if Horloge.sonner(id(self), "Fog change"):
            self._alphaFog += self._fogChange
            self._boiteOutils.ajouterTransformation(True, "Fog", permanente=True, alpha=self._alphaFog, minorChange=True)
            Horloge.initialiser(id(self), "Fog change", 10)
            if self._alphaFog == 250:
                self._boiteOutils.interrupteurs["Wizards disappear"].activer()
                self._fogChange = -1
            if self._alphaFog == 150 and self._fogChange == -1:
                self._etape += 1
                Horloge.initialiser(id(self), "Tea time1",1)
                Horloge.initialiser(id(self), "Tea time2",1)
            self._boiteOutils.interrupteurs["RetourDuckGod"].activer()
            self._boiteOutils.interrupteurs["MusiqueThe"].activer()

    def _traiter35(self):
        if LANCEMENT_ULTERIEUR:
            Horloge.initialiser(id(self), "Tea time1",1)
            Horloge.initialiser(id(self), "Tea time2",1)
            self._boiteOutils.interrupteurs["MusiqueThe"].activer()
        if self._gestionnaire.nomCarte == "Maison Gods":
            if self._penseeMaisonGods is False:
                Horloge.initialiser(id(self), "Pensée Maison Gods", 2000)
                self._penseeMaisonGods = True
            if Horloge.sonner(id(self), "Pensée Maison Gods"):
                self._boiteOutils.ajouterPensee("Where the hell???")
            if self._gestionnaire.xJoueur == 57 and self._gestionnaire.yJoueur == 31:
                self._boiteOutils.interrupteurs["DébutConversation"].activer()
                self._boiteOutils.ajouterPensee("...which is why I find his opinions undoubtedly distasteful.", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("Mistaking me for a Lord of the lakes, really. What a lack of consideration.", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("Was I to lose my honour, I'd rather have chosen the skies.", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("Actually, I do understand his mistake. Just have look at you for a minute:", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("feathers, beak, wings... There isn't much difference between us!", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("Now how dare you, Sir Duck?", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("I say, aren't we both ruling over the forests of the Middle South?", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("Well, I can't state otherwise...", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("Well, my dear, we could both rule over the Marine Realms.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("I'm myself continuously mistaken for a Lord of the sea,", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("even though it should be common knowledge that I daren't leave my pond.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("It has nothing to do with my current situation!", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("Surely, you've never seen Sir Falcon mistaken for Sir Salmon!", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("I'll grant you that.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("Then tell me for which reason I don't deserve the same rank and dignity.", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("See, there's a wide range of worthiness between the crow and the falcon.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("A wide range of worthiness, really?", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("A wide range, indeed. You're nowhere as majestic.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("I'm very sorry to interrupt your argument, which is delightful to hear...", faceset="WizardGod.png")
                self._boiteOutils.ajouterPensee("But I've brought biscuits. Now please continue. I enjoy it. I'll join you soon.", faceset="WizardGod.png")
                self._boiteOutils.ajouterPensee("Well, thank you very much, Sir Wizard.", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("Learn, my friend, that our respective worthiness don't relie on the same qualities:", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("While Sir Falcon is respected for his majestic windspan, I, Sir Crow,", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("am feared by both men and fairies, for the news I bring truly are terrible.", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("This, my friend, used to be true in our youth, centuries ago.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("Nowadays most men have completely forgotten the fear you inspired them.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("Would you venture into a city, would they certainly try to have you roasted.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("Roasted, really? The taste of men hasn't improved with time.", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("Would they try to do so, you do know what would happen to them.", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("Well, I sure do! But they don't. That's the problem of our times.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("I'm glad we still have the men of the countryside and of the forests.", faceset="Crow.png")
                self._boiteOutils.ajouterPensee("I sure am too.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("Won't you come with us, Sir Wizard? We're eating your biscuits.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("Not many will remain.", faceset="DuckGod.png")
                self._boiteOutils.ajouterPensee("I'm almost done by now, please don't worry about me.", faceset="WizardGod.png")
                self._etape += 1

    def _gererSonsThe(self):
        if self._boiteOutils.interrupteurs["MusiqueThe"].voir() is True:
            if self._etape != 39:
                if Horloge.sonner(id(self), "Tea time1"):
                    self._boiteOutils.jouerSon("BruitsRepas", "Bruits repas Gods1", fixe=True, xFixe=71, yFixe=42)
                    Horloge.initialiser(id(self), "Tea time1", random.randint(3000,10000))
                if Horloge.sonner(id(self), "Tea time2"):
                    self._boiteOutils.jouerSon("BruitThe", "Bruits repas Gods2", fixe=True, xFixe=71, yFixe=42)
                    Horloge.initialiser(id(self), "Tea time2", random.randint(10000,20000))
            else:
                pass

    def _traiter36(self):
        self._gererSonsThe()
        if self._gestionnaire.xJoueur == 60 and self._gestionnaire.yJoueur == 35:
            fermerPorte(self._boiteOutils, 60, 37)
            self._etape += 1

    def _traiter37(self):
        self._gererSonsThe()
        if self._gestionnaire.yJoueur == 40:
            self._boiteOutils.ajouterPensee(".........", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("Sir Duck, surely there has to be a misunderstanding on the guest.", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("Does it? To be honest, I don't really see how.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("Where to begin? Firstly, this is a man. Secondly, he shouldn't be here.", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("I passed by him earlier. I thought the witches had taken care of him.", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("Well, he found his way around as expected. I'm glad.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("Yes, I did visit him in his dream and then led him there.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("So you felt the urgent need to invite a man for tea without announcing him.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("Absolutely, Sir Wizard. I found his story quite distracting, you'll see.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("But let's all sit first. Music!", faceset="DuckGod.png")
            self._etape += 1

    def _traiter38(self):
        self._gererSonsThe()
        if self._penseePossible.voir():
            self._boiteOutils.interrupteurs["DialogueVisiteur"].activer()
            self._boiteOutils.interrupteurs["MusiqueThe"].activer()
            self._placesDisponibles = [(69,42), (69,43), (73,43)]
            self._etape += 1

    def _traiter39(self):
        self._gererSonsThe()
        if (self._gestionnaire.xJoueur,self._gestionnaire.yJoueur) in self._placesDisponibles and self._boiteOutils.interrupteurs["GodsAssis"].voir() is True:
            self._boiteOutils.ajouterPensee("So what are we to do with this peasant?", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("He is a hunter. And he lives on our very own lands, Sir Crow,", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("in the Realm of the Forest. He's been there for years.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("That certainly is unusual. I'm astonished by this peasant of yours.", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("I'll just ignore you, you know. The thing is, he has a funny claim.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("He believes “we haven't been fair with the humble hunter he is”.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("We haven't been fair with him, really? Today's men have become insulting.", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("Can such a daring man be as humble as he believes he is?", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("Quite funny, isn't it? I knew he would amuse you.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("“Amuse” isn't quite the word, but he certainly is original.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("It isn't a very probing reason to bring a stranger at my home though.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("It isn't, indeed! Shall we punish him? I'd like to see him swim in lava.", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("Actually, I wondered whether we couldn't assist him.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("In what honour should we alter the fate of a mortal?", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("In the name of charity. He deserves it.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("This hunter is born poor, and is likely to die poor as well.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("Sir Duck, I don't even understand you.", faceset="Crow.png")
            self._boiteOutils.ajouterPensee("Nonsense, Sir Duck. You do know we mustn't intervene arbitrarily.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("Still, this man believes in our existence. That's rare in our modern world.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("I don't care, Sir Duck. And as Lord Master of the Forest Realm,", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("I hereby sentence him to become my man-servant in this dream, forever.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("But...", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("Enough. I've spoken. Let's drink. Oh, there's almost nothing left.", faceset="WizardGod.png")
            self._etape += 1

    def _traiter40(self):
        if self._penseePossible.voir():
            if self._boiteOutils.interrupteurs["NouvelleMission"].voir() is False:
                self._boiteOutils.ajouterPensee("Now “humble” hunter, come here, will you? I've got work for you.", faceset="WizardGod.png")
            else:
                self._boiteOutils.ajouterPensee("Humble hunter, I need your help again.", faceset="WizardGod.png")
            self._boiteOutils.interrupteurs["JoueurOrdreTea"].activer()
            self._etape += 1

    def _traiter41(self):
        if self._boiteOutils.interrupteurs["MissionTerminee"].voir() is True:
            if self._boiteOutils.variables["TeaGiven"] == "Green":
                self._etape += 1
            elif self._boiteOutils.variables["TeaGiven"] == "Blue":
                self._boiteOutils.interrupteurs["MissionTerminee"].desactiver()
                self._boiteOutils.interrupteurs["JoueurOrdreTea"].desactiver()
                self._boiteOutils.interrupteurs["JoueurServiteur"].desactiver()
                self._boiteOutils.interrupteurs["TeaServed"].desactiver()
                self._boiteOutils.interrupteurs["TeapotFilled"].desactiver()
                self._boiteOutils.interrupteurs["NouvelleMission"].activer()
                self._boiteOutils.variables["TeaGiven"] = None
                Horloge.initialiser(id(self), "Nouvelle mission", 12000)
        elif Horloge.sonner(id(self), "Nouvelle mission"):
            self._etape = 40

    def _traiter42(self):
        self._gererSonsThe()
        self._boiteOutils.ajouterPensee("I say, this lime-flower tea has a unique savour.", faceset="DuckGod.png")
        self._boiteOutils.ajouterPensee("Surprisingly, I do agree! Where did you find the flowers? Millenial tree?", faceset="Crow.png")
        self._boiteOutils.ajouterPensee("Something disturbs me... This is no lime-... Oh no, he didn't.", faceset="WizardGod.png", tempsLecture=0)
        self._etape += 1

    def _traiter43(self):
        if self._penseePossible.voir():
            self._boiteOutils.arreterSonEnFondu("Tea Music", 3000)
            self._boiteOutils.interrupteurs["MusiqueThe"].desactiver()
            self._gestionnaire.evenements["concrets"]["Maison Gods"]["Bruiteur"][0]._pause = False
            self._boiteOutils.interrupteurs["ParalysieGods1"].activer()
            self._boiteOutils.ajouterPensee("Well played, clever hunter, well played.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("He served us some Devil Tea from the Heart of the Forest.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("I use it, well to fool the unsuspecting men I encounter and punish them.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("I'm afraid we won't be able to move or speak for a whi... ", faceset="WizardGod.png", tempsLecture=0)
            self._etape += 1

    def _traiter44(self):
        if self._penseePossible.voir():
            self._boiteOutils.interrupteurs["ParalysieGods2"].activer()
            self._etape += 1

    def _traiter45(self):
        if self._boiteOutils.interrupteurs["CakeEaten"].voir() is True and self._gestionnaire.yJoueur == 35 and self._gestionnaire.xJoueur >= 83:
            self._boiteOutils.joueurLibre.desactiver()
            self._coefNoircisseur = 1
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
            Horloge.initialiser(id(self), "Noir", 100)
            self._etape += 1

    def _traiter46(self):
        if Horloge.sonner(id(self), "Noir"):
            self._coefNoircisseur += 1
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
            Horloge.initialiser(id(self), "Noir", 100)
            if self._coefNoircisseur == 12:
                self._etape += 1

    def _traiter47(self):
        self._boiteOutils.ajouterPensee("So I fell asleep, and left this dream, at last...")
        self._etape += 1

    def _traiter48(self):
        if self._penseePossible.voir():
            self._boiteOutils.teleporterSurCarte("Last Dream", 8, 96, 2, "Bas")
            Horloge.initialiser(id(self), "Noir", 1)
            self._etape += 1

    def _traiter49(self):
        if LANCEMENT_ULTERIEUR and self._setDepart is False:
            Horloge.initialiser(id(self), "Noir", 1)
            self._coefNoircisseur, self._setDepart = 12, True
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
        if self._gestionnaire.nomCarte == "Last Dream" and Horloge.sonner(id(self), "Noir"):
            self._boiteOutils.joueurLibre.activer()
            self._boiteOutils.ajouterTransformation(True, "Fog")
            self._coefNoircisseur -= 1
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
            if self._coefNoircisseur == 1:
                self._boiteOutils.retirerTransformation(True, "Noir")
                self._etape += 1
            else:
                Horloge.initialiser(id(self), "Noir", 100)

    def _traiter50(self):
        self._boiteOutils.jouerSon("Crow Call", "Crow Call")
        self._boiteOutils.ajouterPensee("I'm still here. You can't see me but I'm watching you.", faceset="Crow.png")
        self._boiteOutils.ajouterPensee("Did you really think you could leave us like this?", faceset="Crow.png")
        self._boiteOutils.ajouterPensee("You've impressed me, humble hunter. I offer you a gift.", faceset="Crow.png")
        self._boiteOutils.ajouterPensee("Take that key. It will open the door to the Heart of the Forest.", faceset="Crow.png")
        self._boiteOutils.ajouterPensee("You'll find something hidden there. An ancient weapon.", faceset="Crow.png")
        self._boiteOutils.ajouterPensee("If you truly are as humble as you claim to be,", faceset="Crow.png")
        self._boiteOutils.ajouterPensee("You'll never be hungry again. But be careful.", faceset="Crow.png")
        self._boiteOutils.ajouterPensee("If you ever befriend the people from the Northern Plains,", faceset="Crow.png")
        self._boiteOutils.ajouterPensee("then you are truly lost. I'll be watching you. Good luck.", faceset="Crow.png")
        self._etape += 1

    def _traiter51(self):
        if self._penseePossible.voir() and self._gestionnaire.yJoueur == 2 and (self._gestionnaire.xJoueur >= 7 and self._gestionnaire.xJoueur <= 9) and self._boiteOutils.interrupteurs["KeyForestFound"].voir() is True:
            self._coefNoircisseur = 1
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
            Horloge.initialiser(id(self), "Noir", 100)
            self._etape += 1

    def _traiter52(self):
        if Horloge.sonner(id(self), "Noir"):
            self._coefNoircisseur += 1
            self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
            if self._coefNoircisseur == 12:
                self._boiteOutils.teleporterSurCarte("EtageMaison", 6, 3, 2, "Bas")
                self._etape += 1
            else:
                Horloge.initialiser(id(self), "Noir", 100)

    def _traiter53(self):
        if self._gestionnaire.nomCarte == "EtageMaison":
            self._boiteOutils.retirerTransformation(True, "Noir")
            self._boiteOutils.retirerTransformation(True, "Fog")
            self._boiteOutils.joueurLibre.activer()
            Horloge.initialiser(id(self), "Retour Maison", 3000)
            self._etape += 1

    def _traiter54(self):
        if Horloge.sonner(id(self), "Retour Maison"):
            self._boiteOutils.ajouterPensee("I was home, at last.")
            self._etape += 1

    def _traiter55(self):
        pass

    def onMortAnimal(self, typeAnimal, viaChasse=False):
        if viaChasse and not self._premiereMortChasse:
            self._premiereMortChasse = True

    def onChangementCarte(self, carteQuittee, carteEntree):
        if carteQuittee == "InterieurMaison" and carteEntree == "Maison Dream":
            self._boiteOutils.enleverInstanceSon("", "It's the night")

class DuckGod(PNJ):
    def __init__(self, jeu, gestionnaire, x, y, c, directionDepart):
        super().__init__(jeu, gestionnaire, "DuckGod", x, y, c, "DuckGod.png", (0,0,0), (0,0), False, ["Aucune"], directionDepart=directionDepart,vitesseDeplacement=50, eau=True)
        self._positionSource = Rect(0,0,24,26)
        i, self._traitement = 1, dict()
        while i <= 17:
            self._traitement[i] = getattr(self, "_gererEtape" + str(i))
            i += 1
        self._surPlace, self._poursuiteJoueur, self._attenteJoueur, self._premierMouvementJoueur = False, False, False, False
        ###
        if LANCEMENT_ULTERIEUR is True:
            etapeLancementUlterieur = {"Entree Maison Gods":15}
            self._etapeTraitement = etapeLancementUlterieur.get(NOM_CARTE_LANCEMENT, 0) 
    
    def _ajusterPositionSource(self, enMarche, direction):
        self._positionSource.left, self._positionSource.top = 0, 0
        if self._surPlace:
            self._positionSource.left += 24 * 4
        if "Bas" in direction:
            pass
        elif "Gauche" in direction:
            self._positionSource.top = 1 * 26
        elif "Haut" in direction:
            self._positionSource.top = 2 * 26
        elif "Droite" in direction:
            self._positionSource.top = 3 * 26
        self._positionSource.left += (self._etapeAnimation-1) * 24

    def _determinerAnimation(self, surPlace=False):
        if self._surPlace != surPlace:
            self._etapeAnimation = 1
        self._surPlace = surPlace
        if Horloge.sonner(id(self), 2) or self._surPlace:
            self._etapeAnimation += 1
            if self._etapeAnimation > 4:
                self._etapeAnimation = 1
            Horloge.initialiser(id(self), 2, self._dureeAnimation)
            return True
        else:
            return False

    def onChangementCarte(self, carteQuittee, carteEntree):
        if carteQuittee == "EtageMaison" and carteEntree == "InterieurMaison":
            self._finirDeplacementSP()
            self._deplacerSurCarte("InterieurMaison", 1, 3, 2, "Bas")
            self._poseDepart = False
            self._etapeTraitement += 1
        elif carteQuittee == "InterieurMaison" and carteEntree == "Maison Dream":
            self._finirDeplacementSP()
            self._poseDepart, self._etapeTraitement = False, 7
            self._transformationBrouillard()
            self._deplacerSurCarte("Maison Dream", 3, 5, 2, "Bas")

    def _transformationBrouillard(self):
        self._boiteOutils.ajouterTransformation(True, "Fog", permanente=True)
        self._boiteOutils.retirerTransformation(True, "Noir")
        self._boiteOutils.retirerTransformation(True, "Glow")

    def _gererEtape(self):
        etapeActuelle = self._etapeTraitement
        self._traitement[self._etapeTraitement]()
        while etapeActuelle < self._etapeTraitement:
            etapeActuelle = self._etapeTraitement
            self._traitement[self._etapeTraitement]()

    def _gererEtape1(self):
        self._boiteOutils.ajouterTransformation(True, "Glow", nomPNJ="DuckGod", couche=2, permanente=True)
        self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 8, 10, regardFinal="Haut")
        self._etapeTraitement += 1

    def _gererEtape2(self):
        if not self._poursuiteJoueur and not self._attenteJoueur and self._xTile == 8 and self._yTile == 10 and not self._deplacementBoucle:
            self._attendreJoueur()
        elif Horloge.sonner(id(self), "Attente joueur"):
            self._etapeTraitement += 1
        elif self._poursuiteJoueur and self._joueurProche and self._deplacementBoucle is False:
            self._attendreJoueur()
        if self._etapeMarche == 1 or self._listeActions[self._etapeAction][0] == "V":
            self._majInfosJoueur()
            horsChambre = False
            if self._yJoueur[0] >= 10 or self._xJoueur[0] <= 2 or self._xJoueur[0] >= 11:
                horsChambre = True
            if (self._joueurBouge[0] and self._premierMouvementJoueur) or (horsChambre and not self._premierMouvementJoueur):
                self._premierMouvementJoueur = True
                self._poursuivreJoueur()

    def _poursuivreJoueur(self):
        self._poursuiteJoueur, self._vitesseDeplacement = True, 150
        self._finirDeplacementSP()
        self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._xTile, self._yTile, self._c)

    def _attendreJoueur(self):
        if not self._attenteJoueur:
            Horloge.initialiser(id(self), "Attente joueur", 3000)
        self._attenteJoueur, self._poursuiteJoueur = True, False
        self._boiteOutils.ajouterTransformation(True, "SplashText Duck", nomPNJ="DuckGod", couche=self._c, texte="Come with me!", taille=12, antialias=True, couleurTexte=(255,255,255))
        self._lancerTrajet(self._boiteOutils.deplacementSPVersPnj("Joueur", 3000, self._xTile, self._yTile), False)

    def _gererEtape3(self):
        self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 1, 3)
        self._boiteOutils.retirerTransformation(True, "SplashText Duck")
        self._boiteOutils.interrupteurs["escalierLibre"].activer()
        self._gestionnaire.evenements["concrets"]["InterieurMaison"]["SortieExterieur"][0].nomCarte = "Maison Dream"
        self._etapeTraitement += 1

    def _gererEtape4(self):
        if self._xTile == 1 and self._yTile == 3 and self._deplacementBoucle is False:
            self._deplacerSurCarte("InterieurMaison", 1, 4, 2, "Bas")
            self._etapeTraitement += 1

    def _gererEtape5(self):
        departMaison = False
        if (self._xTile,self._yTile) != (1,3):
            departMaison = True
        elif self._boiteOutils.getCoordonneesJoueur() != (1,3):
            self._poseDepart, departMaison = True, True
        if departMaison:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 13, 3)
            self._etapeTraitement += 1

    def _gererEtape6(self):
        if (self._xTile,self._yTile) == (13,3) and self._deplacementBoucle is False:
            self._deplacerSurCarte("Maison Dream", 3, 7, 2, "Bas")
            self._etapeTraitement += 1

    def _gererEtape7(self):
        if self._gestionnaire.nomCarte == "Maison Dream":
            departMaison = False
            if (self._xTile,self._yTile) != (3,5):
                departMaison = True
                self._transformationBrouillard()
            elif self._boiteOutils.getCoordonneesJoueur() != (3,5):
                self._poseDepart, departMaison = True, True
            if departMaison:
                self._initialiserDeplacement(1, direction=self._directionRegard) 
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 10, 17)
                self._etapeTraitement += 1

    def _gererEtape8(self):
        self._majInfosJoueur()
        if self._xTile == 10 and self._yTile == 17 and self._deplacementBoucle is False and self._joueurProche is True:
            self._vitesseDeplacement = 170
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 63, 6)
            self._boiteOutils.ajouterTransformation(True, "SplashText Duck2", nomPNJ="DuckGod", couche=self._c, texte="This way, quick!", taille=12, antialias=True, couleurTexte=(255,255,255))
            self._etapeTraitement += 1

    def _gererEtape9(self):
        if self._xTile == 63 and self._yTile == 6 and self._deplacementBoucle is False:
            self._boiteOutils.retirerTransformation(True, "SplashText Duck2")
            self._boiteOutils.interrupteurs["fogRises"].activer()
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 93, 10)
            self._etapeTraitement += 1

    def _gererEtape10(self):
        if self._boiteOutils.interrupteurs["fogRises"].voir() is False:
            self._finirDeplacementSP()
            self._poseDepart = False
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._lancerTrajet("Aucune", False)
            self._etapeTraitement += 1

    def _gererEtape11(self):
        if self._boiteOutils.interrupteurs["RetourDuckGod"].voir() is True:
            self._poseDepart = True
            self._seTeleporter(228, 10, "Droite")
            self._etapeTraitement += 1

    def _gererEtape12(self):
        if self._boiteOutils.evenementVisible(self._nom, self._c) and self._deplacementBoucle is False:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 233, 10)
            self._etapeTraitement += 1

    def _gererEtape13(self):
        if self._deplacementBoucle is False and self._xTile == 233 and self._yTile == 10:
            self._vitesseDeplacement = 165
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 285, 21, eau=True)
            self._etapeTraitement += 1

    def _gererEtape14(self):
        if self._deplacementBoucle is False and self._xTile == 285 and self._yTile == 21:
            self._deplacerSurCarte("Entree Maison Gods", 9, 5, 2, "Droite")
            self._etapeTraitement += 1

    def _gererEtape15(self):
        if LANCEMENT_ULTERIEUR:
            self._initialiserDeplacement(1, direction=self._directionRegard)
            self._vitesseDeplacement = 165
        if self._jeu.carteActuelle.nom == "Entree Maison Gods":
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 3, 5)
            self._etapeTraitement += 1

    def _gererEtape16(self):
        if self._deplacementBoucle is False and self._xTile == 3 and self._yTile == 5:
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._boiteOutils.jouerSon("Fall", "Duck Fall Maison Gods")
            self._etapeTraitement += 1

    def _gererEtape17(self):
        pass

class Crow(PNJ):
    def __init__(self, jeu, gestionnaire, x, y, c, directionDepart):
        super().__init__(jeu, gestionnaire, "Crow", x, y, c, "Crow.png", (0,0,0), (0,0), False, ["Aucune"], directionDepart=directionDepart,vitesseDeplacement=50)
        i, self._traitement, self._sonorite = 1, dict(), True
        self._xArrivee, self._xArriveeOld, self._yArrivee, self._yArriveeOld = -1, -1, -1, -1
        while i <= 6:
            self._traitement[i] = getattr(self, "_gererEtape" + str(i))
            i += 1
        Horloge.initialiser(id(self), "Crow call", 1)
        self._dureeAppel = False

    def _gererEtape(self):
        if Horloge.sonner(id(self), "Crow call") and self._sonorite:
            self._boiteOutils.jouerSon("Crow Call", "Crow Call", fixe=True, evenementFixe=self._nom)
            if self._dureeAppel is False:
                self._dureeAppel = self._boiteOutils.getDureeInstanceSon("Crow Call")
            Horloge.initialiser(id(self), "Crow call", self._dureeAppel + random.randint(3000,8000))
        etapeActuelle = self._etapeTraitement
        self._traitement[self._etapeTraitement]()
        while etapeActuelle < self._etapeTraitement:
            etapeActuelle = self._etapeTraitement
            self._traitement[self._etapeTraitement]()

    def _genererLancerTrajetAleatoire(self, x1, y1, x2, y2):
        while (self._xArrivee == self._xArriveeOld and self._yArrivee == self._yArriveeOld) or (self._xArrivee == self._xTile and self._yArrivee == self._yTile) or self._jeu.carteActuelle.tilePraticable(self._xArrivee, self._yArrivee, self._c) is False:
            self._xArrivee, self._yArrivee = random.randint(x1, x2), random.randint(y1, y2)
        self._xArriveeOld, self._yArriveeOld = self._xArrivee, self._yArrivee
        self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xArrivee, self._yArrivee, balade=True, frequencePauseBalade=2)
    

    def _gererEtape1(self):
        self._majInfosJoueur()
        if (self._deplacementBoucle is False or self._etapeMarche == 1) and self._boiteOutils.evenementVisible(self._nom, self._c) and self._boiteOutils.estimationDistanceRestante((self._xTile,self._yTile), (self._gestionnaire.xJoueur, self._gestionnaire.yJoueur)) <= 5: 
            self._finirDeplacementSP()
            Horloge.initialiser(id(self), "Crow dialogue", 5000)
            self._boiteOutils.ajouterTransformation(True, "SplashText Crow", nomPNJ="Crow", couche=self._c, texte="Are you lost, humble hunter?", taille=12, antialias=True, couleurTexte=(255,255,255))
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 94, 28, intelligence=False)
            self._etapeTraitement += 1
        elif self._deplacementBoucle is False and ((self._xTile == self._xArrivee and self._yTile == self._yArrivee) or (self._xArrivee,self._yArrivee) == (-1,-1)):
            self._genererLancerTrajetAleatoire(83, 10, 90, 13)

    def _gererEtape2(self):
        if self._deplacementBoucle is False and self._xTile == 94 and self._yTile == 28:
            self._vitesseDeplacement = 100
            self._boiteOutils.retirerTransformation(True, "SplashText Crow")
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 164, 42)
            self._etapeTraitement += 1

    def _gererEtape3(self):
        pass

    def _gererEtape4(self):
        pass

    def _gererEtape5(self):
        pass

    def _gererEtape6(self):
        pass

class WizardForest(PNJ):
    def __init__(self, jeu, gestionnaire, x, y, c, directionDepart, nom):
        directionSP = "V" + directionDepart + str(2500)
        super().__init__(jeu, gestionnaire, nom, x, y, c, "Wizard.png", (0,0,0), (0,0), True, [directionSP], directionDepart=directionDepart)
        self._joueurVu = False
        if self._nom == "WizardForest1":
            self._horloges, self._dureeWhisper = ["Whisper now1", "Whisper now2", "Whisper now3"], False
            for horloge in self._horloges:
                Horloge.initialiser(id(self), horloge, random.randint(1,10000))

    def _gererEtape(self):
        if self._nom == "WizardForest1" and self._joueurVu is False:
            for horloge in self._horloges: 
                if Horloge.sonner(id(self), horloge):
                    self._boiteOutils.jouerSon("Whisper", horloge, nombreEcoutes=2, fixe=True, xFixe=169, yFixe=35)
                    if self._dureeWhisper is False:
                        self._dureeWhisper = self._boiteOutils.getDureeInstanceSon(horloge)
                    Horloge.initialiser(id(self), horloge, self._dureeWhisper + 200)
        if self._joueurVu is False and self._boiteOutils.interrupteurs["JoueurVuWizards"].voir() is True:
            self._joueurVu, self._etapeMarche = True, 1
            self._finirDeplacementSP()
            if self._yTile <= 32 or self._xTile == 173:
                self._lancerTrajet("RGauche",False)
            elif self._xTile == 165:
                self._lancerTrajet("RDroite",False)
            else:
                self._lancerTrajet("RHaut",False)
            if self._nom == "WizardForest1":
                for horloge in self._horloges:
                    self._boiteOutils.arreterSonEnFondu(horloge, 1)
        if self._boiteOutils.interrupteurs["Wizards disappear"].voir() is True:
            self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, self._nom)
            self._boiteOutils.supprimerPNJ(self._nom, self._c)

class Feu(PNJ):
    def __init__(self, jeu, gestionnaire, x, y, c):
        super().__init__(jeu, gestionnaire, "Feu", x, y, c, "Feu.png", (0,0,0), (0,0), True, ["VBas2500"], dureeAnimationSP=60)
        self._positionSource = Rect(32,0,32,32)
    
    def _ajusterPositionSource(self, enMarche, direction):
        if enMarche is True:
            if self._pied.voir() is True:
                self._positionSource.move_ip(-self._positionSource.width, 0)
            else:
                self._positionSource.move_ip(self._positionSource.width, 0)

    def _gererEtape(self):
        if self._boiteOutils.interrupteurs["Wizards disappear"].voir() is True:
            self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, self._nom)
            self._boiteOutils.supprimerPNJ(self._nom, self._c)

class Bruiteur(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._sonsLances, self._volume1, self._volume2, self._pause = False, VOLUME_MUSIQUE, 0.0, False

    def traiter(self):
        if self._sonsLances is False:
            self._boiteOutils.jouerSon("Lava", "Lava", nombreEcoutes=0)
            self._boiteOutils.jouerSon("TeaMusic", "Tea Music", volume=0, nombreEcoutes=0)
            self._sonsLances = True
        if self._gestionnaire.xJoueur < 59 and self._gestionnaire.yJoueur < 15:
            self._volume1, self._volume2 = 1.0, 0.0
        elif self._gestionnaire.xJoueur >= 67 or (self._gestionnaire.xJoueur > 59 and self._gestionnaire.yJoueur < 36):
            self._volume1, self._volume2 = 0.0, 1.0
        else: #Zone de transition
            self._volume1 = 1.0 - ((self._gestionnaire.yJoueur - 30) / 10)
            distanceY = 41 - self._gestionnaire.yJoueur
            if self._gestionnaire.xJoueur < 59 and distanceY > 2:
                positionTransition = (((38 - self._gestionnaire.yJoueur) - 23) / -1) + 1
                self._volume2 = (0.5/24) * positionTransition
            elif self._gestionnaire.xJoueur < 59 and distanceY <= 2:
                self._volume2 = 0.5
            elif self._gestionnaire.xJoueur > 59: 
                distanceX = 67 - self._gestionnaire.xJoueur
                if distanceX >= 6:
                    self._volume2 = 1.0 - (distanceX / 17.5)
                elif distanceX >= 2:
                    self._volume2 = 1.0 - (distanceX / 17)
                elif distanceX == 1:
                    self._volume2 = 0.9
        if not JEU_MUET:
            #print(self._pause,self._boiteOutils.interrupteurs["MusiqueThe"].voir() )
            if self._boiteOutils.interrupteurs["MusiqueThe"].voir() is False:
                if self._pause is False:
                    self._pause = True
                    self._boiteOutils.arreterSonEnFondu("Tea Music", 3000)
            else:
                if self._pause is True:
                    self._pause = False
                    self._boiteOutils.jouerSon("TeaMusic", "Tea Music", volume=self._volume2, nombreEcoutes=0)
                if self._boiteOutils.getVolumeInstance("Lava") != self._volume1: 
                    self._boiteOutils.changerVolumeInstance("Lava", self._volume1)
                if self._boiteOutils.getVolumeInstance("Tea Music") != self._volume2: 
                    self._boiteOutils.changerVolumeInstance("Tea Music", self._volume2)

class SkullRing(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._fait = False

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._fait is False:
            self._fait = True
            self._boiteOutils.interrupteurs["JoueurSonneMaisonGods"].activer()
            self._boiteOutils.interrupteurs["MusiqueThe"].desactiver()
            self._boiteOutils.arreterSonEnFondu("Tea Music", 3000)
            self._boiteOutils.jouerSon("DoorBell", "DoorBell")
            self._boiteOutils.arreterPensees()

class God(PNJ):
    etapesMax = { "DuckGod": 8, "CrowGod": 4, "WizardGod": 8 }
    wizardQuestion, duckOuverture, duckAccueil = False, False, False
    placesDisponibles = [(69,42), (69,43), (73,43)]
    godsAssis = {"DuckGod":False, "CrowGod":False, "WizardGod":False}

    def __init__(self, jeu, gestionnaire, x, y, c, directionDepart, nom, fichier):
        super().__init__(jeu, gestionnaire, nom, x, y, c, fichier, (0,0,0), (0,0), True, ["V"+directionDepart+str(2500)], directionDepart=directionDepart)
        i, self.traitement = 1, {}
        while i <= God.etapesMax[nom]:
            self.traitement[i] = getattr(self, "_gererEtape" + nom + str(i))
            i += 1
        if self._nom == "DuckGod":
            self._surPlace, self._positionSource = False, Rect(0,0,24,26)
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)
        self._xArrivee, self._yArrivee, self._enRoute = -1, -1, False
        self._sleeping = False

    def _gererEtape(self):
        etapeActuelle = self._etapeTraitement
        self.traitement[self._etapeTraitement]()
        while etapeActuelle < self._etapeTraitement:
            etapeActuelle = self._etapeTraitement
            self.traitement[self._etapeTraitement]()

    def _ajusterPositionSource(self, enMarche, direction):
        if self._nom != "DuckGod":
            Mobile._ajusterPositionSource(self, enMarche, direction)
            return
        self._positionSource.left, self._positionSource.top = 0, 0
        if self._surPlace:
            self._positionSource.left += 24 * 4
        if "Bas" in direction:
            pass
        elif "Gauche" in direction:
            self._positionSource.top = 1 * 26
        elif "Haut" in direction:
            self._positionSource.top = 2 * 26
        elif "Droite" in direction:
            self._positionSource.top = 3 * 26
        self._positionSource.left += (self._etapeAnimation-1) * 24

    def _determinerAnimation(self, surPlace=False):
        if self._nom != "DuckGod":
            return Mobile._determinerAnimation(self, surPlace=surPlace)
        if self._surPlace != surPlace:
            self._etapeAnimation = 1
        self._surPlace = surPlace
        if Horloge.sonner(id(self), 2) or self._surPlace:
            self._etapeAnimation += 1
            if self._etapeAnimation > 4:
                self._etapeAnimation = 1
            Horloge.initialiser(id(self), 2, self._dureeAnimation)
            return True
        else:
            return False

    def _invitesConversation(self):
        if self._boiteOutils.interrupteurs["JoueurSonneMaisonGods"].voir() is True and self._etapeMarche == 1:
            self._finirDeplacementSP()
            self._lancerTrajet("RGauche", False)
            self._etapeTraitement += 1

    def _suivreJoueurDuRegard(self):
        self._majInfosJoueur()
        if self._joueurBouge[0] and self._enRoute is False:
            self._lancerTrajet(self._boiteOutils.regardVersPnj("Joueur", self._xTile, self._yTile), False)
        if self._boiteOutils.interrupteurs["DialogueVisiteur"].voir():
            if self._nom == "CrowGod":
                self._lancerTrajet("VGauche2500", True)
                God.godsAssis[self._nom] = True
                self._etapeTraitement += 1
            elif self._deplacementBoucle is False and self._xTile == self._xArrivee and self._yTile == self._yArrivee:
                self._lancerTrajet("VDroite2500" if self._xTile == 69 else "VGauche2500", True)
                self._actionTea = self._listeActions[0]
                God.godsAssis[self._nom] = True
                self._etapeTraitement += 1
            elif self._etapeMarche == 1 and (self._xTile != self._xArrivee or self._yTile != self._yArrivee) and (self._enRoute is False or (self._xArrivee,self._yArrivee) == (self._gestionnaire.xJoueur,self._gestionnaire.yJoueur)):
                self._enRoute = True
                if self._gestionnaire.xJoueur == self._xArrivee and self._gestionnaire.yJoueur == self._yArrivee:
                    God.placesDisponibles.append((self._xArrivee,self._yArrivee))
                self._xArrivee, self._yArrivee = God.placesDisponibles[0] 
                God.placesDisponibles.remove((self._xArrivee,self._yArrivee))
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xArrivee, self._yArrivee)

    def _verifierGodsAssis(self):
        if self._boiteOutils.interrupteurs["GodsAssis"].voir() is False and False not in God.godsAssis.values():
            self._boiteOutils.interrupteurs["GodsAssis"].activer()
        if self._boiteOutils.interrupteurs["ParalysieGods1"].voir():
            self._finirDeplacementSP()
            self._etapeTraitement += 1

    def _gererParalysie(self):
        self._sleeping = True
        self._majInfosJoueur()
        if self._joueurBouge[0]:
            self._lancerTrajet(self._boiteOutils.regardVersPnj("Joueur", self._xTile, self._yTile), False)

    def _gererEtapeDuckGod1(self):
        self._invitesConversation()

    def _gererEtapeDuckGod2(self):
        if God.wizardQuestion == True:
            self._lancerTrajet("VHaut2500", True)
            Horloge.initialiser(id(self), "Discussion visiteur", 13000)
            self._etapeTraitement += 1

    def _gererEtapeDuckGod3(self):
        if Horloge.sonner(id(self), "Discussion visiteur"):
            self._finirDeplacementSP()
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 60, 35, regardFinal="Bas")
            God.duckOuverture = True
            self._etapeTraitement += 1

    def _gererEtapeDuckGod4(self):
        if self._deplacementBoucle is False and self._xTile == 60 and self._yTile == 35:
            ouvrirPorte(self._boiteOutils, 60, 37)
            self._boiteOutils.jouerSon("DoorOpening", "Door Maison Gods")
            self._boiteOutils.ajouterPensee("Good morning, humble hunter. I knew you would make it.", faceset="DuckGod.png")
            self._lancerTrajet("VBas3000","Droite","Droite","Droite","Droite","Droite","Droite","Droite","Droite","Droite","RGauche",False)
            self._etapeTraitement += 1

    def _gererEtapeDuckGod5(self):
        if self._deplacementBoucle is False and self._xTile == 69 and self._yTile == 35:
            God.duckAccueil = True
            self._etapeTraitement += 1

    def _gererEtapeDuckGod6(self):
        self._suivreJoueurDuRegard()

    def _gererEtapeDuckGod7(self):
        self._verifierGodsAssis()

    def _gererEtapeDuckGod8(self):
        self._gererParalysie()

    def _gererEtapeCrowGod1(self):
        self._invitesConversation()

    def _gererEtapeCrowGod2(self):
        self._suivreJoueurDuRegard()

    def _gererEtapeCrowGod3(self):
        self._verifierGodsAssis()

    def _gererEtapeCrowGod4(self):
        self._gererParalysie()

    def _gererEtapeWizardGod1(self):
        if self._boiteOutils.interrupteurs["DébutConversation"].voir() is True and self._etapeMarche == 1:
            self._lancerTrajet("VHaut63000", "Gauche", "Gauche", "Gauche", "Bas","Bas","Bas","Bas","Gauche","Gauche","Gauche","VBas10000","Droite","Droite","Droite","Haut","Haut","Haut","Haut","Droite","Droite","Droite","VHaut2500", False)
            self._etapeTraitement += 1

    def _gererEtapeWizardGod2(self):
        if self._boiteOutils.interrupteurs["JoueurSonneMaisonGods"].voir() is True and (self._deplacementBoucle is False or self._etapeMarche == 1 or "V" in self._listeActions[self._etapeAction]):
            self._finirDeplacementSP()
            self._lancerTrajet("RGauche",False)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 69, 41, regardFinal="Bas")
            self._etapeTraitement += 1

    def _gererEtapeWizardGod3(self):
        if self._deplacementBoucle is False and self._xTile == 69 and self._yTile == 41:
            God.wizardQuestion = True
            self._lancerTrajet("VBas2500",True)
            self._boiteOutils.ajouterPensee("Who's that? I didn't expect anyone else.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("Oh, don't worry, I know who that is.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("I thought I would bring... er... an acquaintance.", faceset="DuckGod.png")
            self._boiteOutils.ajouterPensee("You do suprise me, Sir Duck. But then go on, let this Lord enter.", faceset="WizardGod.png")
            self._boiteOutils.ajouterPensee("He's not exactly a Lord but... you'll see.", faceset="DuckGod.png")
            self._etapeTraitement += 1

    def _gererEtapeWizardGod4(self):
        if God.duckOuverture is True:
            self._finirDeplacementSP()
            self._lancerTrajet("Aucune", False)
            self._etapeTraitement += 1

    def _gererEtapeWizardGod5(self):
        self._suivreJoueurDuRegard()

    def _gererEtapeWizardGod6(self):
        self._verifierGodsAssis()
        if self._boiteOutils.interrupteurs["JoueurOrdreTea"].voir() is True:
            self._etapeTraitement += 1

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._nom == "WizardGod": 
            if self._boiteOutils.interrupteurs["JoueurOrdreTea"].voir() is True:
                self._finirDeplacementSP()
                self._lancerTrajet(self._boiteOutils.deplacementSPVersPnj("Joueur", 5000, self._xTile, self._yTile), False)
                self._boiteOutils.ajouterPensee("Take the teapot and go fill it in the back room.", faceset="WizardGod.png")
                self._boiteOutils.interrupteurs["JoueurServiteur"].activer()
                self._boiteOutils.interrupteurs["JoueurOrdreTea"].desactiver()
            elif self._boiteOutils.interrupteurs["BackRoomToOpen"].voir() is True and self._boiteOutils.interrupteurs["PasswordGiven1"].voir() is False:
                self._finirDeplacementSP()
                self._lancerTrajet(self._boiteOutils.deplacementSPVersPnj("Joueur", 5000, self._xTile, self._yTile), False)
                self._boiteOutils.ajouterPensee("Oh you need a password for the door, that's right.", faceset="WizardGod.png")
                self._boiteOutils.ajouterPensee("It's MY GOOD OLD ALE.", faceset="WizardGod.png")
                self._boiteOutils.ajouterPensee("You'll find a blue and a green bottle. Fill the teapot with the blue one.", faceset="WizardGod.png", tempsLecture=0)
                self._boiteOutils.interrupteurs["PasswordGiven1"].activer()
            elif self._boiteOutils.interrupteurs["ParalysieGods2"].voir() is True and self._boiteOutils.interrupteurs["KeyFound"].voir() is False:
                self._boiteOutils.ajouterPensee("I found a key under the hood of Sir Wizard.", tempsLecture=0)
                self._boiteOutils.interrupteurs["KeyFound"].activer()

    def _gererEtapeWizardGod7(self):
        if self._deplacementBoucle is False:
            self._lancerTrajet(self._actionTea, True)
        if self._boiteOutils.interrupteurs["TeaServed"].voir() is True and self._boiteOutils.interrupteurs["MissionTerminee"].voir() is False:
            self._boiteOutils.ajouterPensee("Thanks for this, daring hunter.", faceset="WizardGod.png")
            self._boiteOutils.interrupteurs["MissionTerminee"].activer()
        if self._boiteOutils.interrupteurs["ParalysieGods1"].voir() is True:
            self._finirDeplacementSP()
            self._etapeTraitement += 1

    def _gererEtapeWizardGod8(self):
        self._gererParalysie()

class Teapot(EvenementConcret):
    surTable = Interrupteur(True)
    initInterrupteurGlobal = False

    def __init__(self, jeu, gestionnaire):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        if not Teapot.initInterrupteurGlobal:
            self._boiteOutils.interrupteurs["TeapotInHands"], Teapot.initInterrupteurGlobal = InterrupteurInverse(Teapot.surTable), True

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._boiteOutils.interrupteurs["JoueurServiteur"].voir() is False:
            return
        Teapot.surTable.inverser()
        if Teapot.surTable.voir() is True:
            self._boiteOutils.changerBloc(70, 42, 3, "woodland_indoor.png", (11*32, 10*32, 32,32), (0,0,0), False)
            if self._boiteOutils.interrupteurs["TeapotFilled"].voir():
                self._boiteOutils.interrupteurs["TeaServed"].activer()
        else:
            self._boiteOutils.changerBloc(70, 42, 3, "", [], [], True, vide=True)

class SpeakingDoor(EvenementConcret):
    def __init__(self, jeu, gestionnaire, x, y):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._ouverture, self._passwordAsked, self._x, self._y = False, False, x, y

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._ouverture is False and self._boiteOutils.interrupteurs["JoueurServiteur"].voir():
            if self._x == 92 and self._y == 40:
                self._interactionBackroom()
            elif self._x == 100 and self._y == 40:
                self._interactionLastDoor()

    def _interactionBackroom(self):
        if self._boiteOutils.interrupteurs["PasswordGiven1"].voir() is False:
            if self._passwordAsked is False:
                self._boiteOutils.ajouterPensee("You're not the master of this house. I won't open unless you have a password.", tempsLecture=0)
                self._boiteOutils.interrupteurs["BackRoomToOpen"].activer()
                self._passwordAsked = True
            else:
                self._boiteOutils.ajouterPensee("So what's the password? My master will certainly not reveal it to a man.", tempsLecture=0)
        else:
            self._boiteOutils.ajouterPensee("What? You know the password? Well, er um, you can pass, I guess.", tempsLecture=0)
            Horloge.initialiser(id(self), "Ouverture", 2000)
            self._ouverture = True

    def _interactionLastDoor(self):
        if self._boiteOutils.interrupteurs["KeyFound"].voir() is False and self._boiteOutils.interrupteurs["ParalysieGods2"].voir() is True:
            if self._passwordAsked is False:
                self._boiteOutils.ajouterPensee("Look, mortal, I'm locked. And I doubt my master gave you the key.", tempsLecture=0)
                self._passwordAsked = True
            else:
                self._boiteOutils.ajouterPensee("Why do you even come back? It's pointless, my master won't give it to a man.", tempsLecture=0)
        elif self._boiteOutils.interrupteurs["KeyFound"].voir() is True:
            self._boiteOutils.ajouterPensee("What? You...you've found the key? Dammit. That was unexpected.", tempsLecture=0)
            Horloge.initialiser(id(self), "Ouverture", 2000)

    def traiter(self):
        if Horloge.sonner(id(self), "Ouverture"):
            self._boiteOutils.jouerSon("DoorOpening", "Door Maison Gods Speaking")
            ouvrirPorte(self._boiteOutils, self._x, self._y)

class Bottle(EvenementConcret):
    def __init__(self, jeu, gestionnaire, couleur):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._couleur, self._filling, self._splash  = couleur, False, False
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._penseePossible.voir() and self._filling is False and self._splash is False:
            self._boiteOutils.ajouterTransformation(True, "SplashText Tea"+self._couleur, texte="Press Z quickly to fill the teapot", antialias=True, couleurTexte=(255,255,255), position=(10, 10), taille=30, alpha=255)
            Horloge.initialiser(id(self), "SplashText", 5000)
            self._splash = True
            if self._couleur == "Blue":
                self._boiteOutils.ajouterPensee("The blue bottle was filled with lime flowers. The label read:")
                self._boiteOutils.ajouterPensee("“Lime Flower Tea from the Middle South. To drink in the morning.”", tempsLecture=0)
            elif self._couleur == "Green":
                self._boiteOutils.ajouterPensee("The green bottle was filled with tiny blood-red petals. The label read:")
                self._boiteOutils.ajouterPensee("“Devil Tea from the Heart of the Forest. To drink in emergency. Immediate effects.”", tempsLecture=0)
        elif self._boiteOutils.interrupteurs["JoueurServiteur"].voir() is True and self._boiteOutils.interrupteurs["TeapotFilled"].voir() is False and self._boiteOutils.interrupteurs["TeapotInHands"].voir() is True:
            if self._filling is False:
                self._boiteOutils.jouerSon("BruitThe", "BruitTheFilling")
                Horloge.initialiser(id(self), "Filling over", 3000)
            self._filling = True
            Horloge.initialiser(id(self), "Filling deadline", 1000)

    def traiter(self):
        if self._filling:
            if Horloge.sonner(id(self), "Filling over"):
                self._boiteOutils.interrupteurs["TeapotFilled"].activer()
                self._boiteOutils.retirerTransformation(True, "SplashText Tea"+self._couleur)
                self._splash = True
                self._boiteOutils.ajouterTransformation(True, "SplashText Filled"+self._couleur, texte="Teapot filled with the {0} bottle".format(self._couleur.lower()), antialias=True, couleurTexte=(255,255,255), position=(10,10), taille=30, alpha=255)
                Horloge.arreterSonnerie(id(self), "Filling deadline")
                Horloge.initialiser(id(self), "SplashText", 5000)
                self._boiteOutils.variables["TeaGiven"] = self._couleur
                self._filling = False
            if Horloge.sonner(id(self), "Filling deadline"):
                self._filling = False
                Horloge.arreterSonnerie(id(self), "Filling over")
        if self._splash:
            if Horloge.sonner(id(self), "SplashText"):
                self._boiteOutils.retirerTransformation(True, "SplashText Tea"+self._couleur)
                self._boiteOutils.retirerTransformation(True, "SplashText Filled"+self._couleur)
                self._splash = False

class Cake(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._nombreAppuis, self._penseePossible, self._cakeEaten = 0, InterrupteurInverse(self._boiteOutils.penseeAGerer), False
        self._messagePrinted = False

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        self._nombreAppuis += 1
        if self._penseePossible.voir() is True:
            if self._cakeEaten is False:
                self._boiteOutils.ajouterPensee("I saw a piece of strawberry cake. It looked delicious.")
            self._boiteOutils.ajouterPensee("There was a note nearby. It read:")
            self._boiteOutils.ajouterPensee("“To leave this dream, eat me, then rest.”", tempsLecture=0)
            self._boiteOutils.ajouterTransformation(True, "SplashText Cake", texte="Press Z again to eat the cake", antialias=True, position=(10,30), couleurTexte=(255,255,255), taille=30, alpha=255)
            Horloge.initialiser(id(self), "Splash", 3000)
            self._messagePrinted = True
        if self._nombreAppuis >= 2 and self._cakeEaten is False and self._messagePrinted is True:
            self._boiteOutils.retirerTransformation(True, "SplashText Cake")
            self._boiteOutils.ajouterTransformation(True, "SplashText Cake", texte="You have eaten a piece of cake", antialias=True, position=(10,30), couleurTexte=(255,255,255), taille=30, alpha=255)
            self._boiteOutils.interrupteurs["CakeEaten"].activer()
            self._boiteOutils.changerBloc(100, 34, 3, None, None, None, True, vide=True)
            self._cakeEaten = True
            Horloge.initialiser(id(self), "Splash", 3000)

    def traiter(self):
        if Horloge.sonner(id(self), "Splash"):
            self._boiteOutils.retirerTransformation(True, "SplashText Cake")

class ForestKey(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._clePrise = False
        
    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._clePrise is False:
            self._clePrise = True
            self._boiteOutils.changerBloc(8, 68, 3, None, None, None, True, vide=True)
            self._boiteOutils.interrupteurs["KeyForestFound"].activer()

def fermerPorte(boiteOutils, x, y):
    boiteOutils.changerBloc(x, y, 3, "woodland_indoor_x3.png", (0,0,32,32), (0,0,0), True)
    boiteOutils.changerBloc(x, y+1, 1, "woodland_indoor_x3.png", (0,32,32,32), (0,0,0), False)
    boiteOutils.changerBloc(x, y+2, 1, "woodland_indoor_x3.png", (0,64,32,32), (0,0,0), True)
            
def ouvrirPorte(boiteOutils, x, y):
    boiteOutils.changerBloc(x, y, 3, "woodland_indoor_x3.png", (32,0,32,32), (0,0,0), True)
    boiteOutils.changerBloc(x, y+1, 1, "woodland_indoor_x3.png", (32,32,32,32), (0,0,0), True)
    boiteOutils.changerBloc(x, y+2, 1, "woodland_indoor_x3.png", (32,64,32,32), (0,0,0), True)
            
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
                #print("Au depart", self._parametresGeneration[typeActuel]["typeAnimal"]+str(animauxDeCeType), (x,y))
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
                self._nombre = {"Squirrel":4, "SquirrelMinimal":4}
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
                self._nombre["SquirrelMinimal"] = 3
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
        #print("Ajout de", nom, (int(positionCarte.left/32), int(positionCarte.top/32)) )

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
                self._boiteOutils.jouerSon(self._typeAnimal+"Fuite", self._nom + "fuite", fixe=True, xFixe=self._xTile, yFixe=self._yTile)
                self._monteeArbre, self._fuite = True, False
        if self._monteeArbre:
            if self._deplacementBoucle is False:
                self._boiteOutils.supprimerPNJ(self._nom, self._c)
                self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, self._nom)
                self._gestionnaireAnimaux.onMortAnimal(self._typeAnimal)
                self._gestionnaire.evenements["abstraits"]["Narrateur"].onMortAnimal(self._typeAnimal)
        if self._animationMort is True and self._xTile == self._tileCadavre[0] and self._yTile == self._tileCadavre[1] and self._cadavreEnPlace is False:
            self._cadavreEnPlace = True

    def onCollision(self, nomPNJ, positionCarte):
        super().onCollision(nomPNJ, positionCarte)
        if "Fleche" in nomPNJ and self._vulnerable:
            self._vie -= 1
            self._etapeTraitement, self._intelligence, self._courage, self._fuyard, self._blessure = 1, True, True, False, True
            self._boiteOutils.jouerSon(self._typeAnimal+"Blesse", self._nom + "blesse", fixe=True, evenementFixe=self._nom)
            Horloge.initialiser(id(self), "Fin clignotant", 2000)
            Horloge.initialiser(id(self), "Rouge clignotant", 1)
            self._lancerFuite()
        if self._vie == 0 and self._animationMort is False:
            self._finirDeplacementSP()
            self._trouverTileCadavre()
            self._gestionnaireAnimaux.onMortAnimal(self._typeAnimal, viaChasse=True)
            self._gestionnaire.evenements["abstraits"]["Narrateur"].onMortAnimal(self._typeAnimal, viaChasse=True)
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
        self._penseePossible, self._penseeJour1Dite = InterrupteurInverse(self._boiteOutils.penseeAGerer), False
        self._traitement, i, etapeMax = dict(), 1, 29
        while i <= etapeMax:
            self._traitement[i] = getattr(self, "_gererEtape"+str(i))
            i += 1
        ###

    def _gererEtape(self):
        etapeActuelle = self._etapeTraitement
        self._traitement[self._etapeTraitement]()
        while etapeActuelle < self._etapeTraitement:
            etapeActuelle = self._etapeTraitement
            self._traitement[self._etapeTraitement]()

    def _gererEtape1(self):
        self._gererSons()

    def _gererEtape2(self):
        if self._deplacementBoucle is False:
            self._finirDeplacementSP()
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 5, 3, regardFinal="Bas", arretAvant=False)
            self._comportementParticulier = True
            self._etapeTraitement += 1

    def _gererEtape3(self):
        if self._deplacementBoucle is False and self._xTile == 5 and self._yTile == 3 and self._comportementParticulier is True:
            self._comportementParticulier = False
        if self._boiteOutils.getNomPensee() == "thoughtOutside":
            self._comportementParticulier = True
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 7, 6, regardFinal="Droite")
            self._etapeTraitement += 1

    def _gererEtape4(self):
        if self._xTile == 7 and self._yTile == 6 and self._deplacementBoucle is False:
            self._lancerTrajet("VDroite1500", False)
            self._etapeTraitement += 1

    def _gererEtape5(self):
        if self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(8, 5, 2, "base_out_atlas.png", (576, 448, 32, 32), (0,0,0), False, permanente=True, nomModif="Retrait tonneaux1")
            self._boiteOutils.changerBloc(9, 5, 2, "base_out_atlas.png", (608, 448, 32, 32), (0,0,0), False, permanente=True, nomModif="Retrait tonneaux2")
            self._boiteOutils.changerBloc(8, 6, 2, "base_out_atlas.png", (576, 480, 32, 32), (0,0,0), False, permanente=True, nomModif="Retrait tonneaux3")
            self._boiteOutils.changerBloc(9, 6, 2, "base_out_atlas.png", (608, 480, 32, 32), (0,0,0), False, permanente=True, nomModif="Retrait tonneaux4")
            self._boiteOutils.jouerSon("Barrel", "Taking it for laundry", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 13, 3)
            self._etapeTraitement += 1

    def _gererEtape6(self):
        if self._deplacementBoucle is False and self._xTile == 13 and self._yTile == 3:
            self._boiteOutils.interrupteurs["BeliaSortie"].activer()
            self._deplacerSurCarte("Maison", 3, 8, 2, "Bas")
            self._etapeTraitement += 1

    def _gererEtape7(self):
        if self._jeu.carteActuelle.nom == "Maison":
            self._porteRefermee, self._sons = True, dict()
            self._sons[0] = [["Wateragitation", "Washing clothe"], {"fixe":True, "evenementFixe":self._nom}, True]
            self._sons[9], self._sons[18] = list(self._sons[0]), list(self._sons[0])
            self._sons[4] = [["Barrel", "Taking clothe"], {"fixe":True, "evenementFixe":self._nom}, True]
            self._sons[13], self._sons[22] = list(self._sons[4]), list(self._sons[4])
            self._sons[8] = [["Washing", "Washing clothe"], {"fixe":True, "evenementFixe":self._nom}, True]
            self._sons[17], self._sons[26] = list(self._sons[8]), list(self._sons[8])
            if self._boiteOutils.interrupteurs["BeliaSortie"].voir():
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 14, arretAvant=True)
                self._etapeTraitement += 2
            else:
                Horloge.initialiser(id(self), "Attente départ", 3000)
                self._etapeTraitement += 1

    def _gererEtape8(self):
        coordonneesJoueur = self._boiteOutils.getCoordonneesJoueur()
        if self._boiteOutils.tileProcheDe((3,5), coordonneesJoueur, 3) is False or (Horloge.sonner(id(self), "Attente départ", arretApresSonnerie=False) and coordonneesJoueur != (3,5)):
            if self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].getPorteOuverte() is False:
                self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].ouvrirOuFermerPorte()
                self._porteRefermee = False
            self._poseDepart = True
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 14, arretAvant=True)
            self._boiteOutils.interrupteurs["BeliaSortie"].activer()
            self._etapeTraitement += 1

    def _gererEtape9(self):
        if self._porteRefermee is False and self._boiteOutils.tileProcheDe((self._xTile,self._yTile),(3,4), 4) is False:
            if self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].getPorteOuverte():
                self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].ouvrirOuFermerPorte()
                self._porteRefermee = True
        if self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(15, 14, self._nom):
            self._boiteOutils.interrupteurs["discussionEtang"].activer()
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(15,14))+"1500",False)
            self._etapeTraitement += 1

    def _gererEtape10(self):
        if self._boiteOutils.getCoordonneesJoueur() != (15,14) and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(15, 14, 2, "base_out_atlas.png", (480, 448, 32, 32), (0,0,0), False)
            self._boiteOutils.jouerSon("Barrel", "Setting it up", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 17, 11, arretAvant=True)
            self._etapeTraitement += 1

    def _gererEtape11(self):
        if self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(17, 11, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(17,11))+"1500",False)
            self._etapeTraitement += 1

    def _gererEtape12(self):
        if self._boiteOutils.getCoordonneesJoueur() != (17,11) and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(17, 10, 3, "base_out_atlas.png", (608, 448, 32, 32), (0,0,0), False)
            self._boiteOutils.changerBloc(17, 11, 2, "base_out_atlas.png", (608, 480, 32, 32), (0,0,0), False)
            self._boiteOutils.jouerSon("Barrel", "Setting it up2", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 13, regardFinal="Droite")
            self._etapeTraitement += 1

    def _gererEtape13(self):
        if self._xTile == 15 and self._yTile == 13 and self._deplacementBoucle is False:
            self._lancerTrajet(["VDroite2500", "Haut", "Haut", "Droite", "VDroite2500","Gauche","Bas","Bas","VBas1500"]*3, False)
            self._etapeTraitement += 1

    def _gererEtape14(self):
        if self._deplacementBoucle is False:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 12, arretAvant=True)
            self._etapeTraitement += 1
        else:
            self._gererSons2()
            if self._etapeAction == 17:
                self._boiteOutils.changerBloc(15, 14, 2, "base_out_atlas.png", (480, 480, 32, 32), (0,0,0), False)

    def _gererEtape15(self):
        if self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(15, 12, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(15,12))+"1500",False)
            self._etapeTraitement += 1

    def _gererEtape16(self):
        if self._boiteOutils.getCoordonneesJoueur() != (15,12) and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(15, 12, 2, "base_out_atlas.png", (480, 448, 32, 32), (0,0,0), False)
            self._boiteOutils.jouerSon("Barrel", "Setting it up3", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 13, regardFinal="Droite")
            self._etapeTraitement += 1

    def _gererEtape17(self):
        if self._xTile == 15 and self._yTile == 13 and self._deplacementBoucle is False:
            self._majSons()
            self._lancerTrajet(["VDroite2500", "Gauche","Haut", "Haut", "Droite", "Droite", "VDroite2500","Gauche", "VBas1500", "Gauche", "Bas", "Bas", "Droite", "VBas1500"]*3, False)
            self._etapeTraitement += 1

    def _gererEtape18(self):
        if self._deplacementBoucle is False:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 17, 11, arretAvant=True)
            self._etapeTraitement += 1
        else:
            self._gererSons2()
            if self._etapeAction == 22:
                self._boiteOutils.changerBloc(15, 12, 2, "base_out_atlas.png", (480, 480, 32, 32), (0,0,0), False)

    def _gererEtape19(self):
        if self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(17, 11, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(17,11))+"1500",False)
            self._etapeTraitement += 1

    def _gererEtape20(self):
        if self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(17,11,2, -1,-1,-1,-1, vide=True )
            self._boiteOutils.changerBloc(17,10,3, -1,-1,-1,-1, vide=True )
            self._boiteOutils.jouerSon("Barrel", "Setting it up4", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 12, arretAvant=True)
            self._etapeTraitement += 1

    def _gererEtape21(self):
        if self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(15, 12, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(15,12))+"1500",False)
            self._etapeTraitement += 1

    def _gererEtape22(self):
        if self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(15,12,2, -1,-1,-1,-1, vide=True )
            self._boiteOutils.jouerSon("Barrel", "Setting it up5", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 15, 14, arretAvant=True)
            self._etapeTraitement += 1

    def _gererEtape23(self):
        if self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(15, 14, self._nom):
            self._lancerTrajet("V"+self._boiteOutils.determinerDirectionDeplacement((self._xTile,self._yTile),(15,14))+"1500",False)
            self._etapeTraitement += 1

    def _gererEtape24(self):
        if self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(15,14,2, -1,-1,-1,-1, vide=True )
            self._boiteOutils.jouerSon("Barrel", "Setting it up6", fixe=True, evenementFixe=self._nom)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 3, 5, regardFinal="Haut")
            self._etapeTraitement += 1

    def _gererEtape25(self):
        if self._deplacementBoucle is False and self._xTile == 3 and self._yTile == 5:
            self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].ouvrirOuFermerPorte()
            self._lancerTrajet("Haut",False)
            self._etapeTraitement += 1

    def _gererEtape26(self):
        if self._deplacementBoucle is False and self._xTile == 3 and self._yTile == 4:
            self._gestionnaire.evenements["concrets"]["Maison"]["SortieInterieurMaison"][0].ouvrirOuFermerPorte()
            self._boiteOutils.interrupteurs["BeliaRentree"].activer()
            self._deplacerSurCarte("InterieurMaison", 7, 6, 2, "Gauche")
            self._etapeTraitement += 1

    def _gererEtape27(self):
        if self._jeu.carteActuelle.nom == "InterieurMaison":
            self._lancerTrajet("Haut","Haut","Gauche","Gauche","Gauche","VHaut2500","Droite","Droite","Droite","VHaut2500","Droite","Droite","Droite","VHaut2500","Gauche","Gauche","Gauche","Bas","Bas","VGauche2500",True)
            self._etapeTraitement += 1

    def _gererEtape28(self):
        self._gererSons()

    def _gererEtape29(self):
        pass

    def _gererSons(self):
        if self._etapeAction == self._listeSons[self._etapeSon][1]:
            self._boiteOutils.jouerSon(self._listeSons[self._etapeSon][0], "Cuisine"+str(self._etapeSon), fixe=True, evenementFixe="Belia", duree=2500, nombreEcoutes=self._listeSons[self._etapeSon][2])
            self._etapeSon += 1
            if self._etapeSon == 4:
                self._etapeSon = 0

    def _gererSons2(self):
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

    def onChangementCarte(self, carteQuittee, carteEntree):
        if carteQuittee == "InterieurMaison" and carteEntree == "Maison":
            if self._boiteOutils.interrupteurs["squirrelPose"].voir() and not self._boiteOutils.interrupteurs["BeliaRentree"].voir() and not self._boiteOutils.interrupteurs["BeliaSortie"].voir():
                self._deplacerSurCarte("Maison", 3, 4, 2, "Bas")
                self._lancerTrajet("Aucune", False)
                self._poseDepart = False
                self._etapeTraitement = 7

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._etapeTraitement == 28 and self._penseePossible.voir() and not self._penseeJour1Dite:
            if self._boiteOutils.variables["NombreGlands"] == 0:
                self._boiteOutils.ajouterPensee("Have you found some nuts? You should shake down the oak trees outside.", faceset="Belia.png", tempsLecture=0)
            elif not self._boiteOutils.interrupteurs["nutsOnTable"].voir():
                self._boiteOutils.ajouterPensee("Just put the nuts on the table for the children.", faceset="Belia.png", tempsLecture=0)
            elif self._boiteOutils.interrupteurs["nutsOnTable"].voir():
                self._boiteOutils.ajouterPensee("Tomorrow is another day...", faceset="Belia.png", tempsLecture=0)
            self._penseeJour1Dite = True

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
            self._boiteOutils.jouerSon("Pickup", "Gland ramassé", fixe=True, xFixe=x, yFixe=y)
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._gestionnaire.ajouterEvenementATuer("concrets", self._jeu.carteActuelle.nom, self._nom)

class Enfant(PNJ):
    def __init__(self, jeu, gestionnaire, nom, x, y, c):
        fichier, couleurTransparente, persoCharset, vitesseDeplacement, self._nom = nom + ".png", (0,0,0), (0,0), 150, nom
        repetitionActions, directionDepart, poseDepart = True, "Gauche", True
        listeActions = ["Droite","Bas","Bas","Bas","Bas","Bas","Bas","Bas","Droite","Droite","Droite","Bas","Gauche","Gauche","Gauche","Gauche","Haut","Haut","Haut","Haut","Haut","Haut","Haut","Haut"]
        super().__init__(jeu, gestionnaire, nom, x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement, poseDepart=poseDepart)
        if y == 8:
            self._etapeAction = 20
        self._positionsSuivi, self._etapeSuivi = {"Tom":[(10,7),(7,6)], "Elie":[(10,9),(7,5)]}, 0
        self._xArrivee, self._yArrivee = -1, -1
        (self._xEtage,self._yEtage) = (1,7) if self._nom == "Tom" else (1,6)
        (self._xRDC,self._yRDC) = (1,3) if self._nom == "Tom" else (5,13)
        self._gestionnaire.ajouterChangementCarteANotifier("Maison", "InterieurMaison", self._nom, "EtageMaison")
        self._monteeEtage, self._descenteEtage, self._penseeDite, self._penseePossible = False, False, False, InterrupteurInverse(self._boiteOutils.penseeAGerer)
        self._traitement, i, etapeMax = dict(), 1, 13
        while i <= etapeMax:
            self._traitement[i] = getattr(self, "_gererEtape"+str(i))
            i += 1
        ###

    def onChangementCarte(self, carteQuittee, carteEntree):
        if carteQuittee == "InterieurMaison" and carteEntree == "Maison" and self._boiteOutils.interrupteurs["squirrelPose"].voir() and not self._boiteOutils.interrupteurs["BeliaRentree"].voir() and not self._monteeEtage:
            self._deplacerSurCarte("EtageMaison", self._xEtage, self._yEtage, 2, "Bas")
            self._etapeTraitement, self._monteeEtage = 7, True
        elif carteQuittee == "InterieurMaison" and carteEntree == "EtageMaison" and self._boiteOutils.interrupteurs["squirrelPose"].voir() and not self._boiteOutils.interrupteurs["BeliaRentree"].voir() and not self._monteeEtage:
            self._deplacerSurCarte("EtageMaison", 1, 3, 2, "Bas")
            self._etapeTraitement = 6
            self._poseDepart, self._monteeEtage = False, True
        elif carteQuittee == "Maison" and carteEntree == "InterieurMaison" and self._boiteOutils.interrupteurs["BeliaRentree"].voir() and not self._descenteEtage:
            self._deplacerSurCarte("InterieurMaison", self._xRDC, self._yRDC, 2, "Bas", carteQuittee="EtageMaison")
            self._etapeTraitement, self._descenteEtage = 10, True

    def _gererEtape(self):
        etapeActuelle = self._etapeTraitement
        self._traitement[self._etapeTraitement]()
        while etapeActuelle < self._etapeTraitement:
            etapeActuelle = self._etapeTraitement
            self._traitement[self._etapeTraitement]()

    def _gererEtape1(self):
        pass

    def _gererEtape2(self):
        if self._deplacementBoucle is False and self._boiteOutils.interrupteurs["JoueurEntre2"].voir() is True:
            (self._xArrivee, self._yArrivee) = self._positionsSuivi[self._nom][self._etapeSuivi]
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xArrivee, self._yArrivee)
            self._comportementParticulier = True
            self._etapeTraitement += 1
            self._etapeSuivi += 1
        if  self._boiteOutils.getNomPensee() == "thoughtUpstairs" and self._etapeMarche == 1:
            self._etapeTraitement = 4
            self._finirDeplacementSP()
        if self._comportementParticulier is True and self._xTile == self._xArrivee and self._yTile == self._yArrivee and self._deplacementBoucle is False:
            self._finirDeplacementSP()
            self._comportementParticulier = False

    def _gererEtape3(self):
        if self._deplacementBoucle is False and self._boiteOutils.interrupteurs["JoueurEntre3"].voir() is True:
            (self._xArrivee, self._yArrivee) = self._positionsSuivi[self._nom][self._etapeSuivi]
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xArrivee, self._yArrivee, regardFinal="Gauche")
            self._comportementParticulier = True
            self._etapeSuivi += 1
            self._etapeTraitement += 1
        if  self._boiteOutils.getNomPensee() == "thoughtUpstairs" and self._etapeMarche == 1:
            self._etapeTraitement = 4
            self._finirDeplacementSP()
        if self._comportementParticulier is True and self._xTile == self._xArrivee and self._yTile == self._yArrivee and self._deplacementBoucle is False:
            self._finirDeplacementSP()
            self._comportementParticulier = False

    def _gererEtape4(self):
        if self._etapeMarche == 1 and self._boiteOutils.getNomPensee() == "thoughtUpstairs":
            self._comportementParticulier = True
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 1, 3)
            self._etapeTraitement += 1

    def _gererEtape5(self):
        if self._deplacementBoucle is False and self._xTile == 1 and self._yTile == 3:
            self._boiteOutils.interrupteurs[self._nom+"Etage"].activer()
            self._deplacerSurCarte("EtageMaison", self._xEtage, self._yEtage, 2, "Bas")
            self._etapeTraitement, self._monteeEtage = 7, True

    def _gererEtape6(self):
        if self._jeu.carteActuelle.deplacementPossible(Rect(1*32, 3*32, 32, 32), self._c, self._nom):
            self._poseDepart = True
            self._etapeTraitement += 1

    def _gererEtape7(self):
        (self._xArrivee,self._yArrivee) = (3,11) if self._nom == "Tom" else (3,10)
        self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xArrivee, self._yArrivee)
        self._etapeTraitement += 1

    def _gererEtape8(self):
        if self._xTile == self._xArrivee and self._yTile == self._yArrivee and self._deplacementBoucle is False:
            self._lancerTrajet(500,False)
            self._fuyard = True
            self._etapeTraitement += 1

    def _gererEtape9(self):
        if self._deplacementBoucle is False:
            self._genererLancerTrajetAleatoire(2,2)
            if self._boiteOutils.interrupteurs["ConversationEnfants"].voir() is False and self._boiteOutils.penseeAGerer.voir() is False:
                self._boiteOutils.ajouterPensee("Are we havin' nuts for dinner tonight? Will I ever taste some meat again?", faceset="Tom.png")
                self._boiteOutils.ajouterPensee("Shhh, not so loud... He's here!", faceset="Elie.png")
                self._boiteOutils.interrupteurs["ConversationEnfants"].activer()

    def _gererEtape10(self):
        self._poseDepart = True
        if self._nom == "Tom":
            self._lancerTrajet("RBas", True)
        self._etapeTraitement += 1

    def _gererEtape11(self):
        if self._deplacementBoucle is False or self._etapeMarche == 1:
            if self._nom == "Elie" and not self._boiteOutils.interrupteurs["nutsOnTable"].voir():
                self._fuyard = True
                self._genererLancerTrajetAleatoire(2,2)
            elif self._boiteOutils.interrupteurs["nutsOnTable"].voir():
                (self._xTable,self._yTable) = (5,13) if self._nom == "Tom" else (9,13)
                self._directionTable = "Droite" if self._nom == "Tom" else "Gauche"
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, self._xTable, self._yTable, regardFinal=self._directionTable)
                self._etapeTraitement += 1

    def _gererEtape12(self):
        if self._deplacementBoucle is False and self._xTile == self._xTable and self._yTile == self._yTable:
            self._lancerTrajet("V"+self._directionTable+str(2500), True)

    def _gererEtape13(self):
        pass

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

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._etapeTraitement == 11 and self._penseePossible.voir():
            if self._nom == "Tom" and self._penseeDite is False:
                self._boiteOutils.ajouterPensee("I'M HUNGRY!!!", faceset="Tom.png", tempsLecture=0)
                self._boiteOutils.interrupteurs["TomHungry"].activer()
                self._penseeDite = True
            elif self._nom == "Elie" and self._penseeDite is False:
                self._boiteOutils.ajouterPensee("Whatever you've found for dinner will do.", faceset="Elie.png", tempsLecture=0)
                self._penseeDite = True

class MembreFamille(PNJ):
    """Pattern decorator pour tous les membres de la famille : quelques comportements communs."""
    def __init__(self, pnj):
        self.__dict__["_pnj"], self._comportementParticulier = pnj, False

    def __setattr__(self, attribut, valeur):
        return setattr(self.__dict__["_pnj"], attribut, valeur)

    def __getattr__(self, attribut):
        return getattr(self.__dict__["_pnj"], attribut)

    def _gererEtape(self):
        if self._etapeTraitement == 1 and (self._etapeMarche == 1 or "V" in self._listeActions[self._etapeAction]) and self._boiteOutils.interrupteurs["JoueurEntre"].voir() is True:
            self._finirDeplacementSP()
            self._lancerTrajet(self._boiteOutils.regardVersPnj("Joueur",-1,-1,evenementReference=self._nom),False)
            self._etapeTraitement += 1
        if (self._etapeTraitement == 2 or self._etapeTraitement == 3) and self._comportementParticulier is False:
            self._majInfosJoueur()
            if self._joueurBouge[0] is True:
                self._lancerTrajet(self._boiteOutils.regardVersPnj("Joueur",-1,-1,evenementReference=self._nom),False)
        self.__dict__["_pnj"]._gererEtape()

    def onNotification(self, nomNotifieur, carteNotifieur, objetNotification, *parametres1, **parametres2):
        if objetNotification == "Nuit étage":
            self._finirDeplacementSP()
            self._deplacerSurCarte("EtageMaison", parametres2["x"], parametres2["y"], 2, "Bas", carteQuittee="InterieurMaison")
            self._lancerTrajet("Aucune", True)
            self._etapeTraitement += 1

    def onChangementCarte(self, carteQuittee, carteEntree):
        self.__dict__["_pnj"].onChangementCarte(carteQuittee, carteEntree)

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        self.__dict__["_pnj"]._onJoueurInteractionQuelconque(x, y, c, direction)

class ObjetAPoser(EvenementConcret):
    def __init__(self, jeu, gestionnaire, bloc, *parametresPose1, **parametresPose2):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._objetPose, self._objetVisible, self._poseBloc, self._parametresPose1, self._parametresPose2 = False, False, bloc, parametresPose1, parametresPose2

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._objetPose is False and self._posePossible(initiale=True):
            self._objetPose, self._objetVisible = True, True
            self._actionPose(initiale=True)
            self._actionsApresPose(initiale=True)

    def _actionPose(self, initiale=False):
        if self._poseBloc:
            self._boiteOutils.changerBloc(*self._parametresPose1, **self._parametresPose2)
        else:
            self._jeu.carteActuelle.poserPNJ(*self._parametresPose1, **self._parametresPose2)

    def _posePossible(self, initiale=False):
        return True

    def _actionsApresPose(self, initiale=False):
        pass

    def onChangementCarte(self, carteQuittee, carteEntree):
        self._objetVisible = False

    def traiter(self):
        if self._objetPose and not self._objetVisible and self._posePossible():
            self._objetVisible = True
            self._actionPose()
            self._actionsApresPose()

class TableSquirrel(ObjetAPoser):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire, False, Rect(5 * 32, 5 * 32, 32, 32), 3, Rect(0,0,32,32),  "squirrelDead.png", (0,0,0), "tableSquirrel")

    def _actionsApresPose(self, initiale=False):
        if initiale:
            self._boiteOutils.interrupteurs["squirrelPose"].activer()

class TableNuts(ObjetAPoser):
    def __init__(self, jeu, gestionnaire, x, y):
        super().__init__(jeu, gestionnaire, False, Rect(x * 32, y * 32, 32, 32), 3, Rect(0,0,32,32),  "Gland.png", (0,0,0), "tableGland")

    def _posePossible(self, initiale=False):
        possessionGlands = (self._boiteOutils.variables["NombreGlands"] > 0) if initiale else True
        return possessionGlands and self._boiteOutils.interrupteurs["BeliaRentree"].voir()

    def _actionsApresPose(self, initiale=False):
        if initiale:
            self._boiteOutils.interrupteurs["nutsOnTable"].activer()

class BruiteurPasJoueur(Evenement):
    def __init__(self, jeu, gestionnaire):
        Evenement.__init__(self, jeu, gestionnaire)
        self._cartesGrottes = ["Entree Maison Gods", "Maison Gods"]
        self._xJoueurOld, self._yJoueurOld, self._comptePas, self._nombreSonsJoues = -1, -1, -1, 0

    def traiter(self):
        if self._gestionnaire.nomCarte in self._cartesGrottes:
            if self._gestionnaire.xJoueur != self._xJoueurOld or self._gestionnaire.yJoueur != self._yJoueurOld:
                self._xJoueurOld, self._yJoueurOld = self._gestionnaire.xJoueur, self._gestionnaire.yJoueur
                self._comptePas += 1
                if self._comptePas == 3:
                    self._comptePas, self._nombreSonsJoues = 0, self._nombreSonsJoues + 1
                    self._boiteOutils.jouerSon("CaveSteps", "CaveSteps"+str(self._nombreSonsJoues), volume=0.3)

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
                self._signaleurs[self._jeu.carteActuelle.nom].pop((self._xJoueur[0], self._yJoueur[0]))

class RetourMaisonDream(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        EvenementConcret.__init__(self, jeu, gestionnaire)

    def onJoueurDessus(self, x, y, c, direction):
        if self._boiteOutils.interrupteurs["RetourMaisonDream"].voir():
            self._boiteOutils.ajouterTransformation(True, "Fog", permanente=True)
            self._boiteOutils.jouerSon("Eerie", "Morning Dream2", nombreEcoutes=0, volume=0.4)
            self._boiteOutils.interrupteurs["RetourMaisonDream"].desactiver()


def annulerFog(self):
    self._boiteOutils.retirerTransformation(True, "Fog")
    self._boiteOutils.arreterSonEnFondu("Morning Dream", 1000)
    self._boiteOutils.arreterSonEnFondu("Morning Dream2", 1000)

def retourMaisonDream(self):
    self._boiteOutils.interrupteurs["RetourMaisonDream"].activer()

def sautMaisonGods(self):
    self._boiteOutils.jouerSon("Fall", "Fall joueur")
