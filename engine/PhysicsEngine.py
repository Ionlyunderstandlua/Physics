import ctypes
import math
from pyglet.gl import *
from pyglet.math import Vec3,Vec4
from pyglet.graphics.shader import ComputeShaderProgram
import os
current_directory = os.path.dirname(os.path.abspath(__file__))

class PhysicsParameters():
    def __init__(self):
        self.GravityEnabled = True
        self.Rigid = False
        self.Mass = 1
        self.Bounce = 1

class PhysicsEngineSettings():
    compute_shader_file_paths = [
        f"{current_directory}/shaders/compute/FirstGlance.glsl",
        f"{current_directory}/shaders/compute/SAT.glsl",
        f"{current_directory}/shaders/compute/Gravity.glsl",
        f"{current_directory}/shaders/compute/ResolveVelocities.glsl"
    ]   


    gravity = -0.1

class PhysicsEngine():
    def __init__(self):
        self.GlobalGravity = PhysicsEngineSettings.gravity

        self.compute_shader_programs = []

        for programe_file_path in PhysicsEngineSettings.compute_shader_file_paths:
            compute_shader_program_file = open(programe_file_path)
            compute_shader_program = ComputeShaderProgram(compute_shader_program_file.read())
            self.compute_shader_programs.append(compute_shader_program)
            compute_shader_program_file.close()
 
    def init_scene(self,newScene):

        # make buffers for each instance

        self.positionBufferData=[]
        self.velocityBufferData=[]
        self.aelocityBufferData=[]
        self.rotationBufferData=[]
        self.normalsvBufferData=[]
        self.settingsBufferData=[]
        self.distanceBufferData=[]
        self.boundboxBufferData=[]
        self.collisionBufferData = []

        self.physics_objects = []

        self.total_physics_objects = 0

        self.CurrentScene = newScene



        for instance in newScene.Instances3D.values():
            
            if instance.PhysicsEnabled:
                unit_size = getattr(instance, "UnitSize", Vec3(1,1,1))
                Vec3Scaled = Vec3(unit_size.x * instance.Size.x,unit_size.y * instance.Size.y,unit_size.z * instance.Size.z)
                half_extents = Vec3(
                    abs(Vec3Scaled.x) * 0.5,
                    abs(Vec3Scaled.y) * 0.5,
                    abs(Vec3Scaled.z) * 0.5
                )
                radius = math.sqrt(half_extents.x**2 + half_extents.y**2 + half_extents.z**2)
                inertia = max(instance.PhysicsParameters.Mass,0.001) * radius * radius * 0.4
                self.physics_objects.append(instance)

                self.positionBufferData.extend([instance.Position.x,instance.Position.y,instance.Position.z,0.0])
                self.velocityBufferData.extend([instance.Velocity.x,instance.Velocity.y,instance.Velocity.z,0.0])
                self.aelocityBufferData.extend([instance.Aelocity.x,instance.Aelocity.y,instance.Aelocity.z,0.0])
                self.rotationBufferData.extend([instance.Rotation.x,instance.Rotation.y,instance.Rotation.z,0.0])
                self.settingsBufferData.extend([
                    float(instance.PhysicsParameters.GravityEnabled),
                    float(instance.PhysicsParameters.Rigid),
                    instance.PhysicsParameters.Bounce,
                    instance.PhysicsParameters.Mass,
                    radius,
                    inertia,
                    0.0,
                    0.0
                ])
                self.distanceBufferData.append(self.total_physics_objects)
                self.collisionBufferData.append(0)
                self.normalsvBufferData.extend([
                    instance.LookVector.x,instance.LookVector.y,instance.LookVector.z,0.0,
                    instance.UpVector.x,instance.UpVector.y,instance.UpVector.z,0.0,
                    instance.RightVector.x,instance.RightVector.y,instance.RightVector.z,0.0
                ])

                self.total_physics_objects += 1
        for physics_object in self.physics_objects:



            self.distanceBufferData.extend([-1])
            self.distanceBufferData.extend([0]*self.total_physics_objects)


            # create bounding box
            unit_size = getattr(physics_object, "UnitSize", Vec3(1,1,1))
            Vec3Scaled = Vec3(unit_size.x * physics_object.Size.x,unit_size.y * physics_object.Size.y,unit_size.z * physics_object.Size.z)
            half_extents = Vec3(
                abs(Vec3Scaled.x) * 0.5,
                abs(Vec3Scaled.y) * 0.5,
                abs(Vec3Scaled.z) * 0.5
            )

            hx, hy, hz = half_extents.x, half_extents.y, half_extents.z

            self.boundboxBufferData.extend([
                hx, hy, hz, 0.0,
                hx, hy, -hz, 0.0,
                hx, -hy, hz, 0.0,
                hx, -hy, -hz, 0.0,

                -hx, hy, hz, 0.0,
                -hx, hy, -hz, 0.0,
                -hx, -hy, hz, 0.0,
                -hx, -hy, -hz, 0.0
            ])
            
        if self.total_physics_objects <= 0:
            return
        

        # Store buffer IDs for later reading
        self.pos_ssbo_id = GLuint()
        pos_ssbo_id = self.pos_ssbo_id

        self.positionBufferDataCTYPE = (ctypes.c_float*len(self.positionBufferData))(*self.positionBufferData)
        
        glGenBuffers(1,ctypes.byref(pos_ssbo_id))
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,pos_ssbo_id)
        glBufferData(GL_SHADER_STORAGE_BUFFER,ctypes.sizeof(self.positionBufferDataCTYPE),self.positionBufferDataCTYPE,GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,0,pos_ssbo_id)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,0)

        self.vel_ssbo_id = GLuint()
        vel_ssbo_id = self.vel_ssbo_id

        self.velocityBufferDataCTYPE = (ctypes.c_float*len(self.velocityBufferData))(*self.velocityBufferData)

        glGenBuffers(1,ctypes.byref(vel_ssbo_id))
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,vel_ssbo_id)
        glBufferData(GL_SHADER_STORAGE_BUFFER,ctypes.sizeof(self.velocityBufferDataCTYPE),self.velocityBufferDataCTYPE,GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,1,vel_ssbo_id)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,0)

        self.ael_ssbo_id = GLuint()
        ael_ssbo_id = self.ael_ssbo_id

        self.aelocityBufferDataCTYPE = (ctypes.c_float*len(self.aelocityBufferData))(*self.aelocityBufferData)

        glGenBuffers(1,ctypes.byref(ael_ssbo_id))
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,ael_ssbo_id)
        glBufferData(GL_SHADER_STORAGE_BUFFER,ctypes.sizeof(self.aelocityBufferDataCTYPE),self.aelocityBufferDataCTYPE,GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,2,ael_ssbo_id)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,0)

        self.rot_ssbo_id = GLuint()
        rot_ssbo_id = self.rot_ssbo_id

        self.rotationBufferDataCTYPE = (ctypes.c_float*len(self.rotationBufferData))(*self.rotationBufferData)

        glGenBuffers(1,ctypes.byref(rot_ssbo_id))
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,rot_ssbo_id)
        glBufferData(GL_SHADER_STORAGE_BUFFER,ctypes.sizeof(self.rotationBufferDataCTYPE),self.rotationBufferDataCTYPE,GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,3,rot_ssbo_id)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,0)

        self.nor_ssbo_id = GLuint()
        nor_ssbo_id = self.nor_ssbo_id

        self.normalsvBufferDataCTYPE = (ctypes.c_float*len(self.normalsvBufferData))(*self.normalsvBufferData)

        glGenBuffers(1,ctypes.byref(nor_ssbo_id))
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,nor_ssbo_id)
        glBufferData(GL_SHADER_STORAGE_BUFFER,ctypes.sizeof(self.normalsvBufferDataCTYPE),self.normalsvBufferDataCTYPE,GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,4,nor_ssbo_id)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,0)

        self.set_ssbo_id = GLuint()
        set_ssbo_id = self.set_ssbo_id

        self.settingsBufferDataCTYPE = (ctypes.c_float*len(self.settingsBufferData))(*self.settingsBufferData)

        glGenBuffers(1,ctypes.byref(set_ssbo_id))
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,set_ssbo_id)
        glBufferData(GL_SHADER_STORAGE_BUFFER,ctypes.sizeof(self.settingsBufferDataCTYPE),self.settingsBufferDataCTYPE,GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,5,set_ssbo_id)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,0)

        self.dis_ssbo_id = GLuint()
        dis_ssbo_id = self.dis_ssbo_id

        self.distanceBufferDataCTYPE = (ctypes.c_float*len(self.distanceBufferData))(*self.distanceBufferData)

        glGenBuffers(1,ctypes.byref(dis_ssbo_id))
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,dis_ssbo_id)
        glBufferData(GL_SHADER_STORAGE_BUFFER,ctypes.sizeof(self.distanceBufferDataCTYPE),self.distanceBufferDataCTYPE,GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,6,dis_ssbo_id)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,0)

        self.box_ssbo_id = GLuint()
        box_ssbo_id = self.box_ssbo_id

        self.boundboxBufferDataCTYPE = (ctypes.c_float*len(self.boundboxBufferData))(*self.boundboxBufferData)

        glGenBuffers(1,ctypes.byref(box_ssbo_id))
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,box_ssbo_id)
        glBufferData(GL_SHADER_STORAGE_BUFFER,ctypes.sizeof(self.boundboxBufferDataCTYPE),self.boundboxBufferDataCTYPE,GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,7,box_ssbo_id)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,0)

        self.col_ssbo_id = GLuint()
        col_ssbo_id = self.col_ssbo_id

        self.collisionBufferDataCTYPE = (ctypes.c_float*len(self.collisionBufferData))(*self.collisionBufferData)

        glGenBuffers(1,ctypes.byref(col_ssbo_id))
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,col_ssbo_id)
        glBufferData(GL_SHADER_STORAGE_BUFFER,ctypes.sizeof(self.collisionBufferDataCTYPE),self.collisionBufferDataCTYPE,GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,8,col_ssbo_id)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER,0)

    def read_buffers_from_gpu(self):
        """
        Read all SSBO buffers from GPU memory and cast them to their respective Python lists.
        """
        # Read position buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.pos_ssbo_id)
        mapped_ptr = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        if mapped_ptr:
            float_array = ctypes.cast(mapped_ptr, ctypes.POINTER(ctypes.c_float * len(self.positionBufferData))).contents
            self.positionBufferData = list(float_array)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        # Read velocity buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.vel_ssbo_id)
        mapped_ptr = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        if mapped_ptr:
            float_array = ctypes.cast(mapped_ptr, ctypes.POINTER(ctypes.c_float * len(self.velocityBufferData))).contents
            self.velocityBufferData = list(float_array)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        # Read aelocity buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.ael_ssbo_id)
        mapped_ptr = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        if mapped_ptr:
            float_array = ctypes.cast(mapped_ptr, ctypes.POINTER(ctypes.c_float * len(self.aelocityBufferData))).contents
            self.aelocityBufferData = list(float_array)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        # Read rotation buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.rot_ssbo_id)
        mapped_ptr = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        if mapped_ptr:
            float_array = ctypes.cast(mapped_ptr, ctypes.POINTER(ctypes.c_float * len(self.rotationBufferData))).contents
            self.rotationBufferData = list(float_array)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        # Read normals buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.nor_ssbo_id)
        mapped_ptr = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        if mapped_ptr:
            float_array = ctypes.cast(mapped_ptr, ctypes.POINTER(ctypes.c_float * len(self.normalsvBufferData))).contents
            self.normalsvBufferData = list(float_array)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        # Read settings buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.set_ssbo_id)
        mapped_ptr = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        if mapped_ptr:
            float_array = ctypes.cast(mapped_ptr, ctypes.POINTER(ctypes.c_float * len(self.settingsBufferData))).contents
            self.settingsBufferData = list(float_array)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        # Read distance buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.dis_ssbo_id)
        mapped_ptr = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        if mapped_ptr:
            float_array = ctypes.cast(mapped_ptr, ctypes.POINTER(ctypes.c_float * len(self.distanceBufferData))).contents
            self.distanceBufferData = list(float_array)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        # Read bounding box buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.box_ssbo_id)
        mapped_ptr = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        if mapped_ptr:
            float_array = ctypes.cast(mapped_ptr, ctypes.POINTER(ctypes.c_float * len(self.boundboxBufferData))).contents
            self.boundboxBufferData = list(float_array)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        # Read collision buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.col_ssbo_id)
        mapped_ptr = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        if mapped_ptr:
            float_array = ctypes.cast(mapped_ptr, ctypes.POINTER(ctypes.c_float * len(self.collisionBufferData))).contents
            self.collisionBufferData = list(float_array)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)





    def update_state(self,dt):
        if self.CurrentScene.paused:
            return

        if self.total_physics_objects <= 0:
            return

        for compute_shader in self.compute_shader_programs:
            compute_shader.use()

            # Set uniforms using dictionary-style access or OpenGL directly
            # Try dictionary-style first (pyglet ComputeShaderProgram may support this)
            program_id = getattr(compute_shader, 'id', None) or getattr(compute_shader, 'program', None) or getattr(compute_shader, '_program_id', None)
            if program_id is None:
                # If we can't find the program ID, get it from the current program
                program_id_array = (ctypes.c_int * 1)()
                glGetIntegerv(GL_CURRENT_PROGRAM, program_id_array)
                program_id = program_id_array[0]
            
            gravity_loc = glGetUniformLocation(program_id, b"gravity")
            delta_time_loc = glGetUniformLocation(program_id, b"deltaTime")
            
            if gravity_loc != -1:
                glUniform3f(gravity_loc, 0.0, PhysicsEngineSettings.gravity, 0.0)
            if delta_time_loc != -1:
                glUniform1f(delta_time_loc, dt)

            compute_shader.dispatch(self.total_physics_objects,1,1)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT | GL_BUFFER_UPDATE_BARRIER_BIT)

        # Read all buffers from GPU memory
        self.read_buffers_from_gpu()

        
        

        # Update positions
        pos_offset = 0
        rot_offset = 0
        box_offset = 0
        set_offset = 0
        vec_offset = 0

        def read_vec3(buffer, start):
            return (buffer[start], buffer[start+1], buffer[start+2])

        for physic_object_index in range(self.total_physics_objects):
            physic_object = self.physics_objects[physic_object_index]


            x = self.positionBufferData[pos_offset]
            y = self.positionBufferData[pos_offset+1]
            z = self.positionBufferData[pos_offset+2]

            vx = self.velocityBufferData[pos_offset]
            vy = self.velocityBufferData[pos_offset+1]
            vz = self.velocityBufferData[pos_offset+2]

            rx = self.rotationBufferData[pos_offset]
            ry = self.rotationBufferData[pos_offset+1]
            rz = self.rotationBufferData[pos_offset+2]

            ax = self.aelocityBufferData[pos_offset]
            ay = self.aelocityBufferData[pos_offset+1]
            az = self.aelocityBufferData[pos_offset+2]

            physic_object.Position = Vec3(x,y,z)
            physic_object.Velocity = Vec3(vx,vy,vz)

            physic_object.Rotation = Vec3(rx,ry,rz)
            physic_object.Aelocity = Vec3(ax,ay,az)

            pos_offset += 4

            print(physic_object_index,"\n",self.collisionBufferData[physic_object_index],"\n")

            if self.collisionBufferData[physic_object_index] == 1:
                physic_object.texture.surfaceColor = Vec4(0.5,0,0,0)
            else:
                physic_object.texture.surfaceColor = physic_object.texture.baseColor

        glUseProgram(0)
