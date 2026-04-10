import renderer
import drone
import sentry
import radar

import math
from time import perf_counter_ns

class Main:
    def __init__(self, width, height, title):
        # set up rendering i.e - setting up the window and handling drawing
        self.renderer = renderer.Main(width, height, title)

        self.shaderProgram = self.renderer.__get__()[1]

        self.drone = drone.Drone(-10, 10, 0, 0, 0, 0, 90, 15, 0, 2/5, self.shaderProgram) # x, y, z, vx, vy, vz, yaw, pitch, roll, shader

        self.sentries = []
        self.sentries = self.createSentry(self.sentries, 25, 2.5, 0, 0, self.shaderProgram) # x, y, z, yaw, shader
        self.sentries = self.createSentry(self.sentries, -12.5, 2.5, math.cos(math.radians(30))*25, 30, self.shaderProgram) # x, y, z, yaw, shader
        self.sentries = self.createSentry(self.sentries, -12.5, 2.5, -math.cos(math.radians(30))*25, 60, self.shaderProgram) # x, y, z, yaw, shader
        self.radars = []
        self.radars = self.createRadar(self.radars, -25, 2.5, 0, 0, self.shaderProgram) # x, y, z, yaw, shader
        self.radars = self.createRadar(self.radars, 12.5, 2.5, math.cos(math.radians(30))*25, 60, self.shaderProgram) # x, y, z, yaw, shader
        self.radars = self.createRadar(self.radars, 12.5, 2.5, -math.cos(math.radians(30))*25, 30, self.shaderProgram) # x, y, z, yaw, shader

        self.running = True
        self.last = perf_counter_ns()

    def createSentry(self, sentries, x, y, z, yaw, shader): # x, y, z, yaw, shader
        sentryObject = sentry.Sentry(x, y, z, yaw, shader)
        sentryObject.__set__(self.drone)
        sentries.append(sentryObject)
        return sentries
    
    def createRadar(self, radars, x, y, z, yaw, shader): # x, y, z, yaw, shader
        radarObject = radar.Radar(x, y, z, yaw, shader)
        radarObject.__set__(self.drone)
        radars.append(radarObject)
        return radars
    
    def update(self): # update everything
        self.drone.update(self.dt)
        
        for sentry in self.sentries:
            sentry.update(self.dt)

        for radar in self.radars:
            radar.update(self.dt)

    def render(self): # render everything
        self.renderer.clearScreen()
        self.renderer.renderGround()

        for sentry in self.sentries:
            sentry.render()

        for radar in self.radars:
            radar.render()

        self.drone.render()

    def updateScreen(self): # update the screen
        self.renderer.updateScreen()

    def calculateDelta(self): # calculate delta time
        self.current = perf_counter_ns()
        difference = self.current-self.last
        if difference == 0:
            self.dt = 1/1000000000
        else:
            self.dt = difference/1000000000
        self.last = self.current
        

    def run(self): #  main process
        while self.running:
            self.calculateDelta()

            #self.renderer._setWindowTitle('fps: '+str(1/self.dt)) # set the title ofthe window to be the fps

            if self.renderer.__get__()[0]:
                self.running = False
                self.terminate()
                break
            
            self.render()

            self.update()

            self.updateScreen()

    def terminate(self): # end everything - clear buffers close screen, delete variables
        self.renderer.terminate()
        self.drone.terminate()

        for sentry in self.sentries:
            sentry.terminate()

        for radar in self.radars:
            radar.terminate()

        self.running = False

if __name__ == "__main__": # check if this file is being ran directly or from another source
    # defining key variables
    width = input("Enter the wanted width (or press enter for the default of 900): ")
    if width.isnumeric():
        width = int(width)
    else:
        width = 900

    height = input("Enter the wanted height (or press enter for the default of 700): ")
    if height.isnumeric():
        height = int(height)
    else:
        height = 700

    title = input("Enter the wanted title (or press enter for the default of 'Drone Defense'): ")
    if title == '':
        title = "Drone Defense"

    # run the program
    app = Main(width, height, title)
    app.run()
