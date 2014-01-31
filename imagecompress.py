''' Compress images '''

from PIL import Image


def resizeImage(image_file):
	# get the image's width and height in pixels
	with Image.open(image_file) as img:
		width, height = img.size

		# get the largest dimension
		max_dim = max(img.size)

		if max_dim > 1000:
		# resize the image using the largest side as dimension
			factor = 1000./max_dim
			new_width = int(width*factor)
			new_height = int(height*factor)
			resized_image = img.resize((new_width, new_height), Image.ANTIALIAS)
			print width, height, new_width, new_height

			# save the resized image to a file
			# overwrite existing file
			resized_image_file = image_file
			resized_image.save(resized_image_file)
			#
			print("%s resized" % resized_image_file)
	

# pick an image file you have in the working directory
# (or give full path name)
for i in range(13):
	image_file = "static/images/download/%d.jpg" %(i+1)
	resizeImage(image_file)