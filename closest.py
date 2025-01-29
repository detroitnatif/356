import math
# HW2 Q4
class ClosestPair:
    def __init__(self, inputPoints):
        self.inputPoints = inputPoints

    def findMinimumDistance(self):
        length = len(self.inputPoints)
        if length < 2:
            return 0.0
        pointsX = self._mergeSort(self.inputPoints, keyFunc=lambda p: p[0])
        pointsY = self._mergeSort(self.inputPoints, keyFunc=lambda p: p[1])
        return math.sqrt(self.CPR(pointsX, pointsY))

    def CPR(self, pointsX, pointsY):
        length = len(pointsX)
        if length <= 3:
            minVal = float('inf')
            for i in range(length):
                for j in range(i + 1, length):
                    distSq = ((pointsX[i][0] - pointsX[j][0]) ** 2 +
                              (pointsX[i][1] - pointsX[j][1]) ** 2)
                    if distSq < minVal:
                        minVal = distSq
            return minVal

        midIndex = length // 2
        midX = pointsX[midIndex][0]
        leftPointsX = pointsX[:midIndex]
        rightPointsX = pointsX[midIndex:]

        leftPointsY = []
        rightPointsY = []
        for p in pointsY:
            if p[0] < midX:
                leftPointsY.append(p)
            else:
                rightPointsY.append(p)

        leftDist = self.CPR(leftPointsX, leftPointsY)
        rightDist = self.CPR(rightPointsX, rightPointsY)

        dSq = min(leftDist, rightDist)
        d = math.sqrt(dSq)

        sdt = []
        for p in pointsY:
            if abs(p[0] - midX) < d:
                sdt.append(p)

        minVal = dSq
        sdtLen = len(sdt)

        for i in range(sdtLen):
            j = i + 1
            while j < sdtLen and (sdt[j][1] - sdt[i][1]) ** 2 < minVal:
                distSq = ((sdt[i][0] - sdt[j][0]) ** 2 +
                          (sdt[i][1] - sdt[j][1]) ** 2)
                if distSq < minVal:
                    minVal = distSq
                j += 1

        return min(dSq, minVal)

    def _mergeSort(self, array, keyFunc):
        arrLen = len(array)
        if arrLen <= 1:
            return array[:]
        midIndex = arrLen // 2
        leftArray = self._mergeSort(array[:midIndex], keyFunc)
        rightArray = self._mergeSort(array[midIndex:], keyFunc)
        return self._merge(leftArray, rightArray, keyFunc)

    def _merge(self, leftArray, rightArray, keyFunc):
        mergedList = []
        i = j = 0
        while i < len(leftArray) and j < len(rightArray):
            if keyFunc(leftArray[i]) <= keyFunc(rightArray[j]):
                mergedList.append(leftArray[i])
                i += 1
            else:
                mergedList.append(rightArray[j])
                j += 1
        mergedList.extend(leftArray[i:])
        mergedList.extend(rightArray[j:])
        return mergedList

def minimum_distance(points):
    solver = ClosestPair(points)
    return solver.findMinimumDistance()

if __name__ == 'main':
    minimum_distance()