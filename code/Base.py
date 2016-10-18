# This is the base declaration for general medical image class using nibabel
# and scikit

import os
import urllib
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from scipy.misc import imread
from matplotlib.pyplot import imshow
import pandas as pd

#% Base class features
#%      -> load any type of medical image using nibabel
#%      -> print info about data 
#%      -> print info about usage of functions
#%      -> split data into patches
#%      -> load patch file
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
			self.step = None
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
			self.step = None
			self.fileLoaded = False 
			self.patchesFormed = True
			self.count = 0
			self.is2D = False
			self.patchFile = patchFile
			self.patchesFormed = True
			self.imgShape =  file['imgShape']

		


	def _loadfile(self, imgaddr, fileextension = None):
		#for switch cases over files extensions over here
		# currently assume nibabel can do everything
		self.img = nib.load(imgaddr).get_data()
		self.imgShape = self.img.shape
		self.fileLoaded = True
		pass
		
	
	def splitimage(self, X = 3, Y = 5, Z = 3, step = 1):

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
		self.step = step
		# x y z must be odd

		# now iterate over image to generate patches 
		# check 
		if len( self.img.shape ) == 2: # 2d image
			self.img = np.reshape(self.img, (self.imgSize[0], self.imgSize[1], 1))
			self.is2D = True
			
		i = 0
		x = X/2
		y = Y/2
		z = Z/2

		# zero padding         
		self.img = np.concatenate((self.img, np.zeros(( (self.img.shape[0] - X)%step, self.img.shape[1], self.img.shape[2]) ) ), axis=0)
		self.img = np.concatenate((self.img, np.zeros(( self.img.shape[0], (self.img.shape[1] - Y)%step, self.img.shape[2]) ) ), axis=1)
		self.img = np.concatenate((self.img, np.zeros(( self.img.shape[0], self.img.shape[1], (self.img.shape[2] -Z)%step ) ) ), axis=2)

		imgShape = self.img.shape
		for x in range(X/2, imgShape[0] - X/2 , step):
			for y in range(Y/2, imgShape[1] - Y/2 , step):
				for z in range(Z/2, imgShape[2] - Z/2, step ):
					self.index2patch[i] = self.img[x - X/2: x + X/2 + 1, y - Y/2: y + Y/2 + 1, z - Z/2: z + Z/2 + 1]
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
			df = pd.DataFrame(ptch)
			df.to_hdf(fileName, 'patches', overwrite = True)
			self.patchFile = fileName
			# save them to hdf5 file 

	def patches_to_image(self):
		if patchesFormed:
			pass
		else:
			print("No patches formed")

	
	


