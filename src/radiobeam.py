import renderer
import numpy as np

class Beam:
    def __init__(self, shaderProgram): # setup everything for the radiobeam
        # variables for the beam
        self.x = 0
        self.y = -100 # set it to be under the map
        self.z = 0
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.shaderProgram = shaderProgram
        self.length = 1000

        # creating faces
        v0 = (-0.5, -0.5, 0)
        v1 = (0.5, -0.5, 0)
        v2 = (0.5, 0.5, 0)
        v3 = (-0.5, 0.5, 0)
        v4 = (0.5, -0.5, self.length)
        v5 = (-0.5, -0.5, self.length)
        v6 = (-0.5, 0.5, self.length)
        v7 = (0.5, 0.5, self.length)

        c = (0.0, 0.0, 1.0, 0.5)

        face1 = (renderer.Triangle(v0, v1, v2, c, c, c), 
                 renderer.Triangle(v0, v2, v3, c, c, c))  # front +Z

        face2 = (renderer.Triangle(v5, v0, v3, c, c, c),
                 renderer.Triangle(v5, v3, v6, c, c, c))  # left -X

        face3 = (renderer.Triangle(v4, v5, v6, c, c, c),
                 renderer.Triangle(v4, v6, v7, c, c, c))  # back -Z

        face4 = (renderer.Triangle(v1, v4, v7, c, c, c),
                 renderer.Triangle(v1, v7, v2, c, c, c))  # right +X

        face5 = (renderer.Triangle(v5, v4, v1, c, c, c),
                 renderer.Triangle(v5, v1, v0, c, c, c))  # bottom -Y

        face6 = (renderer.Triangle(v3, v2, v7, c, c, c),
                 renderer.Triangle(v3, v7, v6, c, c, c))  # top +Y
        
        self.faces = (face1, face2, face3, face4, face5, face6)

    def __set__(self, x, y, z, yaw, pitch): # set the x, y, z, yaw and pitch of the beam
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch

    def render(self): # render the radioBeam
        yawRotation, pitchRotation, rollRotation = renderer.generateRotationMatricies(self.yaw, self.pitch, self.roll) # rotations matricies

        for i in range(len(self.faces)):
            for j in range(len(self.faces[i])):
                orig_vertices = self.faces[i][j].vertices.copy() # copy vertices to reset to original state

                self.faces[i][j].rotate(yawRotation, pitchRotation, rollRotation)
                self.faces[i][j].move(self.x, self.y, self.z)
                self.faces[i][j].draw(self.shaderProgram)

                # restore exact original state (no accumulation)
                self.faces[i][j].vertices = orig_vertices
                self.faces[i][j]._sync_vbo()

    def terminate(self): # cleanup buffers and faces
        for i in range(len(self.faces)):
            for j in range(len(self.faces[i])):
                self.faces[i][j].cleanup()