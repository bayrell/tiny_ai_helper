# -*- coding: utf-8 -*-

##
# Copyright (с) Ildar Bikmamatov 2022
# License: MIT
##

import math, io, torch, os, re, torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw


def sign(x):
	
	"""
	Sign function
	"""
	
	if x >= 0: return 1
	return -1
	
	
def index_of(arr, item):
	
	"""
	Index of
	"""
	
	try:
		index = arr.index(item)
		return index
	except Exception:
		pass
	
	return -1
	
	
def indexOf(arr, item):
	
	"""
	Index of
	"""
	
	return index_of(arr, item)
	
	
def append_numpy_vector(res, data):
	
	"""
	Append 2 numpy vectors
	"""
	
	if res is None:
		res = np.expand_dims(data, axis=0)
	else:
		res = np.append(res, [data], axis=0)
	
	return res
	
	
def append_tensor_data(obj, data):
	
	"""
	Append data
	"""
	
	if data is not None:
		
		for index, value in enumerate(data):
			
			if torch.is_tensor(value):
				value = value[None, :]
				obj[index] = torch.cat( (obj[index], value) )
				
			elif isinstance(obj[index], list):
				obj[index].append(value)
		
	return obj
	
	
def init_tensorflow_gpu(memory_limit=1024):
	
	"""
	Init tensorflow GPU
	"""
	
	import tensorflow as tf
	gpus = tf.config.list_physical_devices('GPU')
	tf.config.experimental.set_memory_growth(gpus[0], True)
	tf.config.experimental.set_virtual_device_configuration(
	    gpus[0],
	    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=memory_limit)])


def resize_image_canvas(image, size, color=None):
	
	"""
	Resize image canvas
	"""
	
	width, height = size
	
	if color == None:
		pixels = image.load()
		color = pixels[0, 0]
		del pixels
		
	image_new = Image.new(image.mode, (width, height), color = color)
	draw = ImageDraw.Draw(image_new)
	
	position = (
		math.ceil((width - image.size[0]) / 2),
		math.ceil((height - image.size[1]) / 2),
	)
	
	image_new.paste(image, position)
	
	del draw, image
	
	return image_new
	
	
def image_to_tensor(image_bytes, mode=None):
	
	"""
	Convert image to numpy vector
	"""
	
	image = None
	
	try:
		
		if isinstance(image_bytes, bytes):
			image = Image.open(io.BytesIO(image_bytes))
		
		if isinstance(image_bytes, Image.Image):
			image = image_bytes
	
	except Exception:
		image = None
	
	if image is None:
		return None
	
	if mode is not None:
		image = image.convert(mode)
	
	tensor = torch.from_numpy( np.array(image) )
	tensor = tensor.to(torch.uint8)
	
	del image
	
	return tensor
	

def show_image_in_plot(image, cmap=None):
	
	"""
	Plot show image
	"""
	
	if torch.is_tensor(image):
		#image = image * 255.0
		image = image.type(torch.int64)
	
	plt.imshow(image, cmap)
	plt.show()
	

def get_vector_from_answer(count):
	
	"""
	Returns vector from answer\n
		1 -> [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]\n
		5 -> [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
	"""
	
	def f(number):
		res = [0.0] * count
		
		if (number >=0 and number < count):
			res[number] = 1.0
			
		return res
		
	return f


def get_answer_from_vector(vector):
	
	"""
	Returns answer from vector
	"""
	
	value_max = -math.inf
	value_index = 0
	for i in range(0, len(vector)):
		value = vector[i]
		if value_max < value:
			value_index = i
			value_max = value
	
	return value_index
	

def layer(*args, **kwargs):
	
	"""
	Define layer
	"""
	
	obj = {
		"type": "layer",
		"args": args,
		"kwargs": kwargs,
	}
	
	return obj

	
def list_files(path="", recursive=True):
	
	"""
		Returns files in folder
	"""
	
	def read_dir(path, recursive=True):
		res = []
		items = os.listdir(path)
		for item in items:
			
			item_path = os.path.join(path, item)
			
			if item_path == "." or item_path == "..":
				continue
			
			if os.path.isdir(item_path):
				if recursive:
					res = res + read_dir(item_path, recursive)
			else:
				res.append(item_path)
			
		return res
	
	try:
		items = read_dir( path, recursive )
			
		def f(item):
			return item[len(path + "/"):]
		
		items = list( map(f, items) )
	
	except Exception:
		items = []
	
	return items



def list_dirs(path=""):
	
	"""
		Returns dirs in folder
	"""
	
	try:
		items = os.listdir(path)
	except Exception:
		items = []
	return items


def save_bytes(file_name, data):
	
	"""
		Save bytes to file
	"""
	
	file_dir = os.path.dirname(file_name)
	
	if not os.path.isdir(file_dir):
		os.makedirs(file_dir)
	
	f = open(file_name, 'wb')
	f.write(data)
	f.close()
	

def read_bytes(file_name):
	
	"""
		Load bytes from file
	"""
	
	f = open(file_name, 'rb')
	data = f.read()
	f.close()
	
	return data
	
	
def save_file(file_name, data):
	
	"""
		Save file
	"""
	
	bytes = None
	
	if isinstance(data, Image.Image):
		tmp = io.BytesIO()
		data.save(tmp, format='PNG')
		bytes = tmp.getvalue()
	
	if (isinstance(data, str)):
		bytes = data.encode("utf-8")
	
	if bytes is not None:
		save_bytes(file_name, bytes)
	
	pass



def read_file(file_name):
	
	"""
		Read file
	"""
	
	return read_bytes(file_name)
	
	
def get_sort_alphanum_key(name):
	
	"""
	Returns sort alphanum key
	"""
	
	arr = re.split("([0-9]+)", name)
	
	for key, value in enumerate(arr):
		try:
			value = int(value)
		except:
			pass
		arr[key] = value
	
	arr = list(filter(lambda item: item != "", arr))
	
	return arr


def alphanum_sort(files):
	
	"""
	Alphanum sort
	"""
	
	files.sort(key=get_sort_alphanum_key)