#version 450 core

uniform sampler2D sampTexture;

in vec3 light_dir;
in vec3 light_pos;
in vec4 light_color;
in vec4 surface_col;
in float light_str;

in vec3 normal;
in vec2 texture_coords;

out vec4 outColor;

void main()
{
    vec3 N = normalize(normal);
    vec3 Ld = normalize(-light_dir);
    vec3 Lp = normalize(-light_pos);

    float diffuseDir = max(dot(N, Ld), 0.0f);
    float diffusePoint = max(dot(N, Lp), 0.0f);

    float grey = (diffuseDir + diffusePoint) * 0.5;

    vec4 color = light_color * grey * light_str * surface_col;
    vec4 plaintexture = texture(sampTexture,texture_coords);
    outColor = plaintexture * color;
}
