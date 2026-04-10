import renderer
import numpy as np

import random
from time import perf_counter_ns

class Drone:
    def __init__(self, x, y, z, vx, vy, vz, yaw, pitch, roll, throttle, shaderProgram): # setup everything for the drone
        # define variables for the drone
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.yaw = yaw # also know as the greek letter kappa
        self.pitch = pitch # also know as the greek letter phi
        self.roll = roll # also know as the greek letter theta
        self.throttle = throttle # 0 - 1 range
        self.mass = 900
        self.massThrottlePower = 2700
        self.gravity = 9.81
        self.start = perf_counter_ns()
        self.dragCoefficient = 0.99

        self.state = "normal"
        self.jamDirectionBias = (random.random()*2-1, random.random()*2-1, random.random()*2-1) # a random bais between -1 and 1 for yaw, pitch and roll. This is used when the drone is jammed
        
        # create the drone's faces
        # cubeoid vertex coordinates

        # defining the vertecies
        v0 = (-1, -1, 2)
        v1 = (1, -1, 2)
        v2 = (1, 1, 2)
        v3 = (-1, 1, 2)
        v4 = (1, -1, -2)
        v5 = (-1, -1, -2)
        v6 = (-1, 1, -2)
        v7 = (1, 1, -2)

        self.vertecies = [v0, v1, v2, v3, v4, v5, v6, v7]

        # red
        c = (1.0, 0, 0, 1.0)

        # triangle aguments - (vertexPos1, vertexPos2, vertexPos3, colourVertex1, colourVertex2, colourVertex3)

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
        
        self.faces = [face1, face2, face3, face4, face5, face6]

        # propeller blades
        # 1 quater the depth but only 1 half the height and width

        XOffset = 5/3
        ZOffset = 1

        for XSign in range(-1, 2, 2):
            for ZSign in range(-1, 2, 2):

                propellerXOffset = XSign*XOffset
                propellerZOffset = ZSign*ZOffset
        
                v0 = (-2/3+propellerXOffset, -1/3, 2/3+propellerZOffset)
                v1 = (2/3+propellerXOffset, -1/3, 2/3+propellerZOffset)
                v2 = (2/3+propellerXOffset, 1/3, 2/3+propellerZOffset)
                v3 = (-2/3+propellerXOffset, 1/3, 2/3+propellerZOffset)
                v4 = (2/3+propellerXOffset, -1/3, -2/3+propellerZOffset)
                v5 = (-2/3+propellerXOffset, -1/3, -2/3+propellerZOffset)
                v6 = (-2/3+propellerXOffset, 1/3, -2/3+propellerZOffset)
                v7 = (2/3+propellerXOffset, 1/3, -2/3+propellerZOffset)

                self.vertecies.append(v0)
                self.vertecies.append(v1)
                self.vertecies.append(v2)
                self.vertecies.append(v3)
                self.vertecies.append(v4)
                self.vertecies.append(v5)
                self.vertecies.append(v6)
                self.vertecies.append(v7)

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
                
                self.faces.append(face1)
                self.faces.append(face2)
                self.faces.append(face3)
                self.faces.append(face4)
                self.faces.append(face5)
                self.faces.append(face6)

        self.shaderProgram = shaderProgram

    def render(self): # render the drone
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
                
    def rotateVector(self, vector, yawRotation, pitchRotation, rollRotation): # rotate a vector - used to calculate acceloration
        rotatedVector = np.dot(np.dot(np.dot(vector, rollRotation), yawRotation), pitchRotation)

        return rotatedVector
    
    def groundCollision(self): # if any vertecies are below the ground then this function is ran
        # set state, rotations, velocites, y-position and throttle to ensure the drone is static.
        self.state = "normal"
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.y = 0.99 # just below 1 so it will always collide the the ground and not become the jammed state
        self.throttle = 1/3

    def checkCheckGroundCollision(self): # check if any of the vertecies are below the ground
        yawRotation, pitchRotation, rollRotation = renderer.generateRotationMatricies(self.yaw, self.pitch, self.roll) # rotations matricies

        for vertex in self.vertecies:
            rotatedPos = np.dot(np.dot(np.dot(np.array(vertex), rollRotation), yawRotation), pitchRotation)
            newPos = rotatedPos+np.array([self.x, self.y, self.z])
            if newPos[1] < 0:
                self.groundCollision()

    def update(self, dt): # update the drone
        # add motion to the drone
        self.x += self.vx*dt*self.dragCoefficient
        self.y += self.vy*dt*self.dragCoefficient
        self.z += self.vz*dt*self.dragCoefficient

        # apply gravity
        self.vy -= self.gravity*dt

        # calculate the force force based on the throttle and the drone's rotation
        acceloration = (self.throttle*self.massThrottlePower*self.gravity)/self.mass
        yawRotation, pitchRotation, rollRotation = renderer.generateRotationMatricies(self.yaw, self.pitch, self.roll) # rotations matricies
        accelorationVector = np.array([0, acceloration, 0], dtype=np.float32)

        rotatedAccelorationVector = self.rotateVector(accelorationVector, yawRotation, pitchRotation, rollRotation)

        # apply the force to the velocity of the drone
        self.vx += rotatedAccelorationVector[0]*dt
        self.vy += rotatedAccelorationVector[1]*dt
        self.vz += rotatedAccelorationVector[2]*dt

        # check if it has been 2.5s

        if (perf_counter_ns()-self.start)/1000000000 > 2.5:
            self.state = "jammed"

        # check if the drone has collided with the ground
        self.checkCheckGroundCollision()

        if self.state == "jammed": # if the drone is jammed it will calculate a random yaw, pitch and roll value to apply to the drone. Theses values and tuned by a weight for all the rotations.
            value1Yaw = round(250*self.jamDirectionBias[0])
            value2Yaw = round(250*(1-((2-(self.jamDirectionBias[0]+1))-1)))
            if value1Yaw < value2Yaw:
                self.yaw += random.randint(value1Yaw, value2Yaw)*dt
            else:
                self.yaw += random.randint(value2Yaw, value1Yaw)*dt

            value1Pitch = round(250*self.jamDirectionBias[1])
            value2Pitch = round(250*(1-((2-(self.jamDirectionBias[1]+1))-1)))
            if value1Pitch < value2Pitch:
                self.pitch += random.randint(value1Pitch, value2Pitch)*dt
            else:
                self.pitch += random.randint(value2Pitch, value1Pitch)*dt

            value1Roll = round(250*self.jamDirectionBias[2])
            value2Roll = round(250*(1-((2-(self.jamDirectionBias[2]+1))-1)))
            if value1Roll < value2Roll:
                self.roll += random.randint(value1Roll, value2Roll)*dt
            else:
                self.roll += random.randint(value2Roll, value1Roll)*dt

            # set the drone's throttle to be between 0 and 2x throttle
            self.throttle = 2*random.random()/3

    def terminate(self): # clean up buffers and faces
        for i in range(len(self.faces)):
            for j in range(len(self.faces[i])):
                self.faces[i][j].cleanup()
