import re
import sys
from heapq import heappop, heappush
from math import ceil, sqrt, floor

from PIL import Image, ImageDraw


# To do : pixelchange speed should be relative to the pixel
def readimage(imageName):
    with Image.open(imageName) as im:
        colorpixel = list()
        for y in range(im.height):
            elev = list()
            for x in range(im.width):
                val = tuple(im.getpixel((x, y))[k] for k in range(len(im.getpixel((x, y))) - 1))
                elev.append(val)
            colorpixel.append(elev)
    return colorpixel


def getTerrains(season=""):
    tarrainInfo = dict()
    tarrainInfo[(248, 148, 18)] = 0.20  # Open land
    tarrainInfo[(255, 192, 0)] = 0.8  # Rough meadow
    tarrainInfo[(255, 255, 255)] = 0.2  # Easy movement forest
    tarrainInfo[(2, 208, 60)] = 0.70  # Slow run forest
    tarrainInfo[(2, 136, 40)] = 0.50  # Walk forest
    tarrainInfo[(5, 73, 24)] = -1000  # Impassible vegetation
    tarrainInfo[(0, 0, 255)] = -1000  # Lake/Swamp/Marsh
    tarrainInfo[(71, 51, 3)] = 0  # Paved road
    tarrainInfo[(0, 0, 0)] = 0.1  # Footpath
    tarrainInfo[(205, 0, 101)] = -1000  # Out of bounds
    tarrainInfo[(22, 255, 255)] = 0  # snowcolor
    tarrainInfo[(89, 39, 32)] = 0.4  # mudcolor

    return tarrainInfo


def isvalidcoordinate(point, map):
    if 0 <= int(point[0]) < len(map[0]) and 0 <= int(point[1]) < len(map):
        return True
    return False


def bfsWinterSpringcolor(colorpixel, start, season, elevation):
    visitedNode = set()
    path = list()
    queue = list()
    queue.append(start)
    if season == "winter":
        path.append(start)
    waterelevation = elevation[start[1]][start[0]]
    curPoint = start

    while len(queue) != 0:
        if curPoint in visitedNode:
            curPoint = queue.pop(0)

        for point in getCoordinate():
            currentpoint = (curPoint[0] + point[0], curPoint[1] + point[1])
            if not isvalidcoordinate(currentpoint, colorpixel):
                continue
            curPixColor = colorpixel[currentpoint[1]][currentpoint[0]]
            if currentpoint not in visitedNode and currentpoint not in queue:
                if season == "winter":
                    if curPixColor == (0, 0, 255):
                        if getDistance(start, currentpoint, elevation) >= 7:
                            return path
                        path.append(currentpoint)
                        queue.append(currentpoint)

                elif season == "spring":
                    if curPixColor != (0, 0, 255):

                        if (floor(abs(elevation[currentpoint[1]][currentpoint[0]] - waterelevation)) > 1 and
                            elevation[currentpoint[1]][currentpoint[0]] > waterelevation) or curPixColor == (
                                205, 0, 101):
                            visitedNode.add(currentpoint)
                        else:
                            if getDistance(start, currentpoint, elevation) >= 15:
                                return path
                            waterelevation = elevation[currentpoint[1]][currentpoint[0]]
                            path.append(currentpoint)
                            queue.append(currentpoint)
                elif season == "path":
                    if getDistance(start, currentpoint, elevation) >= 4:
                        return path
                    path.append(currentpoint)
                    queue.append(currentpoint)

        visitedNode.add(curPoint)
    return path


def getCoordinate():
    coordinate = list()
    coordinate.append((1, 0))
    coordinate.append((-1, 0))
    coordinate.append((0, 1))
    coordinate.append((0, -1))
    return coordinate


def findWater(colorpixel):
    wateredges = set()
    for y in range(len(colorpixel)):
        for x in range(len(colorpixel[y])):
            if colorpixel[y][x] == (0, 0, 255):
                for point in getCoordinate():
                    currentpoint = x + point[0], y + point[1]
                    if isvalidcoordinate(currentpoint, colorpixel) and (
                            colorpixel[currentpoint[1]][currentpoint[0]]) != (0, 0, 255):
                        wateredges.add((x, y))
    return wateredges


def aStar(start, end, mapdetails, elevationpath, season):
    terrains = getTerrains(season)
    path = dict()
    path[start] = None, 0, 0, 0
    priorityList = []
    visitednodes = set()
    finaldistance = (0, 0), -1
    priorityList.append((getDistance(start, end, elevationpath), start))
    ispathfound = False
    while len(priorityList) != 0 and not ispathfound:  # int(start[0]) != int(end[0]) or (int(start[1]) != int(end[1])):
        xcoordinate = int(start[0])
        yCoordinate = int(start[1])
        totalcost = path[(xcoordinate, yCoordinate)][2]
        distance = path[(xcoordinate, yCoordinate)][3]
        tarrainfriction = terrains.get(mapdetails[yCoordinate][xcoordinate])
        if tarrainfriction is None or tarrainfriction == -1000:
            visitednodes.add(start)
        currtime = (elevationpath[yCoordinate][xcoordinate] * tarrainfriction) / 2
        if start in visitednodes:
            start = heappop(priorityList)[1]
            continue
        for co in getCoordinate():
            nextcoordinate = co[0] + xcoordinate, co[1] + yCoordinate
            if isvalidcoordinate(nextcoordinate, mapdetails) and nextcoordinate not in visitednodes:

                hr = getDistance(nextcoordinate, end, elevationpath)
                nexttrrainfriction = terrains.get(mapdetails[nextcoordinate[1]][nextcoordinate[0]])
                pathValue = path.get(nextcoordinate)
                eleval = (elevationpath[nextcoordinate[1]][nextcoordinate[0]] * nexttrrainfriction) / 2 + currtime
                if (mapdetails[yCoordinate][xcoordinate] == (255, 255, 255) or mapdetails[nextcoordinate[1]][
                    nextcoordinate[0]]) and season == "fall":
                    tarrainfriction += 0.1
                    currtime *= 1.25
                newdistance = distance + (7.55 if nextcoordinate[0] == xcoordinate else 10.29 if nextcoordinate[1] == yCoordinate else 12.76)
                newdistance += abs(elevationpath[nextcoordinate[1]][nextcoordinate[0]] - elevationpath[yCoordinate][xcoordinate])
                if pathValue is None or int(pathValue[1]) > hr + totalcost + 1 + eleval:
                    path[nextcoordinate] = start, hr, totalcost + 1 + eleval, newdistance
                if hr == 0:
                    finaldistance = nextcoordinate
                    ispathfound = True
                    break
                heappush(priorityList, (hr + totalcost + 1 + eleval, nextcoordinate))
        visitednodes.add(start)
        start = heappop(priorityList)[1]

    finalpath = list()
    finalpath.append(end)
    finalpath.append(finaldistance)

    while path.get(finalpath[len(finalpath) - 1]) is not None and path.get(finalpath[len(finalpath) - 1])[
        0] is not None:
        # print(path[finalpath[len(finalpath) - 1]][0])
        finalpath.append(path[finalpath[len(finalpath) - 1]][0])
    return finalpath, path[finaldistance][3]


def getDistance(start, end, elevationpath):
    xpos = abs((int(start[0]) - int(end[0])) ** 2)
    ypos = abs((int(start[1]) - int(end[1])) ** 2)
    zpos = abs((elevationpath[start[1]][start[0]] - elevationpath[end[1]][end[0]]) ** 2)
    hr = ceil(sqrt(xpos + ypos + zpos))
    return hr


def readPath(fileName):
    path = list()
    with open(fileName) as f:
        for line in f:
            cordinate = line.strip().split(" ")
            path.append((int(cordinate[0]), int(cordinate[1])))
    return path


def readelevation(fileName):
    mapp = list()
    with open(fileName) as f:
        for line in f:
            elev = list()
            for elevation in re.split('\s+', line):
                # print(elevation.split("   "))
                if elevation != "":
                    elev.append(float(elevation.strip()))
            mapp.append(elev)
    return mapp


def readepath(fileName):
    mapp = list()
    with open(fileName) as f:
        for line in f:
            elev = list()
            for elevation in line.strip().split("   "):
                # print(elevation.split("   "))
                elev.append(float(elevation))
            mapp.append(elev)
    return mapp


def getcolorforseason(season):
    if season == "winter":
        return 22, 255, 255
    return 89, 39, 32


def modifyNReadSeasonmap(imageName, OutputImage, elevation, season):
    colorpixel = readimage(imageName)
    pointToUpdate = list()
    if season == "winter" or season == "spring":
        water = findWater(colorpixel)
        for waterpoint in water:
            pointToUpdate.append(bfsWinterSpringcolor(colorpixel, waterpoint, season, elevation))
    count =0
    with Image.open(imageName) as im:
        draw = ImageDraw.Draw(im)
        for eachpath in pointToUpdate:
            for point in eachpath:
                count += 1
                draw.point(point, getcolorforseason(season))
        im.save(OutputImage)
    colorpixel = readimage(OutputImage)
    return colorpixel


def showoutput(outputFile, finalpath, colorpixel, path, elevation):
    distance = 0
    with Image.open(outputFile) as im:
        draw = ImageDraw.Draw(im)
        i = 0
        for eachpath in finalpath:
            distance += float(eachpath[1])
            for point in eachpath[0]:
                if (isvalidcoordinate(point, colorpixel)):
                    draw.point(point, (255, 0, 255))
        for point in path:
            for lap in bfsWinterSpringcolor(colorpixel, point, "path", elevation):
                draw.point(lap, (20, 0, 255))
        im.save(outputFile)
        im.show()
    print("Distance :", round(distance))


def main():
    if len(sys.argv) == 6:
        print("program execution start:")
        imageName = sys.argv[1]
        elevationFileName = sys.argv[2]
        pathfile = sys.argv[3]
        season = sys.argv[4]
        outputFile = sys.argv[5]
        elevation = readelevation(elevationFileName)
        path = readPath(pathfile)
        colorpixel = modifyNReadSeasonmap(imageName, outputFile, elevation, season)
        finalpath = list()
        for index in range(len(path) - 1):
            finalpath.append(aStar(path[index], path[index + 1], colorpixel, elevation, season))
        distance = 00.0
        showoutput(outputFile, finalpath, colorpixel, path, elevation)
        print("program execution end:")


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
