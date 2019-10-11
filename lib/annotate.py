
class Image:

    def __init__(self, name):
        self.name = name
        self.annotations = []

    def add(self, annotation):
        self.annotations.append(annotation)

    def dictionary(self):
      return {
        "image" : self.name,
        "annotations" : list(map(Annotation.dictionary, self.annotations))
      }

class Annotation:

    # label - string
    # center - tuple. x and y coordinates for center of annotation
    # size - tuple. width and height for center of annotation
    def __init__(self, label, center, size):
        self.label = label
        self.center = center
        self.size = size

    def dictionary(self):
        return {
            "label" : self.label,
            "coordinates" : {
                "x" : self.center[0],
                "y" : self.center[1],
                "width" : self.size[0],
                "height" : self.size[1]
            }
        }
