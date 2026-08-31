import cv2

def scar_length(contour):

    x,y,w,h = cv2.boundingRect(contour)

    return max(w,h)
    
def distance(p1, p2):
    return math.sqrt(
        (p2[0]-p1[0])**2 +
        (p2[1]-p1[1])**2
    )    