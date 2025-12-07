from engine.classes.Instances import Camera,LightSource,Mesh,Cube

class SceneData():
    
    def __init__(self):
        self.Cameras = [Camera()]
        self.MainCamera = self.Cameras[0]

        self.Instances3D = {}

        self.Light = LightSource()

        self.filePath="Default"

        self.paused = False

    def fromfile(filepath):

        newScene = SceneData()

        newScene.Cameras.clear()
        newScene.MainCamera = None

        newScene.Instances3D = {}

        scene_data = open(filepath,"r")

        objects = []

        current_Obj = "(none)"
        # split objects

        newScene.filePath = filepath

        for line_data in scene_data.readlines():
            data = str.split(line_data.strip()," ")
            if data[0] == "ty":
                if current_Obj == "(none)":
                    current_Obj = (data[1],[])
                else:
                    print(f"LAST OBJECT IS MISSING AN END TAG: {current_Obj[0]}")
                    break
                continue
         
            if data[0] == "en":
                objects.append(current_Obj)
                current_Obj = "(none)"
                continue

            if current_Obj != "(none)":
                current_Obj[1].append(line_data)
                continue
        # load objecs
        for obj in objects:
            obj_type = obj[0]
            obj_data = obj[1]
            if obj_type == "MESH":
                newMesh = Mesh.fromRawData(obj_data)
                newScene.Instances3D[newMesh.Name] = newMesh

            if obj_type == "LIGHT":
                lightSource = LightSource.fromRawData(obj_data)
                newScene.Light = lightSource
            
            if obj_type == "CAMERA":
                newCamera = Camera.fromRawData(obj_data)
                newScene.Cameras.append(newCamera)

                if newCamera.Name == "MainCamera":
                    newScene.MainCamera = newCamera

        if newScene.MainCamera == None:
            if len(newScene.Cameras) < 1:
                newScene.Cameras.append(Camera())
            newScene.MainCamera = newScene.Cameras[0]

        return newScene
    


                    
            

