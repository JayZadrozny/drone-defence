import glfw
import os
import ctypes
from OpenGL.GL import *
import numpy as np
from math import radians, degrees

def generateRotationMatricies(yaw, pitch, roll): # generate rotation matrices base on a yaw, pitch and roll value
    pitchRotation = np.array([[np.cos(radians(yaw)), 0, np.sin(radians(yaw))],
        [0, 1, 0],
        [-np.sin(radians(yaw)), 0, np.cos(radians(yaw))]]) # Y rotation
        
    yawRotation = np.array([[1, 0, 0],
        [0, np.cos(radians(pitch)), -np.sin(radians(pitch))],
        [0, np.sin(radians(pitch)), np.cos(radians(pitch))]]) # X rotation
        
    rollRotation = np.array([[np.cos(radians(roll)), -np.sin(radians(roll)), 0],
        [np.sin(radians(roll)), np.cos(radians(roll)), 0],
        [0, 0, 1]]) # Z rotation
        
    return yawRotation, pitchRotation, rollRotation

class Triangle:
    def __init__(
        self,
        vertex1: tuple[float, float, float],
        vertex2: tuple[float, float, float],
        vertex3: tuple[float, float, float],
        colour1: tuple[float, float, float, float],
        colour2: tuple[float, float, float, float],
        colour3: tuple[float, float, float, float]):

        # compute normal for the triangle (flat shading)
        v1 = np.array(vertex1, dtype=np.float32)
        v2 = np.array(vertex2, dtype=np.float32)
        v3 = np.array(vertex3, dtype=np.float32)

        edge1 = v2 - v1
        edge2 = v3 - v1
        normal = np.cross(edge1, edge2)
        normal = normal / np.linalg.norm(normal)

        # ensure normal is pointing away from object center (0,0,0)
        center = (v1 + v2 + v3) / 3.0
        if np.dot(normal, center) < 0:
            normal = -normal

        normal = tuple(normal.tolist())

        self.vertices = [
            *vertex1, *normal, *colour1,
            *vertex2, *normal, *colour2,
            *vertex3, *normal, *colour3,
        ]

        # set up buffers
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        vertex_data = (GLfloat * len(self.vertices))(*self.vertices)

        # bind vertex arrays
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(vertex_data), vertex_data, GL_STATIC_DRAW)

        # position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, ctypes.sizeof(GLfloat)*10, ctypes.c_void_p(0))

        # normal attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, ctypes.sizeof(GLfloat)*10, ctypes.c_void_p(ctypes.sizeof(GLfloat)*3))

        # colour attribute
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, ctypes.sizeof(GLfloat)*10, ctypes.c_void_p(ctypes.sizeof(GLfloat)*6))

        # unbind
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        
    def _sync_vbo(self): # sync the vertex buffer object with the vertex data
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        vertex_data = (GLfloat * len(self.vertices))(*self.vertices)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(vertex_data), vertex_data, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def setVerteces(self, vertex1: tuple[float, float, float], vertex2: tuple[float, float, float], vertex3: tuple[float, float, float]): # set the verteces postions - only used for laserBeam as it needs to be a set length every frame
        # set new vertex pos
        pos1 = np.array(vertex1)
        pos2 = np.array(vertex2)
        pos3 = np.array(vertex3)

        # recompute normal
        edge1 = pos2 - pos1
        edge2 = pos3 - pos1
        normal = np.cross(edge1, edge2)
        normal = normal / np.linalg.norm(normal)

        self.vertices[0:3] = pos1.tolist()
        self.vertices[3:6] = normal.tolist()
        self.vertices[10:13] = pos2.tolist()
        self.vertices[13:16] = normal.tolist()
        self.vertices[20:23] = pos3.tolist()
        self.vertices[23:26] = normal.tolist()

        self._sync_vbo()

    def rotate(self, yawRotation, pitchRotation, rollRotation): # rotate the triangle
        # positions: 0,1,2 ; normals: 3,4,5 ; colors: 6,7,8,9
        pos1 = np.array(self.vertices[0:3], dtype=np.float32)
        pos2 = np.array(self.vertices[10:13], dtype=np.float32)
        pos3 = np.array(self.vertices[20:23], dtype=np.float32)

        # rotate positions
        rot_pos1 = np.dot(np.dot(np.dot(pos1, rollRotation), yawRotation), pitchRotation)
        rot_pos2 = np.dot(np.dot(np.dot(pos2, rollRotation), yawRotation), pitchRotation)
        rot_pos3 = np.dot(np.dot(np.dot(pos3, rollRotation), yawRotation), pitchRotation)

        # recompute normal
        edge1 = rot_pos2 - rot_pos1
        edge2 = rot_pos3 - rot_pos1
        normal = np.cross(edge1, edge2)
        normal = normal / np.linalg.norm(normal)

        # update vertices
        self.vertices[0:3] = rot_pos1.tolist()
        self.vertices[3:6] = normal.tolist()
        self.vertices[10:13] = rot_pos2.tolist()
        self.vertices[13:16] = normal.tolist()
        self.vertices[20:23] = rot_pos3.tolist()
        self.vertices[23:26] = normal.tolist()

        self._sync_vbo()

    def move(self, x, y, z): # move the triangle
        for i in range(0, len(self.vertices), 10):
            self.vertices[i] += x
            self.vertices[i+1] += y
            self.vertices[i+2] += z

        self._sync_vbo()

    def draw(self, shaderProgram): # draw the triangle
        # draw the triangle
        glUseProgram(shaderProgram)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)

    def cleanup(self): # clean up buffers
        # deleting buffers for when terminating program. Also reduces memory leak.
        glDeleteBuffers(1, [self.vbo])
        glDeleteVertexArrays(1, [self.vao])

class Main:
    def __init__(self, width, height, title): # create the window, shader program and ground
        # variables for the window
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        self.SHADER_DIR = os.path.join(os.path.dirname(__file__), "shaders")

        # check if glfw started
        if not glfw.init():
            raise SystemExit("Failed to initialize GLFW")
        
        # create the window
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.REFRESH_RATE, 10)

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            raise SystemExit("Failed to create GLFW window")
        
        # enable OpenGL functions
        glfw.make_context_current(self.window)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)  # enable backface culling for better optimisation
        glEnable(GL_BLEND)  # enable alpha blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # set blending function for transparency

        vertex_source = self._read_shader_file(os.path.join(self.SHADER_DIR, "vertex_shader.glsl"))
        fragment_source = self._read_shader_file(os.path.join(self.SHADER_DIR, "fragment_shader.glsl"))
        self.shaderProgram = self._create_shaderProgram(vertex_source, fragment_source)
        
        # Get uniform locations
        self.aspectRatioLoc = glGetUniformLocation(self.shaderProgram, "uAspectRatio")
        
        # Set aspect ratio uniform
        glUseProgram(self.shaderProgram)
        glUniform1f(self.aspectRatioLoc, self.width / self.height)
        glUseProgram(0)
        
        # default ground plane with per-vertex RGBA colours
        self.groundTriangle1 = Triangle(vertex1=(500.0, 0.0, -500.0), vertex2=(-500.0, 0.0, 500.0), vertex3=(500.0, 0.0, 500.0), colour1=(0.2, 0.7, 0.3, 1.0), colour2=(0.2, 0.7, 0.3, 1.0), colour3=(0.2, 0.7, 0.3, 1.0))
        self.groundTriangle2 = Triangle(vertex1=(-500.0, 0.0, 500.0), vertex2=(500.0, 0.0, -500.0), vertex3=(-500.0, 0.0, -500.0), colour1=(0.2, 0.7, 0.3, 1.0), colour2=(0.2, 0.7, 0.3, 1.0), colour3=(0.2, 0.7, 0.3, 1.0))

    def __get__(self): # get if the window should close and the shader program
        return (glfw.window_should_close(self.window), self.shaderProgram)
    
    def _read_shader_file(self, path: str) -> str: # read the shader files
        if not os.path.exists(path):
            raise FileNotFoundError(f"Shader file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _compile_shader(self, source: str, shader_type): # compile the shader program so the GPU can use it
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        compile_status = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not compile_status:
            error = glGetShaderInfoLog(shader).decode("utf-8")
            glDeleteShader(shader)
            raise RuntimeError(f"Shader compile error: {error}")

        return shader

    def _create_shaderProgram(self, vertex_source: str, fragment_source: str): # create a shader program
        vertex_shader = self._compile_shader(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = self._compile_shader(fragment_source, GL_FRAGMENT_SHADER)

        program = glCreateProgram()
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)

        link_status = glGetProgramiv(program, GL_LINK_STATUS)
        if not link_status:
            error = glGetProgramInfoLog(program).decode("utf-8")
            glDeleteProgram(program)
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
            raise RuntimeError(f"Program link error: {error}")

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        return program
    
    def _setWindowTitle(self, title): # set the title of the window
        glfw.set_window_title(self.window, title)

    def generateRotationMatricies(self, yaw, pitch, roll): # generate rotational matricies based on a yaw, pitch and roll value
        pitchRotation = np.matrix([[np.cos(radians(yaw)), 0, np.sin(radians(yaw))],
            [0, 1, 0],
            [-np.sin(radians(yaw)), 0, np.cos(radians(yaw))]]) # Y rotation
        
        yawRotation = np.matrix([[1, 0, 0],
            [0, np.cos(radians(pitch)), -np.sin(radians(pitch))],
            [0, np.sin(radians(pitch)), np.cos(radians(pitch))]]) # X rotation
        
        rollRotation = np.matrix([[np.cos(radians(roll)), -np.sin(radians(roll)), 0],
            [np.sin(radians(roll)), np.cos(radians(roll)), 0],
            [0, 0, 1]]) # Z rotation
        
        return yawRotation, pitchRotation, rollRotation
    
    def clearScreen(self): # clean the screen
        glfw.poll_events()
        skyColourRGB = (135, 206, 235)
        glClearColor(skyColourRGB[0]/255,skyColourRGB[1]/255, skyColourRGB[2]/255, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    def renderGround(self): # render the ground
        self.groundTriangle1.draw(self.shaderProgram)
        self.groundTriangle2.draw(self.shaderProgram)

    def updateScreen(self): # update the screen
        glfw.swap_buffers(self.window)

    def terminate(self): # cleanup buffers and shaders
        if hasattr(self, 'ground'):
            self.ground.cleanup()
        if hasattr(self, 'shaderProgram'):
            glDeleteProgram(self.shaderProgram)
        glfw.terminate()