import renderer
import laserbeam
import numpy as np
from math import sqrt, atan, atan2, degrees, radians

class Radar:
    def __init__(self, x, y, z, yaw, shaderProgram): # setup everything for the radar
        # variables for the radar
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = 0
        self.roll = 0
        self.shaderProgram = shaderProgram

        self.laserbeam = laserbeam.Beam(shaderProgram) # create the laserbeam

        # create faces for the radar
        v0 = (-2.5, -2.5, 2.5)
        v1 = (2.5, -2.5, 2.5)
        v2 = (2.5, 2.5, 2.5)
        v3 = (-2.5, 2.5, 2.5)
        v4 = (2.5, -2.5, -2.5)
        v5 = (-2.5, -2.5, -2.5)
        v6 = (-2.5, 2.5, -2.5)
        v7 = (2.5, 2.5, -2.5)

        c = (0.0, 0.75, 0.0, 1.0)

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

    def __set__(self, drone): # get the drone data
        self.drone = drone

    def render(self): # render the laserbeam and the radar, its self.
        self.laserbeam.render()

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

    def calculateDistance(self, x1, y1, z1, x2, y2, z2): # calculate the distance between 2 3D points
        dx = x2-x1
        dy = y2-y1
        dz = z2-z1
        distance = sqrt(dx**2+dy**2+dz**2)
        return distance

    def update(self, dt): # calculate the yaw and pitch for the laserbeam.
        # Here an actual radar could be used instand of calculating the drone's postion insead of accessing it directly
        # I have used some trigonometry to calculate the yaw, pitch and length for the laserbeam to be set to.
        distance = self.calculateDistance(self.x, self.y, self.z, self.drone.x, self.drone.y, self.drone.z)
        dx = self.drone.x-self.x
        dy = self.drone.y-self.y
        dz = self.drone.z-self.z

        yaw = -degrees(atan2((dx), (dz)))
        
        dxz = sqrt(dx**2+dz**2)

        pitch = degrees(atan2((dy), (dxz)))

        self.laserbeam.__set__(self.x, self.y, self.z, yaw, pitch)
        self.laserbeam.setlength(distance)
        self.laserbeam.updateVertecies()

    def terminate(self): # clean up buffers and faces
        self.laserbeam.terminate()

        for i in range(len(self.faces)):
            for j in range(len(self.faces[i])):
                self.faces[i][j].cleanup()
