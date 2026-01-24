import numpy as np
import png

image = np.ones([200, 300])
image *= 255

png.from_array(image.astype(np.int8), mode='L;8').save('image.png')
