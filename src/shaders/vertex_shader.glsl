#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec4 aColor;

uniform float uAspectRatio;

out vec4 vColor;
out vec3 vNormal;
out vec3 vFragPos;

void main() {
    float fov = radians(60.0);
    float aspect = uAspectRatio;
    float zNear = 0.1;
    float zFar = 1000.0;
    float f = 1.0 / tan(fov * 0.5);

    mat4 proj = mat4(
        f / aspect, 0.0, 0.0, 0.0,
        0.0, f, 0.0, 0.0,
        0.0, 0.0, (zFar + zNear) / (zNear - zFar), -1.0,
        0.0, 0.0, (2.0 * zFar * zNear) / (zNear - zFar), 0.0
    );

    mat4 view = mat4(1.0);
    // camera is moved back in Z and up in Y (inverse of scene translation)
    view[3].x = 0.0;
    view[3].y = -10.0;  // camera is 2 units higher than origin
    view[3].z = -40.0; // move camera back

    vec4 worldPos = vec4(aPos, 1.0);
    gl_Position = proj * view * worldPos;
    vColor = aColor;
    vNormal = aNormal;
    vFragPos = vec3(worldPos);
}
