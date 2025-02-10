####################################################
# N'oubliez pas de mettre du son quand vous lancerez notre jeu ;)
####################################################

# <editor-fold desc="Initialisation et variables générales">
# import des bibliothèques dont on aura besoin
import time
import os, random
import pygame
from pygame.examples.cursors import image
from pygame.locals import *
import math
import random
from random import randint

# Initialisation de pygame, de la fenêtre de jeu et de la musique
pygame.init()
pygame.mixer.init()
path = os.path.dirname(os.path.abspath(__file__)) + "/Musiques"
file = random.choice(os.listdir(path))
pygame.mixer.music.load(f"Musiques/{file}")
pygame.mixer.music.play(-1, 0.0)
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
    # Faire apparaître l'image
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

    # contrôle si le point généré est visible dans la fenêtre de jeu
    def est_contenu_dans_la_fenetre(x, y):
        return 0 <= x < largeur and 0 <= y < hauteur

    def est_valable(point):
        # calcule les indexs de la case actuelle
        gx = int(point[0] / taille_de_grille)
        gy = int(point[1] / taille_de_grille)

        # contrôle les cases environnantes pour un point déjà présent (seulement besoin de contrôler les cases les plus proches)
        for i in range(-2, 3):
            for j in range(-2, 3):
                x_voisin = gx + i
                y_voisin = gy + j
                # contrôle que la case ne soit pas en bord de fenêtre
                if 0 <= x_voisin < largeur_de_grille and 0 <= y_voisin < hauteur_de_grille:
                    # point dans la case voisine
                    voisin = grille[x_voisin][y_voisin]
                    if voisin and distance(point, voisin) < distance_minimum:
                        return False
        return True

    # ajoute un point à la liste des points et à la grille
    def ajouter_point(point):
        points.append(point)
        gx = int(point[0] / taille_de_grille)
        gy = int(point[1] / taille_de_grille)
        grille[gx][gy] = point

    # initialisation du premier point et de la liste de travail (liste active)
    liste_active = []
    point_initial = (random.uniform(0, largeur), random.uniform(0, hauteur))
    ajouter_point(point_initial)
    liste_active.append(point_initial)

    # tant qu'il y a un point dans la liste active
    while liste_active:
        '''
        La boucle prend comme entrée un point aléatoire de la liste active, et essaie de trouver 
        une position pour un nouveau point, satisfaisant la distance minimum
        '''
        point_actuel = random.choice(liste_active)
        trouve = False

        for _ in range(k):
            # coordonnées polaires aléatoires
            angle = random.uniform(0, math.pi * 2)
            rayon = random.uniform(distance_minimum, 2 * distance_minimum)
            nouveau_point = (point_actuel[0] + rayon * math.cos(angle), point_actuel[1] + rayon * math.sin(angle))

            # contrôle la validité du nouveau point
            if est_contenu_dans_la_fenetre(*nouveau_point) and est_valable(nouveau_point):
                ajouter_point(nouveau_point)
                liste_active.append(nouveau_point)
                trouve = True
                break

        if not trouve:
            # considère qu'il n'y a pas de point disponible
            liste_active.remove(point_actuel)

    return points


# </editor-fold>

# <editor-fold desc="Déclaration des classes">
# classe "de base" obstacle
class Obstacles(pygame.sprite.Sprite):
    '''
    :param pos_x: position x de l'obstacle
    :param pos_y: position y de l'obstacle
    :param liste_des_sprites: liste qui comprendra les obstacles
    '''

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
        # fonction qui sera modifié pour les différents obstacles,
        # retourne vrai pour pouvoir l'utiliser pour détecter les collisions
        return True


class Arbre(Obstacles):
    '''
    Classe pour l'obstacle "arbre".
    '''

    def __init__(self, pos_x, pos_y, liste_des_sprites):

        super().__init__(pos_x, pos_y, liste_des_sprites)
        # changement de l'image pour un arbre
        self.image = pygame.image.load("Images/arbre.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image, [55, 55])

    def collision(self, balle, sprite):
        # collision sur l'arbre : suivant le côté sur lequel la balle rebondit,
        # il faut inverser la direction x ou y de la balle
        if sprite.rect.x - 15 <= balle.balle_x <= sprite.rect.x + sprite.rect.height+15:
            balle.direction[1] = -balle.direction[1]
            print("reverted x")
        if sprite.rect.y - 20 <= balle.balle_y <= sprite.rect.y + sprite.rect.width+20:
            balle.direction[0] = -balle.direction[0]
            print("reverted y")
        super().collision()


class Bunker(Obstacles):
    '''
    Classe pour l'obstacle "bunker".
    '''

    def __init__(self, pos_x, pos_y, liste_des_sprites):
        super().__init__(pos_x, pos_y, liste_des_sprites)
        # image pour le bunker (sable)
        self.image = pygame.image.load("Images/sable_image.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, [55, 55])

    def collision(self, balle):
        # le bunker ralentit uniquement la balle en augmentant le frottement
        balle.frottement = 0.95
        print("Oh non! Un bunker!")
        super().collision()


class Balle:
    '''
    Classe pour la balle de golf.
    '''

    def __init__(self, balle_x, balle_y):
        '''
        :param balle_x: position x de la balle
        :param balle_y: position y de la balle
        '''
        self.balle_x = balle_x
        self.balle_y = balle_y
        self.direction = [1, 1]
        self.frottement = 0.989
        self.vitesse = 0
        self.collision = False

    def deplacer_balle(self):
        # si la balle bouge encore, elle subit du frottement pour la ralentir
        if self.vitesse >= 0.1:
            self.balle_x += self.vitesse * self.direction[0]
            self.balle_y += self.vitesse * self.direction[1]
            self.vitesse *= self.frottement
        else:
            # sinon, la balle est stoppée
            self.vitesse = 0


class Drapeau(Obstacles):
    def __init__(self, pos_x, pos_y, liste_des_sprites):
        '''
        Classe pour l'obstacle "drapeau".
        :param pos_x: position x du drapeau
        :param pos_y: position y du drapeau
        :param liste_des_sprites: ajout du drapeau dans la liste de sprite
        '''
        super().__init__(pos_x, pos_y, liste_des_sprites)
        self.image = pygame.image.load("Images/Trou.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, [35, 55])
        self.rect = self.image.get_rect()


    def collision(self):
        # si la balle entre en collision avec le drapeau, le joueur a gagné
        print("Fin du jeu!")


# </editor-fold>

# ajout de la barre qui nous indique la puissance
image_puissance = pygame.image.load("Images/barre_puissance.jpg").convert_alpha()
image_puissance = pygame.transform.scale(image_puissance, [20, 100])
position_barre = (90, 440)

# <editor-fold desc="Déclaration des constantes/variables spécifiques">
NOMBRE_DE_POINTS = 70
PHI = 1.618
RAYON = 350
NOMBRE_ARBRES = 25
NOMBRE_BUNKERS = 5
DISTANCE_MINIMUM_TEE_DRAPEAU = 450
VITESSE_ANGULAIRE = .003
FORCE_MINIMUM = 1

points = poisson_disc_sampling(90, 620, 1250, 50)
game_state = -2  # gère l'action actuelle --> visée = 0, force = 1, mouvement = 2
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
# ajout de l'image de fond
terrain = ajouter_sprite("Images/grass_texture.jpg", 0, 0)

# génération de tout les éléments sur le terrain
liste_arbres, liste_bunkers, drapeau_sprite, tee_position = generation_du_terrain(points)
continuer = True
balle_golf.balle_x = tee_position[0]
balle_golf.balle_y = tee_position[1]
balle_sprite = ajouter_sprite("Images/balle.png", balle_golf.balle_x, balle_golf.balle_y)
balle_sprite.image = pygame.transform.scale(balle_sprite.image, [40, 30])

balle_sprite.rect = balle_sprite.image.get_rect()
obstacles = liste_arbres + liste_bunkers

obstacles.append(drapeau_sprite)

# compteut de coups initialisé
compteur = ajouter_texte(None, 100, f"{nombre_de_tirs}")
compteur.rect.centerx = 100
compteur.rect.centery = 100

# </editor-fold>


# ajout d'un terrain qui cache tout les obstacles, ... pour lire les consignes
terrain_de_start = ajouter_sprite("Images/grass_texture.jpg", 0, 0)
texte_demarrage_1 = ajouter_texte(None, 30,
                                  f"Comment jouer ? Appuyez sur [espace] pour bloquer la direction de la balle et cliquez à nouveau pour bloquer la puissance")
texte_demarrage_1.rect.y -= 200
texte_demarrage_2 = ajouter_texte(None, 30,
                                  "Le but est de mettre la balle dans le trou en évitant les arbres et les bunkers")
texte_demarrage_2.rect.y -= 150
texte_demarrage_3 = ajouter_texte(None, 60, "Bonne chance !")
texte_demarrage_4 = ajouter_texte(None, 50, "Appuyez sur [espace] pour jouer")
texte_demarrage_4.rect.y += 200
# création de l'image qui nous servira pour la fin
image_fin_not_scale = pygame.image.load("Images/feu_artifice.jpg")
image_fin = pygame.transform.scale(image_fin_not_scale, (150, 150))

# <editor-fold desc="Boucle de jeu">
while continuer:
    fenetre.fill((0, 0, 0))
    if game_state >= 0:
        liste_sprite.draw(fenetre)
        # game_state = 0 --> la direction n'est pas bloqué, le joueur dois la choisir
        if game_state == 2 and balle_golf.vitesse == 0:
            direction_aléatoire = [0, 0]
            force_aléatoire = 0
            game_state = 0

        balle_sprite.rect.centerx = balle_golf.balle_x
        balle_sprite.rect.centery = balle_golf.balle_y
        # la balle ne peut pas sortir de l'écran
        if 0 > balle_golf.balle_x or balle_golf.balle_x > fenetre.get_rect().width:
            balle_golf.direction[0] *= -1
        if 0 > balle_golf.balle_y or balle_golf.balle_y > fenetre.get_rect().height:
            balle_golf.direction[1] *= -1
        balle_golf.deplacer_balle()

        # ajout de la barre de puissance
        fenetre.blit(image_puissance, position_barre)

        # création d'une hitlist pour détecter les collisions
        hit_list = pygame.sprite.spritecollide(balle_sprite, obstacles, False)

        if len(hit_list) > 0:
            # règle le bug de collisions multiples
            if balle_golf.collision == False:
                print("Collision detectée")
                # si c'est un arbre, on lance la fonction collision de la classe arbre
                if type(hit_list[0]) == Arbre:
                    balle_golf.collision = hit_list[0].collision(balle_golf, hit_list[0])
                    print("C'est un arbre !")
                # si c'est un bunker, on lance la fonction collision de la classe bunker
                if type(hit_list[0]) == Bunker:
                    balle_golf.collision = hit_list[0].collision(balle_golf)
                    print("C'est un bunker !")
            # si il y a une collision avec le drapeau,
            # on créé l'écran de fin et on change le statut du jeu: game_state = -1
            if type(hit_list[0]) == Drapeau:
                print("collision drapeau")
                hit_list[0].collision()
                time.sleep(0.2)
                terrain_fin = ajouter_sprite("Images/grass_texture.jpg", 0, 0)
                game_state = -1
                texte_fin_1 = ajouter_texte(None, 150, f"Bravo !")
                texte_fin_1.rect.y -= 200
                # contrôle de nombre de coup du joueur pour afficher un texte en fonction
                if nombre_de_tirs <= 1:
                    texte_fin_2 = ajouter_texte(None, 100, f"Hole in one !! Bravo")
                else:
                    texte_fin_2 = ajouter_texte(None, 100, f"Vous avez fait {nombre_de_tirs} coups")

                # dis au joueur comment relancer
                texte_relancer = ajouter_texte(None, 30, "Appuyez sur [espace] pour rejouer")
                texte_relancer.rect.y += 100
                # ajout des textes à la liste de sprite
                liste_sprite.add(texte_fin_1, texte_fin_2, texte_relancer)
        else:
            # si on est pas en collision, balle_golf.collision devient faux
            balle_golf.collision = False
            balle_golf.frottement = 0.989
        match game_state:
            # gère la saisie de la force et de la direction en fonction du gamestate
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

        pygame.draw.line(fenetre, (255, 0, 0), (balle_golf.balle_x, balle_golf.balle_y), (
        balle_golf.balle_x + direction_aléatoire[0] * 50, balle_golf.balle_y + direction_aléatoire[1] * 50), 3)
        pygame.draw.line(fenetre, (255, 0, 0), (fenetre.get_rect().bottomleft[0] + 90, fenetre.get_rect().bottomleft[
            1] - hauteur_force * force_aléatoire * 2 + 1 - 110), (fenetre.get_rect().bottomleft[0] + 110,
                                                                  fenetre.get_rect().bottomleft[
                                                                      1] - hauteur_force * force_aléatoire * 2 + 1 - 110),
                         5)
        police = pygame.font.Font(None, 100)
        compteur.image = police.render(f"{nombre_de_tirs}", 1, (255, 255, 255))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                continuer = False
            elif event.type == pygame.KEYUP:
                if event.key == K_SPACE:
                    if game_state < 3:
                        # la direction est bloqué à la direction choisi et la puissance est mainenant aléatoire,
                        # elle est bloquée quand le joueur appuye sur espace (game_state = 1)
                        if game_state == 1:
                            balle_golf.direction = direction_aléatoire
                            balle_golf.vitesse = FORCE_MINIMUM + force_aléatoire * 2.7
                            nombre_de_tirs += 1
                        if game_state != 2:
                            # on ajoute 1 à game_state pour que la balle bouge (game_state = 2)
                            game_state += 1
    elif game_state == -2:
        # écran d'accueil
        liste_sprite.draw(fenetre)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                continuer = False
            elif event.type == pygame.KEYUP:
                if event.key == K_SPACE:
                    # on supprime les textes et change le statut de jeu
                    # quand le joueur appuye sur espace
                    game_state = 0
                    liste_sprite.remove(texte_demarrage_1)
                    liste_sprite.remove(texte_demarrage_2)
                    liste_sprite.remove(texte_demarrage_3)
                    liste_sprite.remove(texte_demarrage_4)
                    liste_sprite.remove(terrain_de_start)

    elif game_state == -1:
        # ecran de fin
        liste_sprite.draw(fenetre)
        fenetre.blit(image_fin, (10, 10))
        fenetre.blit(image_fin, (1080, 480))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False
            elif event.type == pygame.KEYUP:
                # appuyer sur espace pour relancer le jeu
                if event.key == pygame.K_SPACE:
                    # Réinitialiser les variables du jeu
                    nombre_de_tirs = 0
                    points = poisson_disc_sampling(90, 620, 1250, 50)
                    balle_golf = Balle(10, 10)
                    liste_sprite.empty()
                    file = random.choice(os.listdir(path))
                    pygame.mixer.music.load(f"Musiques/{file}")
                    pygame.mixer.music.play(-1, 0.0)

                    # Ajouter un nouveau terrain et un nouveau compteur
                    terrain = ajouter_sprite("Images/grass_texture.jpg", 0, 0)

                    # Générer les obstacles
                    liste_arbres, liste_bunkers, drapeau_sprite, tee_position = generation_du_terrain(points)
                    continuer = True
                    balle_golf.balle_x = tee_position[0]
                    balle_golf.balle_y = tee_position[1]
                    balle_sprite = ajouter_sprite("Images/balle.png", balle_golf.balle_x, balle_golf.balle_y)
                    balle_sprite.image = pygame.transform.scale(balle_sprite.image, [40, 30])
                    balle_sprite.rect = balle_sprite.image.get_rect()
                    obstacles = liste_arbres + liste_bunkers
                    obstacles.append(drapeau_sprite)
                    compteur = ajouter_texte(None, 100, f"{nombre_de_tirs}")
                    compteur.rect.centerx = 100
                    compteur.rect.centery = 100

                    # Passer au bon état de jeu pour rejouer
                    game_state = 0

        # </editor-fold>
