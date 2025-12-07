from pyglet.image import load
from pyglet.math import Vec4
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
class Texture():
    def __init__(self,filepath=f"{current_directory}/../../assets/textures/blank.png") -> None:
        self.file = load(filepath)
        self.image = self.file.get_texture()
        self.surfaceColor = Vec4(1,1,1,0)
        self.baseColor=self.surfaceColor