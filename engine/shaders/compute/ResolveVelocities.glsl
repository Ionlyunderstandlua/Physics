#version 430 core



struct InstanceNormals {
    vec4 look;
    vec4 up;
    vec4 right;
};

struct InstaceSettings {
    vec4 dynamics;
    vec4 radiusPadding;
};

struct InstanceBoundBox {
    vec4 vert1;
    vec4 vert2;
    vec4 vert3;
    vec4 vert4;

    vec4 vert5;
    vec4 vert6;
    vec4 vert7;
    vec4 vert8;
};


layout(local_size_x = 1,local_size_y = 1,local_size_z = 1) in;

layout(std430, binding=0) buffer InstancePositionBuffer {vec4 positions[]; };
layout(std430, binding=1) buffer InstanceVelocityBuffer {vec4 velocities[]; };
layout(std430, binding=2) buffer InstanceAelocityBuffer {vec4 aelocities[]; };
layout(std430, binding=3) buffer InstanceRotationBuffer {vec4 rotations[]; };
layout(std430, binding=4) buffer InstanceNormalsVBuffer {InstanceNormals normals[]; };
layout(std430, binding=5) buffer InstanceSettingsBuffer {InstaceSettings settings[]; };
layout(std430, binding=6) buffer InstanceDistanceBuffer {float distances[];};
layout(std430, binding=7) buffer InstanceBoundBoxBuffer { InstanceBoundBox verts[];};

layout(std430, binding=8) buffer Collisions {
    float collisionIndex[];
};


uniform vec3 gravity;
uniform float deltaTime;

mat3 rotationMatrix(vec3 euler) {
    float cx = cos(euler.x); float sx = sin(euler.x);
    float cy = cos(euler.y); float sy = sin(euler.y);
    float cz = cos(euler.z); float sz = sin(euler.z);

    // Rotation order: X * Y * Z (matching Instance3D.FromXYZ)
    // GLSL mat3 is column-major: mat3(col0, col1, col2)
    mat3 Rx = mat3(1, 0, 0,   0, cx, sx,   0, -sx, cx);
    mat3 Ry = mat3(cy, 0, -sy,  0, 1, 0,   sy, 0, cy);
    mat3 Rz = mat3(cz, sz, 0,  -sz, cz, 0,   0, 0, 1);

    return Rx * Ry * Rz;
}

void main(){
    uint ObjectID = gl_GlobalInvocationID.z*gl_WorkGroupSize.x*gl_WorkGroupSize.y+gl_GlobalInvocationID.y*gl_WorkGroupSize.x+gl_GlobalInvocationID.x;
    int objId = int(ObjectID);

    if(settings[objId].dynamics.y == 0){
        // Dynamic object: integrate velocity
        positions[objId].xyz += velocities[objId].xyz * deltaTime;
        rotations[objId].xyz += aelocities[objId].xyz * deltaTime;

        // Simple angular damping
        aelocities[objId].xyz *= 0.98;
    } else {
        // Rigid/static object: force zero velocity to prevent drift
        velocities[objId].xyz = vec3(0.0);
        aelocities[objId].xyz = vec3(0.0);
    }

    // Rebuild orientation normals from current rotation angles
    mat3 rot = rotationMatrix(rotations[objId].xyz);
    normals[objId].right = vec4(rot[0], 0.0);
    normals[objId].up    = vec4(rot[1], 0.0);
    normals[objId].look  = vec4(rot[2], 0.0);
}