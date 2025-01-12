# <editor-fold desc="Initialisation et variables générales">
import pygame
from pygame.locals import *
import math
import random
from random import randint

# Initialisation de pygame et de la fenêtre de jeu
pygame.init()
pygame.key.set_repeat(30, 30)
fenetre = pygame.display.set_mode((1280, 649), RESIZABLE)
liste_sprite = pygame.sprite.LayeredUpdates()
# </editor-fold>

# <editor-fold desc="Fonctions générales liées à pygame et à la structure du jeu">

def ajouter_sprite(image_nom, rect_x, rect_y):
    '''
    Ajoute un sprite à la fenêtre avec une image et une position donnée.
    :param image_nom: nom du fichier se trouvant dans le directory Images/
    :param rect_x: largeur de l'image
    :param rect_y: hauteur de l'image
    :return: le sprite instancié
    '''
    sprite_ajout = pygame.sprite.Sprite()
    pygame.sprite.Sprite.__init__(sprite_ajout)
    sprite_ajout.image = pygame.image.load(image_nom).convert_alpha()
    sprite_ajout.rect = sprite_ajout.image.get_rect()
    sprite_ajout.rect.x = rect_x
    sprite_ajout.rect.y = rect_y

    # Ajout du sprite à la liste pour le LayeredUpdate
    liste_sprite.add(sprite_ajout)

    return sprite_ajout

def ajouter_texte(police_nom, taille, texte_a_afficher):
    '''
    Ajoute un texte rendu à la fenêtre dans le LayeredUpdate.
    :param police_nom: nom de la police
    :param taille: taille de la police
    :param texte_a_afficher: texte à afficher
    :return: sprite de texte ajouté
    '''
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

def distance(p1, p2):
    '''
    Calcule la distance entre deux points à l'aide du théorème de Pythagore.
    :param p1: point 1 (x1, y1)
    :param p2: point 2 (x2, y2)
    :return: distance entre les deux points
    '''
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def poisson_disc_sampling(distance_minimum, hauteur, largeur, k=50):
    '''
    Génère des points uniformément répartis sur une surface avec une distance minimale entre les points.
    :param distance_minimum: distance minimale entre deux points
    :param hauteur: hauteur de la surface
    :param largeur: largeur de la surface
    :param k: nombre de tentatives pour générer un nouveau point
    :return: liste des points générés
    '''
    points = []
    taille_de_grille = distance_minimum / math.sqrt(2)
    largeur_de_grille = math.ceil(largeur / taille_de_grille)
    hauteur_de_grille = math.ceil(hauteur / taille_de_grille)
    grille = [[None for _ in range(hauteur_de_grille)] for _ in range(largeur_de_grille)]

    #contrôle si le point généré est visible dans la fenêtre de jeu
    def est_contenu_dans_la_fenetre(x, y):
        return 0 <= x < largeur and 0 <= y < hauteur

    def est_valable(point):
        #calcule les indexs de la case actuelle
        gx = int(point[0] / taille_de_grille)
        gy = int(point[1] / taille_de_grille)

        #contrôle les cases environnantes pour un point déjà présent (seulement besoin de contrôler les cases les plus proches)
        for i in range(-2, 3):
            for j in range(-2, 3):
                x_voisin = gx + i
                y_voisin = gy + j
                #contrôle que la case ne soit pas en bord de fenêtre
                if 0 <= x_voisin < largeur_de_grille and 0 <= y_voisin < hauteur_de_grille:
                    #point dans la case voisine
                    voisin = grille[x_voisin][y_voisin]
                    if voisin and distance(point, voisin) < distance_minimum:
                        return False
        return True

    #ajoute un point à la liste des points et à la grille
    def ajouter_point(point):
        points.append(point)
        gx = int(point[0] / taille_de_grille)
        gy = int(point[1] / taille_de_grille)
        grille[gx][gy] = point

    #initialisation du premier point et de la liste de travail (liste active)
    liste_active = []
    point_initial = (random.uniform(0, largeur), random.uniform(0, hauteur))
    ajouter_point(point_initial)
    liste_active.append(point_initial)

    #tant qu'il y a un point dans la liste active
    while liste_active:
        '''
        La boucle prend comme entrée un point aléatoire de la liste active, et essaie de trouver 
        une position pour un nouveau point, satisfaisant la distance minimum
        '''
        point_actuel = random.choice(liste_active)
        trouve = False

        for _ in range(k):
            #coordonnées polaires aléatoires
            angle = random.uniform(0, math.pi * 2)
            rayon = random.uniform(distance_minimum, 2 * distance_minimum)
            nouveau_point = (point_actuel[0] + rayon * math.cos(angle), point_actuel[1] + rayon * math.sin(angle))

            #contrôle la validité du nouveau point
            if est_contenu_dans_la_fenetre(*nouveau_point) and est_valable(nouveau_point):
                ajouter_point(nouveau_point)
                liste_active.append(nouveau_point)
                trouve = True
                break

        if not trouve:
            #considère qu'il n'y a pas de point disponible
            liste_active.remove(point_actuel)

    return points

# </editor-fold>

# <editor-fold desc="Déclaration des classes">

class Obstacles(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, liste_des_sprites):
        super().__init__()  # Appel obligatoire
        self.image = pygame.image.load("Images/img_2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, [55, 55])
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.pos_x = pos_x
        self.pos_y = pos_y
        liste_des_sprites.add(self)

    def collision(self):
        return True

class Arbre(Obstacles):
    '''
    Classe pour l'obstacle "arbre".
    '''
    def __init__(self, pos_x, pos_y, liste_des_sprites):

        super().__init__(pos_x, pos_y, liste_des_sprites)
        self.image = pygame.image.load("Images/arbre.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image, [55, 55])
        # ajouter_sprite(self.nom_image, pos_x, pos_y)

   

    def collision(self, balle, sprite):
        if sprite.rect.x <= balle.balle_x <= sprite.rect.x + sprite.rect.height:
            balle.direction[1] = -balle.direction[1]
            print("reverted x")
        if sprite.rect.y <= balle.balle_y <= sprite.rect.y + sprite.rect.width:
            balle.direction[0] = -balle.direction[0]
            print("reverted y")
        super().collision()

class Bunker(Obstacles):
    '''
    Classe pour l'obstacle "bunker".
    '''
    def __init__(self, pos_x, pos_y, liste_des_sprites):
        super().__init__(pos_x, pos_y, liste_des_sprites)
        self.image = pygame.image.load("Images/sable_image.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, [55, 55])

    def collision(self, balle):
        balle.frottement = 0.95
        print("Oh non! Un bunker!")
        super().collision()

class Balle:
    '''
    Classe pour la balle de golf.
    '''
    def __init__(self, balle_x, balle_y):
        self.balle_x = balle_x
        self.balle_y = balle_y
        self.direction = [1, 1]
        self.frottement = 0.9888
        self.vitesse = 0
        self.collision = False

    def deplacer_balle(self):
        if self.vitesse >= 0.1:
            self.balle_x += self.vitesse * self.direction[0]
            self.balle_y += self.vitesse * self.direction[1]
            self.vitesse *= self.frottement
        else:
            self.vitesse = 0


#ajout de la barre qui nous indique la puissance
image_puissance = pygame.image.load("Images/barre_puissance.jpg").convert_alpha()
image_puissance = pygame.transform.scale(image_puissance, [20, 100])

position_barre = (90, 440)



class Drapeau(Obstacles):
    '''
    Classe pour l'obstacle "drapeau".
    '''
    def __init__(self, pos_x, pos_y, liste_des_sprites):
        super().__init__(pos_x, pos_y, liste_des_sprites)


    def collision(self):
        print("Fin du jeu!")


# </editor-fold>

# <editor-fold desc="Déclaration des constantes/variables spécifiques">

NOMBRE_DE_POINTS = 70
PHI = 1.618
RAYON = 350
NOMBRE_ARBRES = 25
NOMBRE_BUNKERS = 5
DISTANCE_MINIMUM_TEE_DRAPEAU = 500
VITESSE_ANGULAIRE = .0025
FORCE_MINIMUM = 1

points = poisson_disc_sampling(90, 620, 1250, 50)
game_state = -2 #gère l'action actuelle --> visée = 0, force = 1, mouvement = 2
alpha = 0
hauteur_force = 50
direction_aléatoire = [0, 0]
force_aléatoire = 0
nombre_de_tirs = 0
balle_golf = Balle(10, 10)

# </editor-fold>

# <editor-fold desc="Fonctions spécifiques au jeu">

def generation_du_terrain(liste_de_points):
    '''
    Génère le terrain en fonction d'une liste de points.
    '''
    arbres = []
    if NOMBRE_ARBRES <= len(liste_de_points):
        for _ in range(NOMBRE_ARBRES):
            index = randint(0, len(liste_de_points) - 1)
            x_pos, y_pos = liste_de_points[index]
            arbre_instance = Arbre(x_pos, y_pos, liste_sprite)
            arbres.append(arbre_instance)
            liste_de_points.remove(liste_de_points[index])

    bunkers = []
    if NOMBRE_BUNKERS <= len(liste_de_points):
        for _ in range(NOMBRE_BUNKERS):
            index = randint(0, len(liste_de_points) - 1)
            x_pos, y_pos = liste_de_points[index]
            bunker_instance = Bunker(x_pos, y_pos, liste_sprite)
            bunkers.append(bunker_instance)
            liste_de_points.remove(liste_de_points[index])

    drapeau_index = randint(0, len(liste_de_points) - 1)
    drapeau = liste_de_points[drapeau_index]
    drapeau_sprite = Drapeau(drapeau[0], drapeau[1], liste_sprite)
    liste_de_points.remove(liste_de_points[drapeau_index])

    tee_index = randint(0, len(liste_de_points) - 1)
    tee = liste_de_points[tee_index]
    liste_de_points.remove(liste_de_points[tee_index])

    optimal_distance = distance(tee, drapeau)
    while optimal_distance < DISTANCE_MINIMUM_TEE_DRAPEAU and len(liste_de_points) > 2:
        tee_index_prime = randint(0, len(liste_de_points) - 1)
        tee_prime = liste_de_points[tee_index_prime]
        new_distance = distance(tee_prime, drapeau)
        if new_distance > optimal_distance:
            tee_index = tee_index_prime
            tee = tee_prime
            optimal_distance = new_distance
        liste_de_points.remove(liste_de_points[tee_index_prime])

    return arbres, bunkers, drapeau_sprite, tee

# </editor-fold>

# <editor-fold desc="Initialisation du jeu">
terrain = ajouter_sprite("Images/grass_texture.jpg", 0, 0)
compteur = ajouter_texte(None, 100, f"{nombre_de_tirs}")
compteur.rect.centerx = 100
compteur.rect.centery = 100

liste_arbres, liste_bunkers, drapeau_sprite, tee_position = generation_du_terrain(points)
continuer = True
balle_golf.balle_x = tee_position[0]
balle_golf.balle_y = tee_position[1]
balle_sprite = ajouter_sprite("Images/balle.png", balle_golf.balle_x, balle_golf.balle_y)
balle_sprite.image = pygame.transform.scale(balle_sprite.image, [40, 30])

balle_sprite.rect = balle_sprite.image.get_rect()
obstacles = liste_arbres + liste_bunkers

obstacles.append(drapeau_sprite)

# </editor-fold>


# <editor-fold desc="Boucle de jeu">
texte_demarrage = ajouter_texte(None, 100, "Appuyez sur espace pour démarrer: espace pour viser, espace pour tirer")
texte_fin = ajouter_texte(None, 100, f"Fin du jeu ! Score : {nombre_de_tirs}")
liste_sprite.remove((texte_fin))

while continuer:
    fenetre.fill((0, 0, 0))

    if game_state >=0:
        liste_sprite.draw(fenetre)
        if game_state == 2 and balle_golf.vitesse == 0:
            direction_aléatoire = [0, 0]
            force_aléatoire = 0
            game_state = 0

        balle_sprite.rect.centerx = balle_golf.balle_x
        balle_sprite.rect.centery = balle_golf.balle_y
        if 0 > balle_golf.balle_x or balle_golf.balle_x > fenetre.get_rect().width:
            balle_golf.direction[0] *= -1
        if 0 > balle_golf.balle_y or balle_golf.balle_y> fenetre.get_rect().height:
            balle_golf.direction[1] *= -1
        balle_golf.deplacer_balle()


        fenetre.blit(image_puissance, position_barre)



        hit_list = pygame.sprite.spritecollide(balle_sprite, obstacles, False)

        if len(hit_list) > 0:


            if balle_golf.collision ==False:
                print("Collision detectée")
                if type(hit_list[0]) == Arbre:
                    balle_golf.collision = hit_list[0].collision(balle_golf, hit_list[0])
                    print("C'est un arbre !")
                if type(hit_list[0]) == Bunker:
                    balle_golf.collision = hit_list[0].collision(balle_golf)

                    print("C'est un bunker !")
            if type(hit_list[0]) == Drapeau:
                print("collision drapeau")
                hit_list[0].collision()
                game_state = -1
                liste_sprite.add(texte_fin)

        else:
            balle_golf.collision = False
            balle_golf.frottement = 0.988
        match game_state:
            case 0:
                if alpha < 360:
                    alpha += VITESSE_ANGULAIRE
                else:
                    alpha = 0

                visee_x = math.cos(alpha)
                visee_y = math.sin(alpha)

                direction_aléatoire = [visee_x, visee_y]
            case 1:
                force_y = 0

                if alpha < 360:
                    force_y = math.sin(alpha)
                    alpha += VITESSE_ANGULAIRE
                else:
                    alpha = 0

                force_aléatoire = (force_y + 1) / 2

        #pygame.draw.circle(fenetre, (0, 0, 190), (balle_golf.balle_x + direction_aléatoire[0] * 50, balle_golf.balle_y + direction_aléatoire[1] * 50), 10)
        #pygame.draw.circle(fenetre, (0, 0, 190), (fenetre.get_rect().bottomleft[0] + 100, fenetre.get_rect().bottomleft[1] - hauteur_force * force_aléatoire * 2 + 1 - 100), 10)
        pygame.draw.line(fenetre,(255,0,0), (balle_golf.balle_x, balle_golf.balle_y), (balle_golf.balle_x + direction_aléatoire[0] * 50, balle_golf.balle_y + direction_aléatoire[1] * 50),3)
        pygame.draw.line(fenetre, (255, 0, 0), (fenetre.get_rect().bottomleft[0] + 90, fenetre.get_rect().bottomleft[1] - hauteur_force * force_aléatoire * 2 + 1 - 110), (fenetre.get_rect().bottomleft[0] + 110, fenetre.get_rect().bottomleft[1] - hauteur_force * force_aléatoire * 2 + 1 - 110), 5)
        police = pygame.font.Font(None, 100)
        compteur.image = police.render(f"{nombre_de_tirs}", 1, (255, 255, 255))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                continuer = False
            elif event.type == pygame.KEYUP:
                if event.key == K_SPACE:
                    if game_state < 3:
                        if game_state == 1:

                            balle_golf.direction = direction_aléatoire
                            balle_golf.vitesse = FORCE_MINIMUM + force_aléatoire * 2.7
                            nombre_de_tirs += 1

                        game_state += 1
    elif game_state == -2:
        liste_sprite.draw(fenetre)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                continuer = False
            elif event.type == pygame.KEYUP:
                if event.key == K_SPACE:
                    game_state = 0
                    liste_sprite.remove(texte_demarrage)

    elif game_state == -1:
        liste_sprite.draw(fenetre)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                continuer = False
# </editor-fold>
