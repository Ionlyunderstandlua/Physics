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

const float AXIS_EPSILON = 1e-4;

vec3 getLocalVertex(int obj, int index){
    vec4 localVerts[8] = vec4[](
        verts[obj].vert1,
        verts[obj].vert2,
        verts[obj].vert3,
        verts[obj].vert4,
        verts[obj].vert5,
        verts[obj].vert6,
        verts[obj].vert7,
        verts[obj].vert8
    );
    return localVerts[index].xyz;
}

vec3 getWorldVertex(int obj, int index){
    vec3 local = getLocalVertex(obj, index);
    vec3 right = normals[obj].right.xyz;
    vec3 up = normals[obj].up.xyz;
    vec3 look = normals[obj].look.xyz;
    vec3 offset = right * local.x + up * local.y + look * local.z;
    return positions[obj].xyz + offset;
}

float projectPointOntoAxis(vec3 point, vec3 axis){
    return dot(point, axis);
}

vec2 projectObjectOntoAxis(int objIndex, vec3 axis){
    float projection = projectPointOntoAxis(getWorldVertex(objIndex,0),axis);
    float minProj = projection;
    float maxProj = projection;

    for (int vert_index = 1; vert_index < 8; vert_index ++){
        projection = projectPointOntoAxis(getWorldVertex(objIndex,vert_index),axis);
        minProj = min(minProj, projection);
        maxProj = max(maxProj, projection);
    }

    return vec2(minProj, maxProj);
}

vec4 checkAxis(int obj1, int obj2, vec3 axis){
    float axisLen = length(axis);
    if (axisLen < AXIS_EPSILON){
        return vec4(-1.0);
    }

    vec3 axisNorm = normalize(axis);

    vec2 intervalA = projectObjectOntoAxis(obj1, axisNorm);
    vec2 intervalB = projectObjectOntoAxis(obj2, axisNorm);

    if (intervalA.y < intervalB.x || intervalB.y < intervalA.x){
        return vec4(0.0);
    }

    float overlapA = intervalA.y - intervalB.x;
    float overlapB = intervalB.y - intervalA.x;
    float penetrationDepth = min(overlapA, overlapB);

    float direction = sign(dot(axisNorm, positions[obj2].xyz - positions[obj1].xyz));
    if (direction == 0.0){
        direction = 1.0;
    }

    vec3 separatingAxis = axisNorm * direction;

    return vec4(penetrationDepth, separatingAxis);
}


void main(){
    uint ObjectID = gl_GlobalInvocationID.z*gl_WorkGroupSize.x*gl_WorkGroupSize.y+gl_GlobalInvocationID.y*gl_WorkGroupSize.x+gl_GlobalInvocationID.x;
    int objId = int(ObjectID);

    int pointer = int(distances[objId]);
    collisionIndex[objId] = 0;
    for (int index = 0; index < positions.length(); index ++){
        if (index == objId){
            continue;
        }

        float fullRadius = (settings[objId].radiusPadding.x + settings[index].radiusPadding.x);
        float pairDistance = distances[pointer + 1 + index];

        if (pairDistance < fullRadius){

            

            vec4 AxisChecks[15] = {
                checkAxis(objId,index,normals[objId].look.xyz),
                checkAxis(objId,index,normals[objId].up.xyz),
                checkAxis(objId,index,normals[objId].right.xyz),

                checkAxis(objId,index,normals[index].look.xyz),
                checkAxis(objId,index,normals[index].up.xyz),
                checkAxis(objId,index,normals[index].right.xyz),

                
                checkAxis(objId,index,cross(normals[objId].look.xyz,normals[index].look.xyz)),
                checkAxis(objId,index,cross(normals[objId].look.xyz,normals[index].up.xyz)),
                checkAxis(objId,index,cross(normals[objId].look.xyz,normals[index].right.xyz)),

                checkAxis(objId,index,cross(normals[objId].up.xyz,normals[index].look.xyz)),
                checkAxis(objId,index,cross(normals[objId].up.xyz,normals[index].up.xyz)),
                checkAxis(objId,index,cross(normals[objId].up.xyz,normals[index].right.xyz)),

                checkAxis(objId,index,cross(normals[objId].right.xyz,normals[index].look.xyz)),
                checkAxis(objId,index,cross(normals[objId].right.xyz,normals[index].up.xyz)),
                checkAxis(objId,index,cross(normals[objId].right.xyz,normals[index].right.xyz))
            };

            // check collisions and getminimum overlap

            vec4 minmumOverlap = vec4(fullRadius, 0.0, 0.0, 0.0);
            bool separatingAxisFound = false;

            for (int col_index = 0; col_index < 15; col_index ++){
                float axisResult = AxisChecks[col_index].x;
                if(axisResult == -1.0){
                    continue;
                }

                if(axisResult == 0.0){
                    separatingAxisFound = true;
                    break;
                }

                if(axisResult < minmumOverlap.x){
                    minmumOverlap = AxisChecks[col_index];
                }
                
            }

            if(separatingAxisFound){
                continue;
            }

            // Collisions
            collisionIndex[objId] = 1;

            // Skip if this object is rigid (cannot be moved)
            if (settings[objId].dynamics.y != 0) {
                continue;
            }

            // Resolve Collisions
            // minmumOverlap.yzw points from objId toward index
            // Negate so axis points AWAY from index (direction to push objId out)
            vec3 axis = -normalize(minmumOverlap.yzw);
            float penetration = minmumOverlap.x;

            float restitution = (settings[objId].dynamics.z + settings[index].dynamics.z) * 0.5;

            float massA = settings[objId].dynamics.w;
            float massB = settings[index].dynamics.w;
            // invMass = 0 for rigid objects (infinite mass)
            float invMassA = 1.0 / massA;
            float invMassB = (settings[index].dynamics.y == 0) ? 1.0 / massB : 0.0;

            float inertiaA = settings[objId].radiusPadding.y;
            float inertiaB = settings[index].radiusPadding.y;
            float invInertiaA = (inertiaA > 0.0) ? 1.0 / inertiaA : 0.0;
            float invInertiaB = (settings[index].dynamics.y == 0 && inertiaB > 0.0) ? 1.0 / inertiaB : 0.0;

            // Compute contact point from the deepest-penetrating vertices of objId
            // For a rotated cube landing on a corner/edge, these vertices are
            // offset laterally from center, creating the torque lever arm
            vec3 centerA = positions[objId].xyz;
            vec3 centerB = positions[index].xyz;

            // Find the vertices of objId that penetrate deepest into the other
            // object (smallest projection along axis = farthest in -axis direction)
            float minProj = dot(getWorldVertex(objId, 0), axis);
            for (int vi = 1; vi < 8; vi++) {
                float p = dot(getWorldVertex(objId, vi), axis);
                minProj = min(minProj, p);
            }

            // Average all vertices within penetration depth of the deepest point
            // This gives edge midpoints for edge contacts, corner points for corners
            float contactThreshold = minProj + penetration * 0.5;
            vec3 contactPoint = vec3(0.0);
            int contactCount = 0;
            for (int vi = 0; vi < 8; vi++) {
                vec3 wv = getWorldVertex(objId, vi);
                if (dot(wv, axis) <= contactThreshold) {
                    contactPoint += wv;
                    contactCount++;
                }
            }
            if (contactCount > 0) {
                contactPoint /= float(contactCount);
            } else {
                contactPoint = centerA - axis * (penetration * 0.5);
            }

            vec3 rA = contactPoint - centerA;
            vec3 rB = contactPoint - centerB;

            // Relative velocity at contact including angular contribution
            vec3 velA = velocities[objId].xyz + cross(aelocities[objId].xyz, rA);
            vec3 velB = velocities[index].xyz + cross(aelocities[index].xyz, rB);
            vec3 relVelContact = velA - velB;
            float vAlongContact = dot(relVelContact, axis);

            // Impulse scalar including rotational terms
            vec3 crossRA = cross(rA, axis);
            vec3 crossRB = cross(rB, axis);
            float angularTermA = dot(crossRA * invInertiaA, crossRA);
            float angularTermB = dot(crossRB * invInertiaB, crossRB);
            float denominator = invMassA + invMassB + angularTermA + angularTermB;

            // Apply velocity impulse only if objects are closing
            if (vAlongContact < 0.0 && denominator > 0.0) {
                float J = (-(1.0 + restitution) * vAlongContact) / denominator;
                vec3 impulse = J * axis;

                // Only modify THIS object's velocity (avoid race conditions)
                velocities[objId].xyz += impulse * invMassA;
                aelocities[objId].xyz += cross(rA, impulse) * invInertiaA;
            }

            // ALWAYS apply positional correction to resolve penetration
            // This prevents objects from passing through even at high velocities
            float totalInvMass = invMassA + invMassB;
            if (totalInvMass > 0.0) {
                float correctionShare = invMassA / totalInvMass;
                positions[objId].xyz += axis * penetration * correctionShare;
            }

            // Zero out velocity component pushing into the collision surface
            // This prevents gravity (which runs after SAT) from immediately
            // pulling the object back through the corrected position
            float velIntoSurface = dot(velocities[objId].xyz, -axis);
            if (velIntoSurface > 0.0) {
                velocities[objId].xyz += axis * velIntoSurface;
            }
            
            
        }
    }
}