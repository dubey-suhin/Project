from PIL import Image

def next_valid_pixel(width, height, current_x, current_y, step):
    while True:
        if (current_x + current_y) % step == 0:
            return current_x, current_y
        current_x += 1
        if current_x >= width:
            current_x = 0
            current_y += 1
        if current_y >= height:
            return 0, 0  # Start over if we reach the end of the image

def encode_message(image_path, message, output_path, step=3):
    img = Image.open(image_path).convert('RGB')
    width, height = img.size

    binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'  # Add delimiter
    data_index = 0
    current_x, current_y = 0, 0

    while data_index < len(binary_message):
        current_x, current_y = next_valid_pixel(width, height, current_x, current_y, step)
        pixel = list(img.getpixel((current_x, current_y)))

        for n in range(3):
            if data_index < len(binary_message):
                pixel[n] = (pixel[n] & ~1) | int(binary_message[data_index])
                data_index += 1

        img.putpixel((current_x, current_y), tuple(pixel))
        print(f"Message part stored in ({current_x},{current_y})")

        current_x += 1
        if current_x >= width:
            current_x = 0
            current_y += 1

    img.save(output_path)

def decode_message(image_path, step=3):
    img = Image.open(image_path)
    width, height = img.size
    binary_message = ""
    current_x, current_y = 0, 0

    while True:
        current_x, current_y = next_valid_pixel(width, height, current_x, current_y, step)
        pixel = img.getpixel((current_x, current_y))

        for n in range(3):
            binary_message += str(pixel[n] & 1)

        if binary_message[-8:] == '00000000':
            break

        current_x += 1
        if current_x >= width:
            current_x = 0
            current_y += 1

    message = ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message)-8, 8))
    return message.split('\x00')[0]  # Remove any null characters

# Example usage
choice = input("Enter what do you want to do (Encrypt/Decrypt): ").lower()
if choice == "encrypt":
    image_path = input("Enter the path of the image: ")
    message = input("Enter the hidden message: ")
    output_path = input("Enter the path to save the image: ")
    encode_message(image_path, message, output_path)
    print("Message encrypted successfully!")
elif choice == "decrypt":
    image_path = input("Enter the path of the image which you want to decrypt: ")
    decoded = decode_message(image_path)
    print("Decoded Message is:", decoded)
else:
    print("Please give a correct input (Encrypt/Decrypt).\nEXIT...")