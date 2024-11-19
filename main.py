
import pygame
from pygame.locals import *

pygame.init()
pygame.key.set_repeat(30, 30)
fenetre = pygame.display.set_mode((800, 450), RESIZABLE)

liste_sprite = pygame.sprite.LayeredUpdates()

def ajouter_sprite(image_nom, rect_x, rect_y):
    sprite_ajout = pygame.sprite.Sprite()
    pygame.sprite.Sprite.__init__(sprite_ajout)
    sprite_ajout.image = pygame.image.load(image_nom).convert()
    sprite_ajout.rect = sprite_ajout.image.get_rect()
    sprite_ajout.rect.x=rect_x
    sprite_ajout.rect.y = rect_y
    liste_sprite.add(sprite_ajout)
    return sprite_ajout

def ajouter_texte(police_nom, taille, texte_a_afficher):
    police = pygame.font.Font(police_nom, taille)
    texte = pygame.sprite.Sprite()
    pygame.sprite.Sprite.__init__(texte)

    liste_sprite.add(texte)

    texte.image = police.render(texte_a_afficher, 1, (10,10,10), (255,90,20))
    texte.rect = texte.image.get_rect()
    texte.rect.centerx = fenetre.get_rect().centerx
    texte.rect.centery = fenetre.get_rect().centery
    liste_sprite.add(texte)
    return texte

continuer = True


while continuer:
    liste_sprite.draw(fenetre)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
