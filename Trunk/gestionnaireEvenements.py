# -*-coding:utf-8 -*
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
        return ["ArriveeScholar", "ScholarDevantPorte", "MereAccueil", "TransitionAccueilScholar", 
                "ExplicationsAuFeu","Depart", "ScholarParti", "panneauLu", "cleTrouvee","porteOuverte","MonstreApparition","MonstreDisparu"]

    def _getVariables(self):
        return [("ObjetsHospitaliteTrouves", 5)]

    def _initialiserEvenements(self):
        self._evenements["concrets"]["LD26-Ferme"] = OrderedDict()
        self._evenements["concrets"]["LD26-Foret"] = OrderedDict()
        self._evenements["concrets"]["LD26-Fin"] = OrderedDict()
        if NOM_CARTE_LANCEMENT == "LD26-Ferme":
            self._evenements["concrets"]["LD26-Ferme"]["Joueur"] = [ Joueur(self._jeu, self, 15, 10, 2, fichier="Anna.png"), (12, 24), "Bas"]
        elif NOM_CARTE_LANCEMENT == "LD26-Foret":
            self._evenements["concrets"]["LD26-Foret"]["Joueur"] = [ Joueur(self._jeu, self, 0, 45, 2, fichier="Anna.png"), (0, 45), "Bas"]
        elif NOM_CARTE_LANCEMENT == "LD26-Fin":
            self._evenements["concrets"]["LD26-Fin"]["Joueur"] = [ Joueur(self._jeu, self, 0, 16, 2, fichier="Anna.png"), (0, 16), "Droite"]
        j, self._positionJoueur = self._jeu.joueur, None
        self._xJoueur, self._yJoueur, self._cJoueur, self._directionJoueur, self._appuiValidationJoueur = j.x/32, j.y/32, j.c, j.direction, j.appuiValidation
        self._evenements["abstraits"]["Divers"] = dict()
        self._evenements["abstraits"]["Divers"]["Narrateur"] = Narrateur(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["ModulateurMusique"] = ModulateurMusique(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["AnimateurToucheAction"] = AnimateurToucheAction(self._jeu, self)
        self._evenements["abstraits"]["Divers"]["PanierFleurs"] = PanierFleurs(self._jeu, self)

    def chargerEvenements(self, nomCarte):
        if nomCarte == "LD26-Ferme":
            self._evenements["concrets"]["LD26-Ferme"]["Mere"] = [ Mere(self._jeu, self), (13, 9), "Bas"]
            self._evenements["concrets"]["LD26-Ferme"]["Scholar"] = [Scholar(self._jeu, self), (2, 29), "Haut"]
            self._evenements["concrets"]["LD26-Ferme"]["Sortie"] = [ Teleporteur(self._jeu, self, "LD26-Foret", 0, 45, 2, "Haut", condition="ScholarParti", fonctionAvant="texteTransition", parametresFAvant="So began our journey."), (2, 29), "Aucune"]
        elif nomCarte == "LD26-Foret":
            self._evenements["concrets"]["LD26-Foret"]["Scholar"] = [Scholar2(self._jeu, self), (2, 46), "Gauche"]
            self._evenements["concrets"]["LD26-Foret"]["Panneau"] = [Panneau(self._jeu, self), (2, 28), "Bas"]
            self._evenements["concrets"]["LD26-Foret"]["Porte"] = [Porte(self._jeu, self), (1, 28), "Bas"]
            self._evenements["concrets"]["LD26-Foret"]["Cle1"] = [Cle(self._jeu, self), (39, 40), "Bas"]
            self._evenements["concrets"]["LD26-Foret"]["Cle2"] = [Cle(self._jeu, self), (39, 41), "Bas"]
            self._evenements["concrets"]["LD26-Foret"]["Sortie1"] = [ Teleporteur(self._jeu, self, "LD26-Fin", 0, 16, 2, "Haut", fonctionAvant="texteTransition", parametresFAvant="And it continued, over and over. Until night."), (38, 0), "Aucune"]
            self._evenements["concrets"]["LD26-Foret"]["Sortie2"] = [ Teleporteur(self._jeu, self, "LD26-Fin", 0, 16, 2, "Haut", fonctionAvant="texteTransition", parametresFAvant="And it continued, over and over. Until night."), (39, 0), "Aucune"]
        elif nomCarte == "LD26-Fin":
            self._evenements["concrets"]["LD26-Fin"]["Scholar"] = [Scholar3(self._jeu, self), (2, 16), "Gauche"]
            self._evenements["concrets"]["LD26-Fin"]["Monstre"] = [Monstre(self._jeu, self), (9, 1), "Bas"]
