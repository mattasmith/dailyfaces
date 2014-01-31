''' Compress images '''

from PIL import Image


def resizeImage(image_file):
	# get the image's width and height in pixels
	img = Image.open(image_file)
	width, height = img.size

	# get the largest dimension
	max_dim = max(img.size)

	
	# resize the image using the largest side as dimension
	factor = 0.7
	side = int(max_dim*factor)
	resized_image = img.resize((side, side), Image.ANTIALIAS)

	# save the resized image to a file
	# overwrite existing file
	resized_image_file = image_file
	#resized_image.save(resized_image_file)
	#
	#print("%s resized" % resized_image_file)
	print width, height

# pick an image file you have in the working directory
# (or give full path name)
image_file = "static/images/download/13.jpg"

resizeImage(image_file)