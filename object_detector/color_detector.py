# # USAGE
# # python color_kmeans.py --image images/jp.png --clusters 3

# # import the necessary packages
# from sklearn.cluster import KMeans
# import matplotlib.pyplot as plt
# import argparse
# import cv2
# import webcolors
# import numpy as np

# def centroid_histogram(clt):
#     # grab the number of different clusters and create a histogram
#     # based on the number of pixels assigned to each cluster
#     numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
#     (hist, _) = np.histogram(clt.labels_, bins = numLabels)

#     # normalize the histogram, such that it sums to one
#     hist = hist.astype("float")
#     hist /= hist.sum()

#     # return the histogram
#     return hist

# def closest_colour(requested_colour):
#     min_colours = {}
#     for key, name in webcolors.css3_hex_to_names.items():
#         r_c, g_c, b_c = webcolors.hex_to_rgb(key)
#         rd = (r_c - requested_colour[0]) ** 2
#         gd = (g_c - requested_colour[1]) ** 2
#         bd = (b_c - requested_colour[2]) ** 2
#         min_colours[(rd + gd + bd)] = name
#     return min_colours[min(min_colours.keys())]

# def get_colour_name(requested_colour):
#     try:
#         closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
#     except ValueError:
#         closest_name = closest_colour(requested_colour)
#         actual_name = None
#     return actual_name, closest_name


# def get_color(image, cluster=5):
#     image = image.reshape((image.shape[0] * image.shape[1], 3))

#     # cluster the pixel intensities
#     clt = KMeans(n_clusters = cluster)
#     clt.fit(image)

#     # build a histogram of clusters and then create a figure
#     # representing the number of pixels labeled to each color
#     hist = centroid_histogram(clt)

#     maximum = 0
#     for (percent, color) in zip(hist, clt.cluster_centers_):
#     	if percent > maximum:
#     			maximum = percent
#     			max_color = color

#     actual_name, closest_name = get_colour_name(tuple(max_color))
#     return closest_name


from PIL import Image

class Colors(object):
    class Color(object):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return "%s : %s" % (self.__class__.__name__, self.value)

    class Red(Color): pass
    class Blue(Color): pass
    class Green(Color): pass
    class Yellow(Color): pass
    class White(Color): pass
    class Gray(Color): pass
    class Black(Color): pass
    class Pink(Color): pass
    class Teal(Color): pass

class ColorWheel(object):
    def __init__(self, rgb):
        r, g, b = rgb

        self.rgb = (Colors.Red(r), Colors.Green(g), Colors.Blue(b), )
    
    def estimate_color(self):
        dominant_colors = self.get_dominant_colors()

        total_colors = len(dominant_colors)
        
        if total_colors == 1:
            return dominant_colors[0]
        elif total_colors == 2:
            color_classes = [x.__class__ for x in dominant_colors]

            if Colors.Red in color_classes and Colors.Green in color_classes:
                return Colors.Yellow(dominant_colors[0].value)
            elif Colors.Red in color_classes and Colors.Blue in color_classes:
                return Colors.Pink(dominant_colors[0].value)
            elif Colors.Blue in color_classes and Colors.Green in color_classes:
                return Colors.Teal(dominant_colors[0].value)
        elif total_colors == 3:
            if dominant_colors[0].value > 200:
                return Colors.White(dominant_colors[0].value)
            elif dominant_colors[0].value > 100:
                return Colors.Gray(dominant_colors[0].value)
            else:
                return Colors.Black(dominant_colors[0].value)
        else:
            print "Dominant Colors : %s" % dominant_colors
    
    def get_dominant_colors(self):
        max_color = max([x.value for x in self.rgb])

        return [x for x in self.rgb if x.value >= max_color * .9]

def process_image(image):
    image_color_quantities = {}

    width, height = image.size

    # for x in range(width):
        # for y in range(height):

    width_margin = int(width - (width * .65))
    height_margin = int(height - (height * .65))
    # print height
    # print range(height_margin, height - height_margin)
    for x in range(width_margin, width - width_margin):
        for y in range(height_margin, height - height_margin):
            r, g, b = image.getpixel((x, y))

            key = "%s:%s:%s" % (r, g, b, )

            key = (r, g, b, )

            image_color_quantities[key] = image_color_quantities.get(key, 0) + 1

    total_assessed_pixels = sum([v for k, v in image_color_quantities.items() if v > 10])

    # strongest_color_wheels = [(ColorWheel(k), v / float(total_pixels) * 100, ) for k, v in test.items() if v > 30]
    strongest_color_wheels = [(ColorWheel(k), v / float(total_assessed_pixels) * 100, ) for k, v in image_color_quantities.items() if v > 10]

    final_colors = {}

    for color_wheel, strength in strongest_color_wheels:
        # print "%s => %s" % (strength, [str(x) for x in color_wheel.get_dominant_colors()], )

        # print "%s => %s" % (strength, color_wheel.estimate_color(), )

        color = color_wheel.estimate_color()

        final_colors[color.__class__] = final_colors.get(color.__class__, 0) + strength

    mStr = 0
    maxCol = None
    for color, strength in final_colors.items():
        if mStr < strength:
            mStr = strength
            maxCol = color
        # print "%s - %s" % (color.__name__, strength, )

    # image.show()
    if maxCol is not None:
        return maxCol.__name__
    else:
        return ''
