def load_image(filename):
    image_data = []
    f = open(filename)
    lines = f.readlines()
    for line in lines:
        if line[0] != "#":
            image_data += line.rstrip('\n').split()
    f.close()
    return image_data

def write_image(filename, image_data):
    f = open(filename, 'w')
    f.write(image_data[0] + '\n')
    f.write(image_data[1] + ' ' + image_data[2] + '\n')
    f.write(image_data[3] + '\n')
    
    for i in range(4, len(image_data)):
        f.write(image_data[i] + ' ')
    f.close()
