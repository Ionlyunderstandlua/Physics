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

void main() {
    uint ObjectID = gl_GlobalInvocationID.z*gl_WorkGroupSize.x*gl_WorkGroupSize.y+gl_GlobalInvocationID.y*gl_WorkGroupSize.x+gl_GlobalInvocationID.x;
    
    //get distance array pointer

    int pointer = 0;
    int negValCount = 0;

    for (int index = 0; index < distances.length(); index ++){
        float negVal = distances[index];
        if (negVal == -1) {
            if (negValCount == ObjectID){
                pointer = index;
                break;
            }
            negValCount += 1;
        } 
    }

    distances[ObjectID] = pointer;
   
    for (int index = 0; index < positions.length(); index ++){
        if (index == ObjectID){
            continue;
        }

        float distance = length(positions[ObjectID].xyz - positions[index].xyz);
        distances[pointer + 1 + index] = distance;
    }
}