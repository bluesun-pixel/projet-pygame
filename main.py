# <editor-fold desc="Initialisation et variables générales">

from traceback import print_exception
import pygame
from pygame.locals import *
import math
import random
from random import randint


# Initiation de pygame et de la fenêtre de jeu
pygame.init()
pygame.key.set_repeat(30, 30)
fenetre = pygame.display.set_mode((1280, 649), RESIZABLE)
liste_sprite = pygame.sprite.LayeredUpdates()


# </editor-fold>

# <editor-fold desc="Fonctions générales liées à pygame et à la structure du jeu">
# Fonction permettant d'ajouter un sprite automatiquement dans le LayeredUpdate
def ajouter_sprite(image_nom, rect_x, rect_y):
    sprite_ajout = pygame.sprite.Sprite()
    pygame.sprite.Sprite.__init__(sprite_ajout)
    sprite_ajout.image = pygame.image.load(image_nom).convert()
    sprite_ajout.rect = sprite_ajout.image.get_rect()
    sprite_ajout.rect.x = rect_x
    sprite_ajout.rect.y = rect_y
    liste_sprite.add(sprite_ajout)
    return sprite_ajout

# Fonction permettant d'ajouter du texte automatiquement dans le LayeredUpdate
def ajouter_texte(police_nom, taille, texte_a_afficher):
    police = pygame.font.Font(police_nom, taille)
    texte = pygame.sprite.Sprite()
    pygame.sprite.Sprite.__init__(texte)
    liste_sprite.add(texte)

    texte.image = police.render(texte_a_afficher, 1, (10, 10, 10), (255, 90, 20))
    texte.rect = texte.image.get_rect()
    texte.rect.centerx = fenetre.get_rect().centerx
    texte.rect.centery = fenetre.get_rect().centery
    liste_sprite.add(texte)
    return texte

def poisson_disc_sampling(distance_minimum, hauteur, largeur, k=50):
    points = []
    taille_de_grille = distance_minimum / math.sqrt(2)
    largeur_de_grille = math.ceil(largeur / taille_de_grille)
    hauteur_de_grille = math.ceil(hauteur / taille_de_grille)
    grille = [[None for _ in range(hauteur_de_grille)] for _ in range(largeur_de_grille)]

    def est_contenu_dans_la_fenetre(x, y):
        return 0 <= x < largeur and 0 <= y < hauteur

    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def est_valable(point):
        gx = int(point[0] / taille_de_grille)
        gy = int(point[1] / taille_de_grille)

        for i in range(-2, 3):
            for j in range(-2, 3):
                x_voisin = gx + i
                y_voisin = gy + j  # Fix here, should be gy + j instead of gy + i
                if 0 <= x_voisin < largeur_de_grille and 0 <= y_voisin < hauteur_de_grille:
                    voisin = grille[x_voisin][y_voisin]
                    if voisin and distance(point, voisin) < distance_minimum:
                        return False
        return True

    def ajouter_point(point):
        points.append(point)
        gx = int(point[0] / taille_de_grille)
        gy = int(point[1] / taille_de_grille)
        grille[gx][gy] = point

    liste_active = []
    point_initial = (random.uniform(0, largeur), random.uniform(0, hauteur))
    ajouter_point(point_initial)
    liste_active.append(point_initial)

    while liste_active:
        point_actuel = random.choice(liste_active)
        trouve = False

        for i in range(k):
            angle = random.uniform(0, math.pi * 2)
            rayon = random.uniform(distance_minimum, 2 * distance_minimum)
            nouveau_point = (point_actuel[0] + rayon * math.cos(angle), point_actuel[1] + rayon * math.sin(angle))

            if est_contenu_dans_la_fenetre(*nouveau_point) and est_valable(nouveau_point):
                ajouter_point(nouveau_point)
                liste_active.append(nouveau_point)
                trouve = True
                break
        if not trouve:
            liste_active.remove(point_actuel)

    return points
# </editor-fold>

# <editor-fold desc="Déclaration des classes">
# Classe parente dont les obstacles héritent
class Obstacles:
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y

    # Fonction permettant de créer une distribution uniforme en apparence aléatoire dans une sphère
    def distribution(self, nombre_de_points, fraction, rayon):
        points = poisson_disc_sampling(80, 649, 1280)
        print(len(points))
        return points
        #version utilisant la distribution en spirale
        #points = []  # Array contenant une liste de points dans le plan
        #for i in range(nombre_de_points):
        #   distance = pow((i / (nombre_de_points - 1)), 0.5) * rayon
        #   angle = i * fraction * 2 * math.pi
        #   Conversion des coordonnées polaires à cartésiennes
        #   x = math.cos(angle) * distance
        #   y = math.sin(angle) * distance
        #   points.append([x, y])
        #return points

    # Réaction générale des obstacles à une collision --> effet sur la balle de façon générale
    def collision(self, balle):
        pass

# Classe définissant l'obstacle arbre, faisant rebondir la balle
class Arbre(Obstacles):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.nom_image = "Images/img_2.png"
        ajouter_sprite(self.nom_image, pos_x, pos_y)

    # Override de la fonction collision() du parent
    def collision(self, balle):
        super().collision(balle)
        print("Une balle est rentrée dans l'arbre!")

# Classe définissant les bunkers (sable)
class Bunker(Obstacles):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.nom_image = "Images/img.png"
        ajouter_sprite(self.nom_image, pos_x, pos_y)

    # Override de la fonction collision() du parent
    def collision(self, balle):
        super().collision(balle)
        print("Oh non! Un bunker!")

# </editor-fold>

# <editor-fold desc="Déclaration et définitions des constantes/variables spécifiques">
NOMBRE_DE_POINTS = 70
PHI = 1.618
RAYON = 350
NOMBRE_ARBRES = 0
NOMBRE_BUNKERS = 0

obstacle1 = Obstacles(0, 0)  # TODO: essayer de créer une classe abstraite/virtuelle
points = obstacle1.distribution(NOMBRE_DE_POINTS, PHI, RAYON)

# </editor-fold>

# <editor-fold desc="Fonctions spécifiques au jeu">
# Fonction créant une instance d'arbre un certain nombre de fois aléatoirement basé sur une liste de points du plan
def generation_du_terrain(liste_de_points):
    if NOMBRE_ARBRES <= len(liste_de_points):
        for i in range(NOMBRE_ARBRES):
            index = randint(0, len(liste_de_points) - 1)
            x, y = liste_de_points[index]
            # Ensure the obstacles are placed within the screen bounds
            x_pos = fenetre.get_rect().centerx - x * 1.5
            y_pos = fenetre.get_rect().centery - y
            x_pos = max(0, min(fenetre.get_width(), x_pos))  # Clamp x position
            y_pos = max(0, min(fenetre.get_height(), y_pos))  # Clamp y position
            arbre_instance = Arbre(x_pos, y_pos)
            liste_de_points.remove(liste_de_points[index])

    else:
        print("More obstacles are instanced than there are points available.")

# </editor-fold>

# <editor-fold desc="Initialisation du jeu">
terrain = ajouter_sprite("Images/grass_texture.jpg", 0, 0)
generation_du_terrain(points)
continuer = True
# </editor-fold>

# <editor-fold desc="Boucle de jeu">
while continuer:
    liste_sprite.draw(fenetre)
    for point in points:
        pygame.draw.circle(fenetre, (255, 0, 0), (int(point[0]), int(point[1])), 25)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
# </editor-fold>
