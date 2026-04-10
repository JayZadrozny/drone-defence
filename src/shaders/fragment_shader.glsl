#version 330 core
in vec4 vColor;
in vec3 vNormal;
in vec3 vFragPos;
out vec4 FragColor;

void main() {
    // normalize interpolated normal (important for correct lighting)
    vec3 N = normalize(vNormal);

    // ambient
    float ambientStrength = 0.15;
    vec3 ambient = ambientStrength * vec3(vColor);

    // diffuse (two sided + two light directions to reduce extreme face contrast)
    vec3 lightDir1 = normalize(vec3(1.0, 1.0, 1.0));  // top-right light
    float diff = max(dot(N, lightDir1), 0.0);
    
    // enforce a minimum diffuse so left/back faces aren't near-black
    diff = max(diff, 0.15);
    vec3 diffuse = diff * vec3(vColor);

    vec3 result = ambient + diffuse;
    FragColor = vec4(result, vColor.a);
}
