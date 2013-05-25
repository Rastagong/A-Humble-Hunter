# -*-coding:utf-8 -*
try: #If needed, the _path module must add the path to the Narro directory to sys.path so that the Narro Engine can be imported as a package
    import _path
except:
    pass
from constantes import *
from narro.main import *
from narro.constantes import *
from gestionnaireEvenements import *

if __name__ == "__main__":
    jeu = Narro()
    jeu.inclureGestionnaire(MonGestionnaireEvenements(jeu))
    jeu.executer()
    if REDIRECTION_FICHIER_ERREURS:
        sys.stderr.close()
