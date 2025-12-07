import math
from pyglet.math import Vec2,Vec3,Vec4,Mat4

from engine.classes.Textures import Texture
from engine.classes.Triangles import Triangle
from engine.PhysicsEngine import PhysicsParameters

class Instance3D():
    def __init__(self):

        self._Position = Vec3(0,0,0)
        self._OldPosition = Vec3(0,0,0)
        self._Size = Vec3(1,1,1)
        self._Rotation = Vec3(0,0,0)


        self.RightVector    = Vec3(1,0,0)
        self.UpVector       = Vec3(0,1,0)
        self.LookVector     = Vec3(0,0,1)
        
        self.Parent = "@root"
        self.Children = []

        self.Name = "Instance"

        self.PhysicsEnabled = False
        self.PhysicsParameters = PhysicsParameters()

        self.Velocity = Vec3(0,0,0)
        self.Aelocity = Vec3(0,0,0)

        
    
    def update_matrixs(self):
        self.XrotMatrix = Mat4.from_rotation(self.Rotation.x,self.RightVector.normalize())
        self.YrotMatrix = Mat4.from_rotation(self.Rotation.y,Vec3(0,1,0))
        self.ZrotMatrix = Mat4.from_rotation(self.Rotation.z,self.LookVector.normalize())

        self.PosMatrix = Mat4.from_translation(self.Position)
        self.ScaleMatrix = Mat4.from_scale(self.Size)

        # default world matrix composition (translate → rotate → scale about origin)
        self.WorldMatrix = self.PosMatrix @ self.FromXYZ() @ self.ScaleMatrix
        

    def FromXYZ(self):
        return self.XrotMatrix @ self.YrotMatrix @ self.ZrotMatrix
    
    @property
    def Position(self):
        return self._Position

    @property
    def Rotation(self):
        return self._Rotation

    @property
    def Size(self):
        return self._Size

    @Position.setter
    def Position(self,New_Position:Vec3):
        if New_Position != self._Position:
            self._OldPosition = self._Position
            self._Position = New_Position

    @Rotation.setter
    def Rotation(self,New_Rotation:Vec3):
        if New_Rotation != self._Rotation:
            self._Rotation = New_Rotation

    @Size.setter
    def Size(self,New_Size:Vec3):
        if New_Size != self._Size:
            self._Size = New_Size
    
class Mesh(Instance3D):
    def __init__(self):
        super().__init__()
        self.triangles = []
        self.vectors = []
        self.tvectors = []
        self.texture = Texture()

        self.UnitSize = self.Size

    def update_matrixs(self):
        super().update_matrixs()
    def fromfile(filepath="./Resources/models/Level.obj"):

        newMesh = Mesh()

        mesh_data = open(filepath,"r")
        for ldata in mesh_data.readlines():
            data = str.split(ldata," ")

            if data[0] == "v":
                newMesh.vectors.append(Vec3(float(data[1]),float(data[2]),float(data[3])))
            if data[0] == "vt":
                newMesh.tvectors.append(Vec2(float(data[1]),float(data[2])))

            if data[0] == "f":

                v1,t1 = str.split(data[1],'/')
                v2,t2 = str.split(data[2],'/')
                v3,t3 = str.split(data[3],'/')

                newMesh.triangles.append(Triangle(newMesh.vectors[int(v1)-1],newMesh.vectors[int(v2)-1],newMesh.vectors[int(v3)-1],newMesh.tvectors[int(t1)-1],newMesh.tvectors[int(t2)-1],newMesh.tvectors[int(t3)-1],newMesh))

        mesh_data.close()
        return newMesh
    
    def fromRawData(rawData):
        newMesh = Mesh()

        meshColor = [1,1,1]

        for line_data in rawData:
            data = str.split(line_data.strip()," ")

            if data[0] == "o" or data[0] == "g" :
                newMesh.Name = data[1]
            if data[0] == "v":
                newMesh.vectors.append(Vec3(float(data[1]),float(data[2]),float(data[3])))
            if data[0] == "vt":
                newMesh.tvectors.append(Vec2(float(data[1]),float(data[2])))

            if data[0] == "f":

                v1,t1,n1 = str.split(data[1],'/')
                v2,t2,n2 = str.split(data[2],'/')
                v3,t3,n3 = str.split(data[3],'/')
                newMesh.triangles.append(Triangle(newMesh.vectors[int(v1)-1],newMesh.vectors[int(v2)-1],newMesh.vectors[int(v3)-1],newMesh.tvectors[int(t1)-1],newMesh.tvectors[int(t2)-1],newMesh.tvectors[int(t3)-1],newMesh))

            if data[0] == "p":
                newMesh.Position = Vec3(float(data[1]),float(data[2]),float(data[3]))


            if data[0] == "prc":
                meshColor[0] = float(data[1])
            if data[0] == "pgc":
                meshColor[1] = float(data[1])
            if data[0] == "pbc":
                meshColor[2] = float(data[1])


            if data[0] == "p-":
                newMesh.PhysicsEnabled = True

            if data[0] == "pma":
                newMesh.PhysicsParameters.Mass = float(data[1])

            if data[0] == "pbo":
                newMesh.PhysicsParameters.Bounce = float(data[1])

            if data[0] == "pgr":
                newMesh.PhysicsParameters.GravityEnabled = bool(int(data[1]))

            if data[0] == "pri":
                newMesh.PhysicsParameters.Rigid = bool(int(data[1]))

        # calc size

        boundsx = [newMesh.vectors[0].x,newMesh.vectors[0].x]
        boundsy = [newMesh.vectors[0].y,newMesh.vectors[0].y]
        boundsz = [newMesh.vectors[0].z,newMesh.vectors[0].z]  

        for vert in newMesh.vectors:
            # check mins
            boundsx[0] = min(boundsx[0],vert.x)
            boundsy[0] = min(boundsy[0],vert.y)
            boundsz[0] = min(boundsz[0],vert.z)


            # check maxs
            boundsx[1] = max(boundsx[1],vert.x)
            boundsy[1] = max(boundsy[1],vert.y)
            boundsz[1] = max(boundsz[1],vert.z)

        


        newMesh.UnitSize = Vec3(boundsx[1]-boundsx[0],boundsy[1]-boundsy[0],boundsz[1]-boundsz[0])
        newMesh.texture.surfaceColor = Vec4(meshColor[0],meshColor[1],meshColor[2],0)
        newMesh.texture.baseColor = newMesh.texture.surfaceColor

        return newMesh
    
    def get_array(self):
        vert = []
        text = []
        normals = []
        color = []
        for tri in self.triangles:
            vert.extend(tri.Vertext_Array())
            text.extend(tri.Texture_Array())

            c = self.texture.surfaceColor
            n = tri.Normal()
            for i in range(3):
                normals.extend([n.x,n.y,n.z])
                color.extend([c.x,c.y,c.z,c.w])
        return vert,text,normals,color
    

class Cube(Mesh):
    def __init__(self):
        super().__init__()
        self.triangles = [
            #South
            Triangle(Vec3(-0.5,-0.5,-0.5),Vec3(-0.5,0.5,-0.5),Vec3(0.5,0.5,-0.5),Vec2(0,1),Vec2(0,0),Vec2(1,0),self),
            Triangle(Vec3(-0.5,-0.5,-0.5),Vec3(0.5,0.5,-0.5),Vec3(0.5,-0.5,-0.5),Vec2(0,1),Vec2(1,0),Vec2(1,1),self),
            #East
            Triangle(Vec3(0.5,-0.5,-0.5),Vec3(0.5,0.5,-0.5),Vec3(0.5,0.5,0.5),Vec2(0,1),Vec2(0,0),Vec2(1,0),self),
            Triangle(Vec3(0.5,-0.5,-0.5),Vec3(0.5,0.5,0.5),Vec3(0.5,-0.5,0.5),Vec2(0,1),Vec2(1,0),Vec2(1,1),self),

            #North
            Triangle(Vec3(0.5,-0.5,0.5),Vec3(0.5,0.5,0.5),Vec3(-0.5,0.5,0.5),Vec2(0,1),Vec2(0,0),Vec2(1,0),self),
            Triangle(Vec3(0.5,-0.5,0.5),Vec3(-0.5,0.5,0.5),Vec3(-0.5,-0.5,0.5),Vec2(0,1),Vec2(1,0),Vec2(1,1),self),
            
            #West
            Triangle(Vec3(-0.5,-0.5,0.5),Vec3(-0.5,0.5,0.5),Vec3(-0.5,0.5,-0.5),Vec2(0,1),Vec2(0,0),Vec2(1,0),self),
            Triangle(Vec3(-0.5,-0.5,0.5),Vec3(-0.5,0.5,-0.5),Vec3(-0.5,-0.5,-0.5),Vec2(0,1),Vec2(1,0),Vec2(1,1),self),

            #Top
            Triangle(Vec3(-0.5,0.5,-0.5),Vec3(-0.5,0.5,0.5),Vec3(0.5,0.5,0.5),Vec2(0,1),Vec2(0,0),Vec2(1,0),self),
            Triangle(Vec3(-0.5,0.5,-0.5),Vec3(0.5,0.5,0.5),Vec3(0.5,0.5,-0.5),Vec2(0,1),Vec2(1,0),Vec2(1,1),self),

            #Bottom
            Triangle(Vec3(0.5,-0.5,0.5),Vec3(-0.5,-0.5,0.5),Vec3(-0.5,-0.5,-0.5),Vec2(0,1),Vec2(0,0),Vec2(1,0),self),
            Triangle(Vec3(0.5,-0.5,0.5),Vec3(-0.5,-0.5,-0.5),Vec3(0.5,-0.5,-0.5),Vec2(0,1),Vec2(1,0),Vec2(1,1),self),
        ]


class Camera(Instance3D):
    def __init__(self):
        super().__init__()
        self.MoveSpeed = 10
        self.TurnSpeed = 2


        self.Render_Distance = 200
        self.Position = Vec3()
    
        self._Target_Direction = Vec3(0,0,1)
    def update_matrixs(self):
        self.Rotation = Vec3(min(max(self.Rotation.x,-1),1),self.Rotation.y,self.Rotation.z)
        super().update_matrixs()
        self.UpVector = Vec3(0,1,0) 

        self._Target_Direction = Vec3(0,0,1)

        self.WorldMatrix = self.XrotMatrix @ self.YrotMatrix
        
        self.LookVectorV4 = self.WorldMatrix @ Vec4(self._Target_Direction.x,self._Target_Direction.y,self._Target_Direction.z,1)
        
        self.LookVector = Vec3(self.LookVectorV4.x,self.LookVectorV4.y,self.LookVectorV4.z)

        self.RightVector = self.UpVector.cross(self.LookVector)

        self.UpVector = self.LookVector.cross(self.RightVector)

        self._Target_Direction = self.Position + self.LookVector

        self.WorldMatrix = Mat4.look_at(self.Position,self._Target_Direction,self.UpVector)

    def vectors_to_euler_xyz(self, look_vector=None, up_vector=None, right_vector=None):
        if look_vector is None:
            look_vector = self.LookVector
        if up_vector is None:
            up_vector = self.UpVector
        if right_vector is None:
            right_vector = self.RightVector
        
        look = look_vector.normalize()
        up = up_vector.normalize()
        right = right_vector.normalize()
        
        
        pitch = math.atan2(-look.y, look.z)
        yaw = math.asin(look.x)
        roll = math.atan2(-up.x, right.x)
        
        return Vec3(roll, pitch+1.5, yaw)
    
    def fromRawData(rawData):
        newCamera = Camera()

        LookVector = Vec3(0,0,1) 
        UpVector = Vec3(0,1,0)
        RightVector = Vec3(1,0,0)

        for line_data in rawData:
            data = str.split(line_data.strip()," ")
            if data[0] == "o" or data[0] == "g":
                newCamera.Name = data[1]
            if data[0] == "v" or data[0] == "p":
                newCamera.Position = Vec3(float(data[1]),float(data[2]),float(data[3]))
                pass
            if data[0] == "lv":
                LookVector = Vec3(float(data[1]),float(data[2]),float(data[3]))
            if data[0] == "uv":
                UpVector = Vec3(float(data[1]),float(data[2]),float(data[3]))
            if data[0] == "rv":
                RightVector = Vec3(float(data[1]),float(data[2]),float(data[3]))

        newCamera.Rotation = newCamera.vectors_to_euler_xyz(LookVector,UpVector,RightVector)
        return newCamera


class LightSource(Instance3D):
    def __init__(self):
        super().__init__()

        self.Strength = 100
        self.Color = Vec4(1.0,1.0,1.0,0)

        self.Position = Vec3(5,5,5)

    def fromRawData(rawData):
        newLight = LightSource()
        for line_data in rawData:
            data = str.split(line_data.strip()," ")
            if data[0] == "o" or data[0] == "g":
                newLight.Name = data[1]
            if data[0] == "v" or data[0] == "p":
                newLight.Position = Vec3(-float(data[1]),-float(data[2]),float(data[3]))
            if data[0] == "c":
                newLight.Color = Vec4(float(data[1]),float(data[2]),float(data[3]),0)
            if data[0] == "e":
                newLight.Strength = float(data[1])/50
            if data[0] == "r":
                newLight.Rotation = Vec3(float(data[1]),float(data[2]),float(data[3]))

        return newLight





