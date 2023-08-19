import pygame as pg


class Button:
    def __init__(self, pos: tuple[int, int], image: pg.Surface, single_click: bool = True, check_mouse_on: bool = False, center: bool = False):
        self.image: pg.Surface = image
        self.rect: pg.rect.Rect = self.image.get_rect()
        self.pos: tuple[int, int] = pos
        if center:
            self.rect.center = pos
        else:
            self.rect.topleft = pos
        self.clicked: bool = True
        self.single_click: bool = single_click
        self.check_mouse_on: bool = check_mouse_on

    def draw(self, surface: pg.Surface) -> tuple[bool, bool] | bool:
        mouse_clicked: bool = False
        pos: tuple[int, int] = pg.mouse.get_pos()

        if self.rect.collidepoint(pos):
            mouse_on: bool = True
            if pg.mouse.get_pressed()[0] and not self.clicked:
                mouse_clicked = True
                if self.single_click:
                    self.clicked = True
        else:
            mouse_on = False

        if not pg.mouse.get_pressed()[0]:
            self.clicked = False

        surface.blit(self.image, self.rect)

        return (mouse_clicked, mouse_on) if self.check_mouse_on else mouse_clicked

    def change_image(self, image: pg.Surface) -> None:
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

    def change_pos(self, pos: tuple[int, int], center: bool = False) -> None:
        self.rect = self.image.get_rect()
        if center:
            self.rect.center = pos
        else:
            self.rect.topleft = pos
