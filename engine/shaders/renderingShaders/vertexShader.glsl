#version 450 core
layout(location=0) in vec3 vertices;
layout(location=1) in vec2 texturecoords;
layout(location=2) in vec3 normals;

uniform mat4 proj;
uniform mat4 cma;
uniform mat4 model;
uniform vec4 surfaceColor;

uniform vec3 lightDirection;
uniform vec3 lightPosition;
uniform float lightStrength;
uniform vec4 lightColor;

out vec3 normal;
out vec3 light_dir;
out vec3 light_pos;
out vec4 surface_col;
out vec4 light_color;
out vec2 texture_coords;
out float light_str;



void main()
{
    normal = inverse(transpose(mat3(model))) * normalize(normals);
    light_dir = normalize(lightDirection);   
    light_pos = lightPosition;
    light_str = lightStrength;
    light_color = lightColor;
    surface_col = surfaceColor;


    gl_Position = proj * cma * model * vec4(vertices,1.0f);

    texture_coords = texturecoords;
}
