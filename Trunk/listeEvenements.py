# -*-coding:utf-8 -*
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

class Narrateur(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._penseePossible, self._etape, self._coefNoircisseur = InterrupteurInverse(self._boiteOutils.penseeAGerer), 0, 1
        self._debut = False
    
    def traiter(self):
        x, y = self._gestionnaire.xJoueur, self._gestionnaire._yJoueur
        if self._boiteOutils.nomCarte == "LD26-Ferme":
            if self._etape == 0 and self._penseePossible.voir() is True:
                self._boiteOutils.ajouterPensee("At first, that day had started like all the other days.")
                self._boiteOutils.ajouterPensee("From dawn to twilight, we worked in pain at Dullhill Farm.")
                self._boiteOutils.ajouterPensee("Mother was taking care of the fruit trees.")
                self._boiteOutils.ajouterPensee("I was picking up red flowers to sell them at the market.")
                self._etape += 1
            if self._etape == 1 and self._penseePossible.voir() is True and self._boiteOutils.variables["NombreFleursRouges"] == 0:
                self._boiteOutils.ajouterPensee("And then I heard some steps, His steps.")
                self._boiteOutils.interrupteurs["ArriveeScholar"].activer()
                self._etape += 1
            if self._etape == 2 and self._boiteOutils.interrupteurs["TransitionAccueilScholar"].voir() is True and x >= 7 and x <= 16 and y >= 7 and y <= 12:
                self._boiteOutils.ajouterPensee("And it all started. We had met a scholar from the capital.")
                Horloge.initialiser(id(self), "Transition", 800)
                self._etape += 1
            if self._etape == 3:
                if Horloge.sonner(id(self),"Transition") is False:
                    self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
                    self._coefNoircisseur += 0.5
                    self._boiteOutils.mettreToutAChanger()
                else:
                    self._etape += 1
            if self._etape == 4 and self._penseePossible.voir() is True:
                self._boiteOutils.retirerTransformation(True, "Noir")
                self._boiteOutils.ajouterTransformation(True,"RemplirNoir")
                self._boiteOutils.ajouterTransformation(True, "SplashText1", texte="A Scholar", antialias=True, couleurTexte=(255,255,255), couleurFond=(0,0,0), position=(0,0))
                self._boiteOutils.ajouterTransformation(True, "SplashText2", texte="In The", antialias=True, couleurTexte=(255,255,255), couleurFond=(0,0,0), position=(0,FENETRE["largeurFenetre"]/4))
                self._boiteOutils.ajouterTransformation(True, "SplashText3", texte="Woods", antialias=True, couleurTexte=(255,255,255), couleurFond=(0,0,0), position=(0,FENETRE["largeurFenetre"]/2))
                self._boiteOutils.joueurLibre.desactiver()
                self._boiteOutils.interrupteurs["ExplicationsAuFeu"].activer()
                self._boiteOutils.changerBloc(13, 10, 1, "TilesetLD26.png", (0, 160, 32, 32), (0,0,0), False)
                self._boiteOutils.teleporterJoueurSurPosition(13, 11, "Haut")
                self._boiteOutils.mettreToutAChanger()
                Horloge.initialiser(id(self), "FinTransition", 3000)
                #jouerMusiqueOuJingle
                self._etape += 1
            if self._etape == 5 and Horloge.sonner(id(self), "FinTransition") is True:
                self._boiteOutils.joueurLibre.activer()
                self._boiteOutils.retirerTransformation(True, "RemplirNoir")
                self._boiteOutils.retirerTransformation(True, "SplashText1")
                self._boiteOutils.retirerTransformation(True, "SplashText2")
                self._boiteOutils.retirerTransformation(True, "SplashText3")
                self._boiteOutils.mettreToutAChanger()
                self._boiteOutils.ajouterPensee("Mother: Anna, could you please get some logs and water for our guest?")
                self._gestionnaire.evenements["concrets"]["LD26-Ferme"]["Log1"] = [ObjetHospitalite(self._jeu, self._gestionnaire, "Log1", 1, 1, 1), (1,1), "Bas"]
                self._gestionnaire.evenements["concrets"]["LD26-Ferme"]["Log2"] = [ObjetHospitalite(self._jeu, self._gestionnaire, "Log2", 2, 1, 1), (2,1), "Bas"]
                self._gestionnaire.evenements["concrets"]["LD26-Ferme"]["Log3"] = [ObjetHospitalite(self._jeu, self._gestionnaire, "Log3", 1, 2, 1), (1,2), "Bas"]
                self._gestionnaire.evenements["concrets"]["LD26-Ferme"]["Log4"] = [ObjetHospitalite(self._jeu, self._gestionnaire, "Log4", 2, 2, 1), (2,2), "Bas"]
                self._gestionnaire.evenements["concrets"]["LD26-Ferme"]["Dwell"] = [ObjetHospitalite(self._jeu, self._gestionnaire, "Dwell", 6, 1, 1), (6,1), "Bas"]
                self._etape += 1
        if self._boiteOutils.nomCarte == "LD26-Foret":
            if self._debut == False:
                self._debut = True
                self._etape = 1
            if self._etape == 1:
                self._boiteOutils.jouerSon("Birds", "Birds Passage Secret", nombreEcoutes=0, fixe=True, xFixe=42, yFixe=22)
                self._boiteOutils.ajouterPensee("Hurry up, country girl. I can't stand the wilderness.")
                self._boiteOutils.ajouterPensee("Neither your tastes, for that matter. Ever heard of minimalism?")
                self._boiteOutils.ajouterPensee("Of course you haven't... Your \"traditional\" works of art are far poorer.")
                self._boiteOutils.ajouterPensee("Your songs, dances and farces… They're so meaningless. So childish.")
                self._boiteOutils.ajouterPensee("I truly pity you. I couldn't live without true art, without minimalism.")
                self._boiteOutils.ajouterPensee("At the capital, our artists are highly regarded. Their thoughts are profound.")
                self._boiteOutils.ajouterPensee("Someone should do something about you countrymen. Teach you what art is.")
                self._boiteOutils.ajouterPensee("One can write a play without any violence, you know? It's much better.")
                self._boiteOutils.ajouterPensee("That's what The Minimalist Manifesto says. \"Popular art needs to grow up…")
                self._boiteOutils.ajouterPensee("It needs to grow into a pure, true, minimal simplicity.\"")
                self._boiteOutils.ajouterPensee("Understand what it means? *Sigh* Someday, maybe. I have hope for you.")
                self._boiteOutils.ajouterPensee("It seems we're stuck, country girl. You should go and check that panel.", tempsLecture=0)
                self._etape += 1
            if self._etape == 2 and self._boiteOutils.interrupteurs["porteOuverte"].voir() is True:
                self._boiteOutils.ajouterPensee("Oh, you made it. Good for you. Good for me too. Let's go forward.")
                self._boiteOutils.ajouterPensee("I'm quite surprised by your abilities. You've got some capacities.")
                self._boiteOutils.ajouterPensee("If you were less stubborn, you could work with a minimalist artist.")
                self._boiteOutils.ajouterPensee("I'm not kidding. As an apprentice. But I guess you prefer your countryside.")
                self._boiteOutils.ajouterPensee("I'm tired of waiting. I'll just follow you.")
                self._etape += 1
        if self._boiteOutils.nomCarte == "LD26-Fin":
            if self._debut == False or (self._debut == True and self._etape == 3):
                self._debut = 2
                self._etape = 1
            if self._etape == 1:
                self._boiteOutils.ajouterPensee("What is this place? It looks dismal, wild and scary. Just like you.")
                self._boiteOutils.ajouterPensee("- It's a sanctuary, Sir. For our Gods.")
                self._boiteOutils.ajouterPensee("- Of course. I had forgotten how naive you are.")
                self._boiteOutils.ajouterPensee("- You shouldn't offend them.")
                self._boiteOutils.ajouterPensee("- Duh! Your \"Gods\" are an instrument of power that some men use to contr…", nom="Attaque")
                self._boiteOutils.ajouterPensee("What was that?", tempsLecture=700)
                self._boiteOutils.ajouterPensee("There are no monsters around here, right, country gi...?")
                self._etape += 1
            if self._etape == 2 and self._boiteOutils.getNomPensee() == "Attaque" and self._boiteOutils.getMotPenseeActuelle() == 59:
                self._coefNoircisseur = 0
                self._boiteOutils.ajouterTransformation(True,"Noir", coef=self._coefNoircisseur)
                Horloge.initialiser(id(self),"Transi", 800)
                self._etape += 1
            if self._etape == 3:
                self._coefNoircisseur += 0.5
                self._boiteOutils.ajouterTransformation(True,"Noir", coef=self._coefNoircisseur)
                if Horloge.sonner(id(self),"Transi") is True:
                    self._etape += 1
            if self._etape == 4:
                self._boiteOutils.retirerTransformation(True,"Noir")
                self._boiteOutils.ajouterTransformation(True,"Nuit")
                self._boiteOutils.mettreToutAChanger()
                self._boiteOutils.interrupteurs["MonstreApparition"].activer()
                self._etape += 1
            if self._etape == 5 and self._boiteOutils.interrupteurs["MonstreDisparu"].voir() is True:
                self._boiteOutils.retirerTransformation(True,"Nuit")
                self._boiteOutils.supprimerPNJ("Monstre",2)
                self._boiteOutils.supprimerPNJ("Scholar",2)
                self._gestionnaire.ajouterEvenementATuer("concrets","LD26-Fin","Scholar")
                self._boiteOutils.changerBloc(9, 8, 1, "TilesetLD26.png", (64,288,32,32), (0,0,0), False)
                Horloge.initialiser(id(self),"TheEnd",2000)
                self._boiteOutils.mettreToutAChanger()
                self._etape += 1
            if self._etape == 6 and Horloge.sonner(id(self),"TheEnd"):
                self._boiteOutils.ajouterTransformation(True, "SplashText1", texte="The End", antialias=True, couleurTexte=(255,255,255),  position=(0,0))
                self._etape += 1


class ObjetHospitalite(EvenementConcret):
    def __init__(self, jeu, gestionnaire, nom, xTile, yTile, c):
        super().__init__(jeu, gestionnaire)
        self._nom, self._objetTrouve, self._xTile, self._yTile, self._c = nom, False, xTile, yTile, c

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._objetTrouve == False:
            self._objetTrouve = True
            if "Log" in self._nom:
                self._boiteOutils.changerBloc(self._xTile, self._yTile, self._c, -1, -1, -1, -1, vide=True)
                self._boiteOutils.jouerSon("Ouverture","Log")
            else:
                self._boiteOutils.jouerSon("Blip","Dwell")
            self._gestionnaire.ajouterEvenementATuer("concrets", "LD26-Ferme", self._nom)
            self._boiteOutils.variables["ObjetsHospitaliteTrouves"] -= 1

class PanierFleurs(Evenement):
    def __init__(self, jeu, gestionnaire):
        self._etape = 0
        super().__init__(jeu, gestionnaire)

    def traiter(self):
        if self._etape == 0:
            self._tilesFleurs, i = self._boiteOutils.determinerPresenceTilesSurCarte(1, "TilesetLD26.png", (64, 224, 32, 32)), 0
            for tileFleur in self._tilesFleurs:
                self._gestionnaire.evenements["concrets"]["LD26-Ferme"]["Fleur" + str(i)] = [FleurRouge(self._jeu, self._gestionnaire, "Fleur" + str(i), tileFleur[0], tileFleur[1], 1), (tileFleur[0], tileFleur[1]), "Bas"]
                i += 1
            self._boiteOutils.variables["NombreFleursRouges"] = len(self._tilesFleurs)
            self._etape += 1
        if self._etape == 1 and self._boiteOutils.variables["NombreFleursRouges"] == 0:
            self._gestionnaire.ajouterEvenementATuer("abstraits","Divers","PanierFleurs")
            self._etape += 1


class FleurRouge(EvenementConcret):
    def __init__(self, jeu, gestionnaire, nom, xTile, yTile, c):
        super().__init__(jeu, gestionnaire)
        self._nom, self._fleurTrouvee, self._xTile, self._yTile, self._c = nom, False, xTile, yTile, c

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._fleurTrouvee == False:
            self._fleurTrouvee = True
            self._boiteOutils.changerBloc(self._xTile, self._yTile, self._c, -1, -1, -1, -1, vide=True)
            self._boiteOutils.variables["NombreFleursRouges"] -= 1
            self._gestionnaire.ajouterEvenementATuer("concrets","LD26-Ferme",self._nom)
            self._boiteOutils.jouerSon("Blip","FleurRouge")

class Mere(PNJ):
    def __init__(self, jeu, gestionnaire):
        x, y, c = 13, 9, 2
        fichier, couleurTransparente, persoCharset, vitesseDeplacement = "Mother.png", (0,0,0), (0,0), 150
        repetitionActions, directionDepart = False, "Bas"
        listeActions = ["Gauche","Gauche","VHaut2500","Gauche","Haut","Haut","Droite","VDroite2500","Gauche","Gauche","Gauche","Gauche","Gauche","Gauche","VGauche2500", "Haut", "Droite","VBas2500","Haut","Haut","Haut","Haut"]
        super().__init__(jeu, gestionnaire, "Mere", x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement)

    def _gererEtape(self):
        if self._etapeTraitement == 1:
            if self._etapeAction == 3:
                self._boiteOutils.changerBloc(11, 8, 1, -1, -1, -1, -1, vide=True)
            if self._etapeAction >= 9 and self._etapeAction <= 14:
                self._boiteOutils.changerBloc(self._xTilePrecedent, self._yTilePrecedent, 3, "TilesetLD26.png", (32, 320, 32, 32), (0,0,0), True)
            elif self._etapeAction == 15:
                self._boiteOutils.changerBloc(5, 7, 3, "TilesetLD26.png", (32, 320, 32, 32), (0,0,0), True)
                self._boiteOutils.changerBloc(4, 7, 3, "TilesetLD26.png", (0, 320, 32, 32), (0,0,0), True)
            elif self._etapeAction == 18:
                self._boiteOutils.changerBloc(6, 7, 3, "TilesetLD26.png", (64, 320, 32, 32), (0,0,0), True)
            elif self._etapeAction == 19:
                self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._etapeAction == 22:
            self._lancerTrajet(["VHaut2500","Droite","Droite","Droite","Droite","Droite","Droite","Droite","Droite","Droite","VHaut2500","Droite","Droite","Droite","Bas","Bas","VGauche2500","Bas","Bas","Bas","Bas","Bas","Bas","Bas","Bas","Bas","VGauche2500","Bas","Gauche","Gauche","Gauche","Gauche","Haut","Gauche","Gauche","Gauche","Gauche","Gauche","Gauche","Gauche","Gauche","Haut","Haut","Haut","Haut","Haut","Haut","Haut","Haut","Haut","Haut","Haut"], True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 3 and self._boiteOutils.interrupteurs["ScholarDevantPorte"].voir() is True and self._etapeMarche == 1:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 14, 9, arretAvant=True, regardAvant=True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 4 and self._boiteOutils.positionProcheEvenement(self._xTile, self._yTile, "Scholar") and self._deplacementBoucle is False:
            self._boiteOutils.interrupteurs["MereAccueil"].activer()
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and self._boiteOutils.interrupteurs["ExplicationsAuFeu"].voir() is True:
            self._seTeleporter(12, 11, "Droite")
            self._lancerTrajet(["VDroite5000","Haut","RDroite"], False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 6 and self._boiteOutils.variables["ObjetsHospitaliteTrouves"] == 0:
            self._majInfosJoueur(0)
            if self._joueurProche is True:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 3, 28, regardFinal="Gauche")
                self._boiteOutils.ajouterPensee("Scholar: Thank you, young lady. Now, come, we must tell you something.")
                self._etapeTraitement += 1
        if self._etapeTraitement == 7 and self._xTile == 3 and self._yTile == 28 and self._deplacementBoucle is False:
            self._lancerTrajet(["VGauche200"], True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 8:
            self._majInfosJoueur(0)
            if self._joueurProche is True:
                self._finirDeplacementSP()
                self._lancerTrajet(self._boiteOutils.regardVersPnj("Joueur", self._xTile, self._yTile), False)

class Scholar(PNJ):
    def __init__(self, jeu, gestionnaire):
        x, y, c = 2, 29, 2
        fichier, couleurTransparente, persoCharset, vitesseDeplacement = "Savant.png", (0,0,0), (0,0), 150
        self._annonceProjet = False
        repetitionActions, directionDepart, intelligence, poseDepart, listeActions = False, "Bas", True, False, []
        super().__init__(jeu, gestionnaire, "Scholar", x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement, intelligence=intelligence, poseDepart=poseDepart)
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def _gererEtape(self):
        if self._etapeTraitement == 0 and self._boiteOutils.interrupteurs["ArriveeScholar"].voir() is True:
           self._poseDepart = True
        if self._etapeTraitement == 1 and self._deplacementBoucle is False:
           self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 14, 9, regardFinal="Haut")
           self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._deplacementBoucle is False and self._xTile == 14 and self._yTile == 9:
            self._boiteOutils.jouerSon("tocPorte","Porte") 
            self._boiteOutils.interrupteurs["ScholarDevantPorte"].activer()
            self._etapeTraitement += 1
        if self._etapeTraitement == 3 and self._boiteOutils.interrupteurs["MereAccueil"].voir() is True:
            self._lancerTrajet( self._boiteOutils.regardVersPnj("Mere", self._xTile, self._yTile), False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 4 and self._deplacementBoucle is False:
            self._lancerTrajet(["V"+self._directionRegard+str(5000)], False)
            self._boiteOutils.ajouterPensee("???: Now, that's what I call the countryside.")
            self._boiteOutils.ajouterPensee("You must be one of these poor farmers, aren't you, Madam?")
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and self._penseePossible.voir() is True:
            self._boiteOutils.interrupteurs["TransitionAccueilScholar"].activer()
            self._etapeTraitement += 1
        if self._etapeTraitement == 6 and self._boiteOutils.interrupteurs["ExplicationsAuFeu"].voir() is True:
            self._seTeleporter(13, 9, "Bas")
            self._etapeTraitement += 1
        if self._etapeTraitement == 7 and self._boiteOutils.variables["ObjetsHospitaliteTrouves"] == 0:
            self._majInfosJoueur(0)
            if self._joueurProche is True:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 2, 28, regardFinal="Droite")
                self._etapeTraitement += 1
        if self._etapeTraitement == 8 and self._xTile == 2 and self._yTile == 28 and self._deplacementBoucle is False:
            self._lancerTrajet(["VDroite200"], True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 9:
            self._majInfosJoueur(0)
            if self._joueurProche == True:
                self._finirDeplacementSP()
                self._lancerTrajet(self._boiteOutils.regardVersPnj("Joueur", self._xTile, self._yTile), False)
                if self._annonceProjet is False:
                    self._annonceProjet = True
                    self._boiteOutils.ajouterPensee("I need you to guide me through the woods.")
                    self._boiteOutils.ajouterPensee("I've got to meet some brilliant artists you've never heard of,")
                    self._boiteOutils.ajouterPensee("far from here, where you've never been. Let's go, now!")
            if self._annonceProjet is True and self._penseePossible.voir() is True:
                self._boiteOutils.interrupteurs["Depart"].activer()
                self._finirDeplacementSP()
                self._etapeTraitement += 1
        if self._etapeTraitement == 10:
            self._finirDeplacementSP()
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 2, 29, regardFinal="Bas")
            self._etapeTraitement += 1
        if self._etapeTraitement == 11 and self._xTile == 2 and self._yTile == 29 and self._deplacementBoucle is False:
            self._boiteOutils.interrupteurs["ScholarParti"].activer()
            self._boiteOutils.supprimerPNJ(self._nom, self._c)
            self._etapeTraitement += 1

class Scholar2(PNJ):
    def __init__(self, jeu, gestionnaire):
        x, y, c = 2, 46, 2
        fichier, couleurTransparente, persoCharset, vitesseDeplacement = "Savant.png", (0,0,0), (0,0), 120
        repetitionActions, directionDepart, intelligence, listeActions = False, "Gauche", True, ["VGauche2500"]
        super().__init__(jeu, gestionnaire, "Scholar", x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement, intelligence=intelligence)
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)
        self._pensee1, self._pensee2, self._pensee3, self._coince = False, False, False, False

    def _gererEtape(self):
        if self._etapeTraitement == 1 and self._deplacementBoucle is False:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 22, 40, typeTile=[("TilesetLD26.png", (64, 0, 32, 32))])
            self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._deplacementBoucle is False and self._xTile == 22 and self._yTile == 40:
            self._majInfosJoueur(0)
            if self._joueurProche is True:
                self._lancerTrajet(self._boiteOutils.regardVersPnj("Joueur", self._xTile, self._yTile), False)
            if self._boiteOutils.interrupteurs["porteOuverte"].voir() is True:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 1, 29, typeTile=[("TilesetLD26.png", (64, 0, 32, 32))])
                self._etapeTraitement += 1
        if self._etapeTraitement == 3 and self._xTile == 1 and self._yTile == 29 and self._deplacementBoucle is False:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 5, 23, regardFinal="Bas")
            self._etapeTraitement += 1
        if self._etapeTraitement == 4 and self._xTile == 5 and self._yTile == 23 and self._deplacementBoucle is False:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._xTile, self._yTile, self._c)
            self._etapeTraitement += 1
        if self._etapeTraitement == 5:
            self._majInfosJoueur()
            if self._joueurBouge[0] is True and self._etapeMarche == 1 and (not self._coince):
                self._finirDeplacementSP()
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._xTile, self._yTile, self._c)
            elif self._joueurBouge[0] is False and self._joueurProche is False and self._etapeMarche == 1 and self._deplacementBoucle is False and (not self._coince):
                self._finirDeplacementSP()
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._xTile, self._yTile, self._c)
            if self._xJoueur[0] >= 17 and self._xJoueur[0] <= 26 and self._yJoueur[0] >= 24 and self._yJoueur[0] <= 30 and self._pensee1 is False:
                self._pensee1 = True
                self._boiteOutils.ajouterPensee("Well, are we lost again? Funny. Know what I was thinking of?")
                self._boiteOutils.ajouterPensee("I should write an article. \"Minimalism & Popular classes.\"")
                self._boiteOutils.ajouterPensee("I see a great potential there.")
            if self._xJoueur[0] >= 0 and self._xJoueur[0] <= 8 and self._yJoueur[0] >= 13 and self._yJoueur[0] <= 14 and self._pensee2 is False:
                self._pensee2 = True
                self._boiteOutils.ajouterPensee("That's a river, indeed! But we can't go anywhere, there's no bridge.")
                self._boiteOutils.ajouterPensee("It reminds of the gap between your ignorance and my great knowledge.")
            if self._xJoueur[0] >= 43 and self._xJoueur[0] <= 49 and self._yJoueur[0] >= 13 and self._yJoueur[0] <= 20 and self._pensee3 is False:
                self._pensee3 = True
                self._boiteOutils.ajouterPensee("You found our way out, once again! I'm impressed.")
                self._boiteOutils.ajouterPensee("Now, Let's get out of here. I hate these woods.")
            if Horloge.sonner(id(self), "Coince"):
                self._coince = False

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._penseePossible.voir() is True and self._boiteOutils.interrupteurs["panneauLu"].voir() is True and self._boiteOutils.interrupteurs["porteOuverte"].voir() is False:
            self._boiteOutils.ajouterPensee("What? An enigma? Hm, let me check in my books...")
            self._boiteOutils.ajouterPensee("I've always been fascinated by the love of storytelling among poor men.")
            self._boiteOutils.ajouterPensee("Tell them a story, and they will be happy for the day. Fascinating.")
        if self._etapeTraitement == 5 and directions.directionContraire(direction) == self._directionRegard:
            self._finirDeplacementSP()
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 37, 26)
            self._coince = True
            Horloge.initialiser(id(self), "Coince", 3000)


class Scholar3(PNJ):
    def __init__(self, jeu, gestionnaire):
        x, y, c = 2, 16, 2
        fichier, couleurTransparente, persoCharset, vitesseDeplacement = "Savant.png", (0,0,0), (0,0), 120
        repetitionActions, directionDepart, intelligence, listeActions = False, "Gauche", True, []
        super().__init__(jeu, gestionnaire, "Scholar", x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement, intelligence=intelligence)
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def _gererEtape(self):
        if self._etapeTraitement == 1:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 9, 7, regardFinal="Droite")
            self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._xTile == 9 and self._yTile == 7 and self._deplacementBoucle is False and self._etapeMarche == 1:
            self._lancerTrajet(["RBas",1000,"RDroite",1000,"RHaut",1000,"RGauche",1000], True)
            self._etapeTraitement += 1

class Panneau(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def _onJoueurInteractionFace(self, x, y, c, direction):
        if self._penseePossible.voir() is True:
            self._boiteOutils.ajouterPensee("It's a panel. It reads:")
            self._boiteOutils.ajouterPensee("Only those with true children's eyes will pass.")
            self._boiteOutils.ajouterPensee("Forget your knowledge, leave the paths and explore the unknown.")
            self._boiteOutils.ajouterPensee("Do not trust what you see, for the leaves of rationality hide the invisible.")
            self._boiteOutils.ajouterPensee("You will find the key in a golden nest, on a twisted tree.")
        self._boiteOutils.interrupteurs["panneauLu"].activer()

class Cle(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._penseePossible, self._trouve = InterrupteurInverse(self._boiteOutils.penseeAGerer), False

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        if self._trouve == False:
            self._boiteOutils.jouerSon("Blip","FleurRouge")
            self._boiteOutils.interrupteurs["cleTrouvee"].activer()
            self._gestionnaire.ajouterEvenementATuer("concrets", "LD26-Foret", "Cle1")
            self._gestionnaire.ajouterEvenementATuer("concrets", "LD26-Foret", "Cle2")
            self._trouve = True

class Porte(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)

    def _onJoueurInteractionFace(self, x, y, c, direction):
        if self._boiteOutils.interrupteurs["cleTrouvee"].voir() is True:
            self._boiteOutils.changerBloc(1, 28, 2, "TilesetLD26.png", (0, 128, 32, 32), (0,0,0), True)
            self._boiteOutils.changerPraticabilite(1, 28, 1, True)
            self._boiteOutils.mettreToutAChanger()
            self._boiteOutils.jouerSon("Ouverture","Porte")
            self._gestionnaire.ajouterEvenementATuer("concrets", "LD26-Foret", "Porte")
            self._boiteOutils.interrupteurs["porteOuverte"].activer()

class Monstre(PNJ):
    def __init__(self, jeu, gestionnaire):
        x, y, c = 9, 1, 2
        fichier, couleurTransparente, persoCharset, vitesseDeplacement = "YeuxMonstre.png", (0,0,0), (0,0), 150
        repetitionActions, directionDepart, intelligence, listeActions, poseDepart = False, "Gauche", True, [], False
        super().__init__(jeu, gestionnaire, "Monstre", x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, vitesseDeplacement=vitesseDeplacement, intelligence=intelligence, poseDepart=poseDepart)
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def _gererEtape(self):
        if self._etapeTraitement == 0 and self._boiteOutils.interrupteurs["MonstreApparition"].voir() is True:
            self._poseDepart = True
        if self._etapeTraitement == 1 and self._etapeMarche == 1:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._xTile, self._yTile, self._c, 9, 7, arretAvant=True)
            self._boiteOutils.jouerSon("Bete","Bete")
            self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(self._xTile, self._yTile, "Scholar") is True:
            self._boiteOutils.interrupteurs["MonstreDisparu"].activer()
            self._etapeTraitement += 1
