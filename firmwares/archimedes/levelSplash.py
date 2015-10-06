import cv2
import numpy as np
import math
import time
import threading

class gestorCam(object):

	def __init__(self):
		self.rutaFoto='/var/www/images/hdpicture.jpg'
		self.rutaLevel='/opt/restlite/level'
		self.Cam=cv2.VideoCapture(0)
		self.cannyT=30
		self.limSup=356.0
		self.limInf=742.0
		self.dist=16.0
		self.ad=8
		self.rot=270

	def hiloProces(self):

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


		self.Cam.set(3,800)
		self.Cam.set(4,600)
		while True:
			try:
				aux=0
				contLines=0
				level=0
				while contLines==0:
					c,img = self.Cam.read()
				        if c is not True:
				           	print 'Error al tomar foto'
				        else:
				           	img=rotateImage(img,self.rot)
						cv2.imwrite(self.rutaFoto,img)
				           	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				           	edges1 = cv2.Canny(gray, self.cannyT,self.cannyT*3)
			               		lines = cv2.HoughLinesP(edges1, 1, math.pi/2, 2, minLineLength = 20);
			               		cv2.line(img, (180,int(self.limInf)), (380,int(self.limInf)), (255,0,0), 1)
			               		cv2.line(img, (180,int(self.limSup)), (380,int(self.limSup)), (255,0,0), 1)
			               		for line in lines[0]:
			                       		pt1 = (line[0],line[1])
			                       		pt2 = (line[2],line[3])
			                       		if (line[1]-line[3]>=-4)and(line[1]-line[3]<=4)and(line[0]>180)and(line[0]<400)and(line[1]<self.limInf)and(line[1]>self.limSup):
			                               		contLines=contLines+1
			                             		aux=line[1]+aux
			                             		cv2.line(img, pt1, pt2, (0,0,255))
	   		         	print 'lineas detectadas: '+ str(contLines)
				self.calculandoNivel=False
				aux=aux/contLines
				level=(((self.limInf-aux)/(self.limInf-self.limSup))*self.dist)+self.ad
				level=round(level,1)
				print level
				levelf=open(self.rutaLevel,'w')
				levelf.write(str(level))		
				levelf.close()	
			except:
				print 'Error tomando foto'


	def run(self):
		hiloP=threading.Thread(target=self.hiloProces, name='Nivel')
		hiloP.setDaemon(True)
		hiloP.start()
		hiloP.join()
		
if __name__ == "__main__":
    	gestorCam().run()

			






				
