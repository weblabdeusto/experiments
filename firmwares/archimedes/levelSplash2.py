import cv2
import numpy as np
import math


rutaFoto='/var/www/images/hdpicture.jpg'
rutaLevel='/opt/restlite/level'
cannyT=10
limSup=316.0
limInf=748.0
dist=13
ad=7
rot=90



def rotateImage(src, angle, scale=1.):
            w = src.shape[1]
            h = src.shape[0]
            rangle = np.deg2rad(angle)  # angle in radians
       	    # now calculate new image width and height
    	    nw = (abs(np.sin(rangle)*h) + abs(np.cos(rangle)*w))*scale
            nh = (abs(np.cos(rangle)*h) + abs(np.sin(rangle)*w))*scale
	    # ask OpenCV for the rotation matrix
    	    rot_mat = cv2.getRotationMatrix2D((nw*0.5, nh*0.5), angle, scale)
            # calculate the move from the old center to the new center combined
	    # with the rotation
    	    rot_move = np.dot(rot_mat, np.array([(nw-w)*0.5, (nh-h)*0.5,0]))
            # the move only affects the translation, so update the translation
            # part of the transform
    	    rot_mat[0,2] += rot_move[0]
            rot_mat[1,2] += rot_move[1]
	    return cv2.warpAffine(src, rot_mat, (int(math.ceil(nw)), int(math.ceil(nh))), flags=cv2.INTER_LANCZOS4)



cap = cv2.VideoCapture(0)
cap.set(3,800)
cap.set(4,600)
levelP=0
levelP2=0
up=800
while(1):

    # Take each frame
    _, frame = cap.read()
    frame=rotateImage(frame,90)
    cv2.imwrite(rutaFoto,frame)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower_blue = np.array([70,160,165])
    upper_blue = np.array([180,255,255])
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask)

    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    edges1 = cv2.Canny(gray, cannyT,cannyT*3)
    lines = cv2.HoughLinesP(edges1, 1, math.pi/2, 2, minLineLength = 3);
    if lines!=None:
        for line in lines[0]:
            if (line[1]-line[3]>=-7)and(line[1]-line[3]<=7):
	        if line[1]<up:
                    up=line[1]
                    pt1 = (line[0],line[1])
                    pt2 = (line[2],line[3])
                    cv2.line(frame, pt1, pt2, (0,0,255))

        level=round((((limInf-up)/(limInf-limSup))*dist)+ad,1)    
        print 'incoming level:' +str(level)
        if (level!=levelP):
            levelP=level
        else:
            if level!=levelP2:
                 levelP2=level
            else:
                print 'setting:' +str(level)
                up=800
                levelf=open(rutaLevel,'w')
                levelf.write(str(level))		
                levelf.close()
        print levelP
        print levelP2
        print '-'

    cv2.line(frame, (160,int(limInf)), (410,int(limInf)), (255,0,0), 1)
    cv2.line(frame, (160,int(limSup)), (410,int(limSup)), (255,0,0), 1)
#    cv2.imwrite('frame.jpg',frame)
#    cv2.imwrite('mask.jpg',mask)
#    cv2.imwrite('res.jpg',res)
