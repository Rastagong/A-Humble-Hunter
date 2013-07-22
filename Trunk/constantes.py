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


import pygame
from pygame.locals import *

NOM_CARTE_LANCEMENT = "InterieurMaison"
DOSSIER_RESSOURCES = "Resources"
NOM_FICHIER_POLICE_PAR_DEFAUT = "Riven.ttf"

FENETRE = dict()
FENETRE["messageErreurInitialisationPygame"]="Une erreur s'est produite durant l'initialisation de Pygame, le programme doit donc se fermer." 
FENETRE["messageErreurInitialisationFenetre"]="Une erreur s'est produite durant l'initialisation de la fenêtre, le programme doit donc se fermer." 
FENETRE["longueurFenetre"] = 512
FENETRE["largeurFenetre"] = 384
FENETRE["largeurFenetreReelle"] = 416
FENETRE["couleurFenetre"] = (0,0,0) ##Couleur de fond de la fenêtre (hors zones spéciales comme tileset, outils...)
FENETRE["titreFenetre"] = "A Humble Hunter"
FENETRE["flagsFenetre"] = DOUBLEBUF#|FULLSCREEN|HWSURFACE
FENETRE["forceDirectX"] = False

VITESSE_PENSEE_PAR_DEFAUT = 40
TAILLE_POLICE_PAR_DEFAUT = 16
TEMPS_LECTURE_PENSEE = 2000

FICHIER_ICONE = "Narro.ico"

VITESSE_DEPLACEMENT_FLECHE = 800

NOMBRE_CANAUX_SONS = 20
VOLUME_MUSIQUE = 1.0

VITESSE_DEPLACEMENT_JOUEUR_PAR_DEFAUT = 170
LIMITER_FPS = False
NOMBRE_MAX_DE_FPS = 60

