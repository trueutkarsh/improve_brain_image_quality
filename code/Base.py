# This is the base declaration for general medical image class using nibabel
# and scikit

import os
import urllib
import numpy as np
import nibabel as nib
import pandas as pd


#% Base class features
#%      -> load any type of medical image using nibabel
#%      -> print info about data 
#%      -> print info about usage of functions
#% Image Conventions to follow
#%      -> for 2d patches image is suppose to  be in X Y coordinates and patchZ = 1
#%      ->  

class Base:
	def __init__(self, imgaddr = None, type = 'None', patchFile = None):
		if (imgaddr == None) and (patchFile == None):
			raise ValueError('Neither imgaddr nor patchFile specified')
		elif imgaddr :
			if not os.path.exists(imgaddr):
				raise ValueError('File Does not exists')
			self.imgAddr = imgaddr #address of file
			self.img = None        # image itself. Delete when converted to  
			self.index2patch = {}  # map from index to patch
			self.patchX = None
			self.patchY = None
			self.patchZ = None
			# self.step = None
			self.stepX = None
			self.stepY = None
			self.stepZ = None
			self.fileLoaded = False
			self.patchesFormed = False
			self.count = 0
			self.is2D = False
			self.patchFile = None
			self._loadfile(self.imgAddr)


		elif patchFile :
			if not os.path.exists(patchFile):
				raise ValueError('Patch File Does not exists')
			
			file = pd.read_hdf(patchFile)
			self.imgAddr = file['imgAddr'] #address of file
			self.img = None        # image itself. Delete when converted to  
			self.index2patch = file['patches'][0]  # map from index to patch
			self.patchX = file['patches'][0][0].shape[0]
			self.patchY = file['patches'][0][0].shape[0]
			self.patchZ = file['patches'][0][0].shape[0]
			# self.step = file['step'][0]
			self.stepX = file['stepX'][0]
			self.stepY = file['stepY'][0]
			self.stepZ = file['stepZ'][0]
			self.fileLoaded = False 
			self.patchesFormed = True
			self.count = 0
			self.is2D = False
			self.patchFile = patchFile
			self.patchesFormed = True
			self.imgShape =  file['imgShape']
			file = None

		


	def _loadfile(self, imgaddr, fileextension = None):
		#for switch cases over files extensions over here
		# currently assume nibabel can do everything
		self.img = nib.load(imgaddr).get_data()
		self.imgShape = self.img.shape
		self.fileLoaded = True
		pass
		
	
	def splitimage(self, X = 3, Y = 5, Z = 3):

		self.index2patch = {}
		# change index 2 patch here
		if not self.fileLoaded:
			raise ValueError('Image not Loaded.')

		if (X-1)%2 or (Y-1)%2 or (Z-1)%2 :
			raise ValueError('Patch Dimensions not odd')

		# delete patches if present
		# delete the file too
		# 
		self.patchX = X
		self.patchY = Y
		self.patchZ = Z
		# self.step = step
		# # x y z must be odd
		# stepX  = stepX if stepX else step
		# stepY  = stepY if stepY else step
		# stepZ  = stepZ if stepZ else 
		self.stepX  = X
		self.stepY  = Y
		self.stepZ  = Z

		stepX  = X
		stepY  = Y
		stepZ  = Z


		# now iterate over image to generate patches 
		# check 
		if len( self.img.shape ) == 2: # 2d image
			self.img = np.reshape(self.img, (self.imgSize[0], self.imgSize[1], 1))
			self.is2D = True
			
		i = 0
		x = X/2
		y = Y/2
		z = Z/2

		#find pad in each direction
		padX = (stepX -(self.img.shape[0])%stepX) if (self.img.shape[0])%stepX else 0
		padY = (stepY -(self.img.shape[1])%stepY) if (self.img.shape[1])%stepY else 0
		padZ = (stepZ -(self.img.shape[2])%stepZ) if (self.img.shape[2])%stepZ else 0

		# zero padding         
		self.img = np.concatenate((self.img, np.zeros(( padX, self.img.shape[1], self.img.shape[2]) ) ), axis=0)
		self.img = np.concatenate((self.img, np.zeros(( self.img.shape[0], padY, self.img.shape[2]) ) ), axis=1)
		self.img = np.concatenate((self.img, np.zeros(( self.img.shape[0], self.img.shape[1], padZ) ) ), axis=2)

		imgShape = self.getImgShape()
		for x in range(X/2, imgShape[0] - X/2 , stepX):
			for y in range(Y/2, imgShape[1] - Y/2 , stepY):
				for z in range(Z/2, imgShape[2] - Z/2, stepZ):
					self.index2patch[i] = self.img[x - X/2: x + X/2 + 1 , y - Y/2: y + Y/2 + 1, z - Z/2: z + Z/2  + 1]
					i = i + 1

		self.patchesFormed = True
		self.count = i


	def getInfo(self):
		pass
		#send info about data here

	def getImgShape(self):
		if self.fileLoaded:
			return self.img.shape
		else:
			return self.imgShape

	def _savepatches(self, Filename = None):
		if not Filename:
			fileName = imgaddr[imgaddr.rfind('/'):] + "_patches.h5"
		else:
			fileName = Filename

		if self.patchesFormed :
			ptch = {}
			ptch['imgAddr'] = [self.imgAddr]
			ptch['imgShape'] = [self.getImgShape()]
			ptch['patches'] = [self.index2patch]
			#ptch['step'] = [self.step]
			ptch['stepX'] = [self.stepX]
			ptch['stepY'] = [self.stepY]
			ptch['stepZ'] = [self.stepZ]
			df = pd.DataFrame(ptch)
			df.to_hdf(fileName, 'patches', overwrite = True)
			self.patchFile = fileName
			# save them to hdf5 file 

	def patches_to_image(self):
		# convert to image blocks
		if self.patchesFormed:
			imgShape = self.getImgShape()
			# print("imgShape", imgShape)
			X = imgShape[0]/self.patchX
			Y = imgShape[1]/self.patchY	
			Z = imgShape[2]/self.patchZ
			i = 0
			tCub = np.zeros((0, imgShape[1], imgShape[2]))
			
			for x in range(X):
				tPln = np.zeros((self.patchX, 0, imgShape[2]))
				for y in range(Y):
					tCol = np.zeros((self.patchX, self.patchY, 0))
					for z in range(Z):
						tCol = np.concatenate((tCol, self.index2patch[i]), axis = 2)
						i = i+1
					tPln = np.concatenate((tPln, tCol), axis=1)
				# print("tPln",tPln.shape)
				tCub = np.concatenate((tCub, tPln), axis=0)
			
			self.img = tCub
		else:
			print("No patches formed")

	
	


# test the class here

if __name__ == '__main__':
	trainx = Base(imgaddr = "../data/train/t1_icbm_normal_1mm_pn5_rf0.mnc.gz") 
	sindex = 50 # starting images are just 
	trainx.img = trainx.img[:, :, sindex: sindex + 5][:, :, ::2]
	x = 31
	y = 31
	z = 1
	Step = 31
	trainx.splitimage(X = x, Y = y, Z = z)
	trainx.patches_to_image()

