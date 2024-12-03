
# <editor-fold desc="Initialisation et variables générales">
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

#fonction retournant la distance entre 2 points grâce à Pythagore
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

#fonction permettant de générer n points uniformément sur une certaine surface, en respectant une distance minimum
def poisson_disc_sampling(distance_minimum, hauteur, largeur, k=50):
    points = []
    taille_de_grille = distance_minimum / math.sqrt(2)
    largeur_de_grille = math.ceil(largeur / taille_de_grille)
    hauteur_de_grille = math.ceil(hauteur / taille_de_grille)
    grille = [[None for _ in range(hauteur_de_grille)] for _ in range(largeur_de_grille)]

    def est_contenu_dans_la_fenetre(x, y):
        return 0 <= x < largeur and 0 <= y < hauteur

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

    # Réaction générale des obstacles à une collision --> effet sur la balle de façon générale
    #def collision(self, balle):
        #pass

# Classe définissant l'obstacle arbre, faisant rebondir la balle
class Arbre(Obstacles):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.nom_image = "Images/img_2.png"
        #ajouter_sprite(self.nom_image, pos_x, pos_y)

    # Override de la fonction collision() du parent
    def collision(self, balle):
        print("Une balle est rentrée dans l'arbre!")

# Classe définissant les bunkers (sable)
class Bunker(Obstacles):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.nom_image = "Images/img.png"
        #ajouter_sprite(self.nom_image, pos_x, pos_y)

    # Override de la fonction collision() du parent
    def collision(self, balle):
        print("Oh non! Un bunker!")
        
class Balle:
    def __init__(self, balle_x, balle_y):
        self.balle_x = balle_x
        self.balle_y = balle_y
        self.direction = [1, 1]
        self.frottement = 0.9888
        self.vitesse = 5

    def deplacer_balle(self):
        if self.vitesse >= 0.1:
            self.balle_x += self.vitesse * self.direction[0]
            self.balle_y += self.vitesse * self.direction[1]
            self.vitesse *= self.frottement
        else:
            self.vitesse = 0

# </editor-fold>

# <editor-fold desc="Déclaration et définitions des constantes/variables spécifiques">
#définition des constantes du jeu
NOMBRE_DE_POINTS = 70
PHI = 1.618
RAYON = 350
NOMBRE_ARBRES = 20
NOMBRE_BUNKERS = 20
DISTANCE_MINIMUM_TEE_DRAPEAU = 800

#défintion des variables et instances de classe
obstacle1 = Obstacles(0, 0)  # TODO: essayer de créer une classe abstraite/virtuelle
points = poisson_disc_sampling(90, 649, 1280, 50)
balle_golf = Balle( 10, 10)


# </editor-fold>

# <editor-fold desc="Fonctions spécifiques au jeu">
# Fonction générant le terrain basé sur une liste de points
def generation_du_terrain(liste_de_points):
    arbres = []
    if NOMBRE_ARBRES <= len(liste_de_points):
        for i in range(NOMBRE_ARBRES):
            index = randint(0, len(liste_de_points) - 1)
            x_pos, y_pos = liste_de_points[index]
            arbre_instance = Arbre(x_pos, y_pos)
            arbres.append(arbre_instance)
            liste_de_points.remove(liste_de_points[index])
    else:
        print("More obstacles are instanced than there are points available.")

    bunkers = []
    if NOMBRE_BUNKERS <= len(liste_de_points):
        for i in range(NOMBRE_BUNKERS):
            index = randint(0, len(liste_de_points) - 1)
            x_pos, y_pos = liste_de_points[index]
            bunker_instance = Bunker(x_pos, y_pos)
            bunkers.append(bunker_instance)
            liste_de_points.remove(liste_de_points[index])
    else:
        print("More obstacles are instanced than there are points available.")

    drapeau_index = randint(0, len(liste_de_points) - 1)
    drapeau = liste_de_points[drapeau_index]
    liste_de_points.remove(liste_de_points[drapeau_index])

    tee_index = randint(0, len(liste_de_points) - 1)
    tee = liste_de_points[tee_index]
    liste_de_points.remove(liste_de_points[tee_index])

    optimal_distance = distance(tee, drapeau)
    while optimal_distance < DISTANCE_MINIMUM_TEE_DRAPEAU and len(liste_de_points) >1:
        print("loop")
        tee_index_prime = randint(0, len(liste_de_points) - 1)
        tee_prime = liste_de_points[tee_index_prime]
        new_distance = distance(tee_prime, drapeau)
        if new_distance > optimal_distance:
            tee_index = tee_index_prime
            tee = tee_prime
            optimal_distance = new_distance
        else:
            print("point discarded")
        liste_de_points.remove(liste_de_points[tee_index])

    return arbres, bunkers, drapeau, tee

# </editor-fold>

# <editor-fold desc="Initialisation du jeu">
terrain = ajouter_sprite("Images/grass_texture.jpg", 0, 0)

liste_arbres, liste_bunkers, drapeau_position, tee_position = generation_du_terrain(points)
continuer = True
# </editor-fold>
pygame.draw.circle(fenetre, (100, 100, 100), (int(balle_golf.balle_x), int(balle_golf.balle_y)), 15)
balle_sprite = ajouter_sprite("Images/balle.png", balle_golf.balle_x, balle_golf.balle_y)
balle_sprite.image = pygame.transform.scale(balle_sprite.image, [40, 30])
obstacle = []
obstacle_sprite = ajouter_sprite("Images/img.png", 200, 200)
obstacle.append(obstacle_sprite)
hit_list = pygame.sprite.spritecollide(balle_sprite, obstacle, False)
if len(hit_list)>0:
    print("Collision detecté")
    if hit_list[0].image == "Images/img.png":
        print("c'est un arbre")

# <editor-fold desc="Boucle de jeu">
while continuer:
    fenetre.fill((0,0,0))
    liste_sprite.draw(fenetre)

    balle_sprite.rect.x = balle_golf.balle_x
    balle_sprite.rect.y = balle_golf.balle_y

    balle_golf.deplacer_balle()

    for point in points:
        pygame.draw.circle(fenetre, (100, 100, 100), (int(point[0]), int(point[1])), 10)
    for arbre in liste_arbres:
        pygame.draw.circle(fenetre, (0, 255, 100), (int(arbre.pos_x), int(arbre.pos_y)), 25)
    for bunker in liste_bunkers:
        pygame.draw.circle(fenetre, (194, 178, 128), (int(bunker.pos_x), int(bunker.pos_y)), 25)
    pygame.draw.circle(fenetre, (255, 0, 0), (int(drapeau_position[0]), int(drapeau_position[1])), 25)
    pygame.draw.circle(fenetre, (0, 0, 190), (int(tee_position[0]), int(tee_position[1])), 25)

    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
# </editor-fold>
