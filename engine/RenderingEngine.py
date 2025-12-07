import pyglet
from pyglet.gl import *
from pyglet.shapes import *
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.math import Mat4,Vec3,Vec4
from pyglet.window import key

from engine.classes.Scenes import SceneData

import os

current_directory = os.path.dirname(os.path.abspath(__file__))


class ENGINESETTINGS:
    vertextShaderPath = f"{current_directory}/shaders/renderingShaders/vertexShader.glsl"
    fragmentShaderPath = f"{current_directory}/shaders/renderingShaders/fragmentShader.glsl"

    projectionMode = "Perspective"


#Main Engine
class MeshGroup(pyglet.graphics.Group):
    def __init__(self, texture:pyglet.image.Texture,shader_pro:ShaderProgram,worldMatrix:Mat4,surfaceColor:Vec4):
        
        super().__init__()
        self.texture = texture
        self.program = shader_pro
        self.worldMatrix = worldMatrix
        self.surfaceColor = surfaceColor
        self.program.use()
    def set_state(self):
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        self.program['model'] = self.worldMatrix
        self.program['surfaceColor'] = self.surfaceColor
    def unset_state(self):
        pass
    # def __eq__(self,other):
    #     return(self.__class__ is other.__class__ and
    #            self.texture.id == other.texture.id and
    #            self.texture.target == other.texture.target and
    #            self.parent == other.parent)

    def __hash__(self):
        return hash((self.texture.id,self.texture.target))

class MainWindow(pyglet.window.Window):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.CurrentScene = SceneData()

        self.inputs = {"forward":0,"right":0,'up':0,'tright':0,'tup':0}
    
        self.batch = pyglet.graphics.Batch()

        self.render_groups = []

        self.vertext_source_file = open(ENGINESETTINGS.vertextShaderPath)
        self.fragment_source_file = open(ENGINESETTINGS.fragmentShaderPath)

        self.vertext_source = self.vertext_source_file.read()
        self.fragment_source = self.fragment_source_file.read()

        self.vertext_source_file.close()
        self.fragment_source_file.close()

        self.vertex_shader = Shader(self.vertext_source,"vertex")
        self.fragment_shader = Shader(self.fragment_source,"fragment")

        self.program = ShaderProgram(self.vertex_shader,self.fragment_shader)

        self.oproj_mat = Mat4.orthogonal_projection(left=0,right=1280,bottom=0,top=720,z_near=0.1,z_far=100)
        self.pproj_mat = Mat4.perspective_projection(aspect=self.aspect_ratio,z_near=0.1,z_far=100)
        self.proj_mat = self.pproj_mat if ENGINESETTINGS.projectionMode == "Perspective" else self.oproj_mat
        
        self.change_scene(SceneData())


    def change_scene(self,NextScene):

        for instance in self.CurrentScene.Instances3D.values():
            if hasattr(instance,"mGroup") and instance.mGroup in self.render_groups:
                self.render_groups.remove(instance.mGroup)
            
            if hasattr(instance,"v_list"):
                instance.v_list.delete()
        
        del self.CurrentScene
        self.CurrentScene = NextScene

        self.program["lightDirection"] = self.CurrentScene.Light.Rotation
        self.program["lightPosition"] = self.CurrentScene.Light.Position
        self.program["lightStrength"] = self.CurrentScene.Light.Strength
        self.program["lightColor"] = self.CurrentScene.Light.Color

        self.program["proj"] = self.proj_mat

        self.load_scene()











    def load_instance_into_scene(self,instance):
        instance.update_matrixs()
        model = instance.WorldMatrix
        instance.mGroup = MeshGroup(instance.texture.image,self.program,model,instance.texture.surfaceColor)
        self.render_groups.append(instance.mGroup)

        verts,textels,normals,color = instance.get_array()
        instance.v_list = self.program.vertex_list(len(verts)//3,
                                                        GL_TRIANGLES,
                                                        batch = self.batch,
                                                        group = instance.mGroup,
                                                        vertices = ('f',verts),
                                                        texturecoords=('f',textels),
                                                        normals=('f',normals))

    def load_scene(self):
        self.CurrentScene.MainCamera.update_matrixs()
        for instance in self.CurrentScene.Instances3D.values():
            self.load_instance_into_scene(instance)


    def reload_scene(self):
        newScene = SceneData()
        if self.CurrentScene.filePath != "Default":
            newScene = SceneData.fromfile(self.CurrentScene.filePath)
        self.change_scene(newScene)






    def frame_update(self):
        self.CurrentScene.MainCamera.update_matrixs()
        self.program["cma"] = self.CurrentScene.MainCamera.WorldMatrix
        for instance in self.CurrentScene.Instances3D.values():
            instance.update_matrixs()
            instance.mGroup.worldMatrix = instance.WorldMatrix
            instance.mGroup.surfaceColor = instance.texture.surfaceColor


    def on_draw(self):
        self.clear()
        # Draw background

        self.frame_update()
        self.program.use()
        self.batch.draw()

    def update(self,dt):
        mCam = self.CurrentScene.MainCamera
        camForward = mCam.LookVector.normalize() * self.inputs["forward"] * mCam.MoveSpeed * dt
        camRight = mCam.RightVector.normalize() * self.inputs["right"] * mCam.MoveSpeed * dt
        camUp = mCam.UpVector.normalize() * self.inputs["up"] * mCam.MoveSpeed * dt

        camMove = camForward+camRight+camUp

        mCam.Rotation += Vec3(self.inputs['tup']*mCam.TurnSpeed * dt,self.inputs['tright']*mCam.TurnSpeed * dt,0)
        mCam.Position += camMove
        pass






    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.inputs["forward"] = 1
        if symbol == key.A:
            self.inputs["right"] = 1
        if symbol == key.S:
            self.inputs["forward"] = -1
        if symbol == key.D:
            self.inputs["right"] = -1

        if symbol == key.SPACE:
            self.inputs["up"] = 1
        if symbol == key.LSHIFT:
            self.inputs["up"] = -1

        if symbol == key.LEFT:
            self.inputs["tright"] = 1
        if symbol == key.RIGHT:
            self.inputs["tright"] = -1
        if symbol == key.UP:
            self.inputs["tup"] = -1
        if symbol == key.DOWN:
            self.inputs["tup"] = 1

        

    
    def on_key_release(self, symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            self.inputs["forward"] = 0
        if symbol == key.A or symbol == key.D:
            self.inputs["right"] = 0

        if symbol == key.SPACE or symbol == key.LSHIFT:
            self.inputs["up"] = 0

        if symbol == key.LEFT or symbol == key.RIGHT:
            self.inputs["tright"] = 0
        if symbol == key.UP or symbol == key.DOWN:
            self.inputs["tup"] = 0

        if symbol == key.R:
            self.reload_scene()

        if symbol == key.P:
            self.CurrentScene.paused = not self.CurrentScene.paused
