import renderer
import numpy as np

class Beam:
    def __init__(self, shaderProgram): # setup everything for the laserbeam
        # setup everything for the laserbeam
        self.x = 0
        self.y = -100 # set it to be under the map
        self.z = 0
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.shaderProgram = shaderProgram
        self.length = 100

        v0 = (-0.1, -0.1, 0) # set the starting Z to be 0 so it doesn't go backwards through the radar
        v1 = (0.1, -0.1, 0)
        v2 = (0.1, 0.1, 0)
        v3 = (-0.1, 0.1, 0)
        v4 = (0.1, -0.1, self.length)
        v5 = (-0.1, -0.1, self.length)
        v6 = (-0.1, 0.1, self.length)
        v7 = (0.1, 0.1, self.length)

        c = (1.0, 0.0, 0.0, 0.5)

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

    def __set__(self, x, y, z, yaw, pitch): # set the x, y, z, yaw and pitch of the laserbeam
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch

    def setlength(self, length): # set the length of the laserbeam
        self.length = length

    def updateVertecies(self): # update the length of the laser beam so it does not go through the drone
        v0 = (-0.1, -0.1, 0)
        v1 = (0.1, -0.1, 0)
        v2 = (0.1, 0.1, 0)
        v3 = (-0.1, 0.1, 0)
        v4 = (0.1, -0.1, self.length)
        v5 = (-0.1, -0.1, self.length)
        v6 = (-0.1, 0.1, self.length)
        v7 = (0.1, 0.1, self.length)

        self.faces[1][0].setVerteces(v5, v0, v3)
        self.faces[1][1].setVerteces(v5, v3, v6)

        self.faces[2][0].setVerteces(v4, v5, v6)
        self.faces[2][1].setVerteces(v4, v6, v7)

        self.faces[3][0].setVerteces(v1, v4, v7)
        self.faces[3][1].setVerteces(v1, v7, v2)

        self.faces[4][0].setVerteces(v5, v4, v1)
        self.faces[4][1].setVerteces(v5, v1, v0)

        self.faces[5][0].setVerteces(v3, v2, v7)
        self.faces[5][1].setVerteces(v3, v7, v6)

    def render(self): # render the laserBeam.
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