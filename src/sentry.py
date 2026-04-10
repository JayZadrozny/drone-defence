import renderer
import numpy as np
import radiobeam

from math import radians, degrees, atan2, sqrt
from time import perf_counter_ns

class Sentry:
    def __init__(self, x, y, z, yaw, shaderProgram): # setup everything for the sentry
        # variables for the beam
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = 0
        self.roll = 0
        self.shaderProgram = shaderProgram
        self.start = perf_counter_ns()

        self.radarbeam = radiobeam.Beam(shaderProgram)

        # creating sentry faces
        v0 = (-2.5, -2.5, 2.5)
        v1 = (2.5, -2.5, 2.5)
        v2 = (2.5, 2.5, 2.5)
        v3 = (-2.5, 2.5, 2.5)
        v4 = (2.5, -2.5, -2.5)
        v5 = (-2.5, -2.5, -2.5)
        v6 = (-2.5, 2.5, -2.5)
        v7 = (2.5, 2.5, -2.5)

        c = (0.0, 0.0, 1.0, 1.0) # blue

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
                 renderer.Triangle(v3, v7, v6, c, c, c)) # top +Y
        
        self.faces = (face1, face2, face3, face4, face5, face6)

    def __set__(self, drone): # get the drone data
        self.drone = drone

    def render(self): # render the radarBeam and the sentry
        self.radarbeam.render()

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

    def calculateDistance(self, x1, y1, z1, x2, y2, z2): # calculate a distance between 2 3D points
        dx = x2-x1
        dy = y2-y1
        dz = z2-z1
        distance = sqrt(dx**2+dy**2+dz**2)
        return distance

    def update(self, dt): # check if it has been 2.5 seconds - 'warm up phase'
        if (perf_counter_ns()-self.start)/1000000000 > 2.5:
            self.shootRadarBeam()

    def shootRadarBeam(self): # calculate the x, y,z, yaw and pitch the beam needs to have
        # Here I am directly accessing the drone data.
        # However I could use the data from the radars to calculate this instead of raw drone data.
        distance = self.calculateDistance(self.x, self.y, self.z, self.drone.x, self.drone.y, self.drone.z)
        dx = self.drone.x-self.x
        dy = self.drone.y-self.y
        dz = self.drone.z-self.z

        yaw = -degrees(atan2((dx), (dz)))
        
        dxz = sqrt(dx**2+dz**2)

        pitch = degrees(atan2((dy), (dxz)))

        self.radarbeam.__set__(self.x, self.y, self.z, yaw, pitch)

    def terminate(self): # cleanup buffers and faces
        self.radarbeam.terminate()

        for i in range(len(self.faces)):
            for j in range(len(self.faces[i])):
                self.faces[i][j].cleanup()