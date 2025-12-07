import pyglet
from pyglet.gl import *
from pyglet.math import Vec3
from engine.RenderingEngine import MainWindow
from engine.PhysicsEngine import PhysicsEngine
from engine.classes.Scenes import SceneData
import os


current_directory = os.path.dirname(os.path.abspath(__file__))



if __name__ == '__main__':

    main_scene_path = f"{current_directory}/assets/scenes/phycoll.scene"
    main_scene = SceneData.fromfile(main_scene_path)



    window = MainWindow(width=1280,height=720,caption="Engine",resizable=True)
    window.change_scene(main_scene)

    physicsEngine = PhysicsEngine()

    def physics_setup(dt):
        physicsEngine.init_scene(window.CurrentScene)
        #pyglet.clock.schedule_once(physicsEngine.update_state,0.25)
        pyglet.clock.schedule_interval(physicsEngine.update_state,1/60)

    glEnable(GL_DEPTH_TEST)

    pyglet.clock.schedule_once(physics_setup,0.25)
    pyglet.clock.schedule_interval(window.update,1/60)
    pyglet.app.run()