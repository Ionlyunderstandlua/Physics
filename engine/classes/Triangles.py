from pyglet.math import Vec2,Vec3

class Triangle():
    def __init__(self,V1:Vec3,V2:Vec3,V3:Vec3,TV1:Vec2,TV2:Vec2,TV3:Vec2,parent_mesh):
        self.v1 = V1
        self.v2 = V2
        self.v3 = V3
        self.tv1 = TV1
        self.tv2 = TV2
        self.tv3 = TV3
        self.parent_mesh = parent_mesh
    def Normal(self):
        LineA = Vec3(self.v2.x-self.v1.x,self.v2.y-self.v1.y,self.v2.z-self.v1.z)
        LineB = Vec3(self.v3.x-self.v1.x,self.v3.y-self.v1.y,self.v3.z-self.v1.z)
        return LineA.cross(LineB).normalize()
    def Center(self) -> Vec3:
        Cx = (self.v1.x + self.v2.x + self.v3.x)//3
        Cy = (self.v1.y + self.v2.y + self.v3.y)//3
        Cz = (self.v1.z + self.v2.z + self.v3.z)//3
        return Vec3(Cx,Cy,Cz)
    def Vertext_Array(self):
        return [self.v1.x,self.v1.y,self.v1.z, self.v2.x,self.v2.y,self.v2.z, self.v3.x,self.v3.y,self.v3.z]
    def Texture_Array(self):
        return [self.tv1.x,self.tv1.y, self.tv2.x,self.tv2.y, self.tv3.x,self.tv3.y]
    
class Triangle2D():
    def __init__(self,V1:Vec2,V2:Vec2,V3:Vec2,TV1:Vec2,TV2:Vec2,TV3:Vec2,parent_mesh):
        self.v1 = V1
        self.v2 = V2
        self.v3 = V3
        self.tv1 = TV1
        self.tv2 = TV2
        self.tv3 = TV3
        self.parent_mesh = parent_mesh