# Camera
import picamera2
import time
import RPi.GPIO
import numpy
import PIL

def load_reference_image(file_name):
    pil_image = PIL.Image.open("images/" + file_name)
    if pil_image.mode != '1':
        pil_image = pil_image.convert('1')
    numpy_array = numpy.array(pil_image).astype(numpy.uint8).flatten()
    return numpy_array

def load_reference_images():
    reference_images = [load_reference_image(f"{number}_bw.png") for number in range(10)]
    return reference_images

def extract_digit_array(image_array, offset_x, offset_y):
    numpy_array = numpy.array(image_array)
    digit_array = numpy_array[offset_y:offset_y+84, offset_x:offset_x+46, 0]
    min_value = numpy.min(digit_array)
    max_value = numpy.max(digit_array)
    average_value = (float(min_value) + float(max_value)) / 2
    onebit_array = numpy.where(digit_array < average_value, 0, 1).flatten()
    return onebit_array

def detect_digit_value(digit_array):
    differences = [numpy.sum(digit_array != reference_digit_array) for reference_digit_array in reference_arrays]
    index = numpy.argmin(differences)
    value = differences[index]
    print(index, value, differences)
    # Return only clearly identifiable values
    detected_value = str(index) if value < 1000 else "?"
    return detected_value

def save_array_as_png(array, width, height, file_name):
    # Prüfen, ob die Anzahl der Elemente im Array mit der Bildgröße übereinstimmt
    if len(array) != width * height:
        raise ValueError("Array size does not match specified dimensions (width x height)")
    # Das Array in ein 2D-Array umwandeln, das die Dimensionen (height, width) hat
    array_2d = numpy.array(array).reshape((height, width))
    # Das Array in ein Bild im Modus '1' (1-Bit-Farbtiefe) umwandeln
    image = PIL.Image.fromarray(array_2d)  # 0 -> schwarz, 1 -> weiß
    # Bild als PNG speichern
    image.save(file_name)

# Load reference images
reference_arrays = load_reference_images()

# Define digit positions
digit_positions = [
    [19, 166],
    [109, 166],
    [200, 168],
    [292, 169],
    [388, 169],
    [479, 170],
    [576, 171]
]

# Define GPIO port of the camera LED
camera_led_port = 32

# Initialize camera
camera = picamera2.Picamera2()
camera.start()

# Set LED GPIO to output
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(camera_led_port, RPi.GPIO.OUT, initial=False)

# Switch light on
RPi.GPIO.output(camera_led_port, True)
time.sleep(.5)

# Capture image
image_array = camera.capture_array()
PIL.Image.fromarray(image_array).save("image_array.png")

value = ""
for digit_position in digit_positions:
    digit_array = extract_digit_array(image_array, digit_position[0], digit_position[1])
    # Compare with reference images
    digit_value = detect_digit_value(digit_array)
    value += digit_value
print(value)

# Switch light off
time.sleep(.5)
RPi.GPIO.output(camera_led_port, False)

# Clean up ressources
camera.close()