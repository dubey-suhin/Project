from PIL import Image


def encode_message(image_path, message, output_path):
    img = Image.open(image_path)
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert the message to binary
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    binary_message += '00000000'

    data_index = 0
    # Iterate through each pixel
    for x in range(img.width):
        for y in range(img.height):
            pixel = list(img.getpixel((x, y)))
            
            # Modify the least significant bit of each color channel
            for n in range(3):
                if data_index < len(binary_message):
                    pixel[n] = pixel[n] & ~1 | int(binary_message[data_index])
                    data_index += 1
            
            # Put modified pixel back in the image
            img.putpixel((x, y), tuple(pixel))
            
            if data_index >= len(binary_message):
                break
        if data_index >= len(binary_message):
            break
    
   
    img.save(output_path)

def decode_message(image_path):
    img = Image.open(image_path)
    binary_message = ""
    
    
    for x in range(img.width):
        for y in range(img.height):
            pixel = img.getpixel((x, y))
            
            for n in range(3):
                binary_message += str(pixel[n] & 1)
            
            if binary_message[-8:] == '00000000':
                break
        if binary_message[-8:] == '00000000':
            break
    
    # Convert binary to ASCII
    message = ""
    for i in range(0, len(binary_message)-8, 8):
        message += chr(int(binary_message[i:i+8], 2))
    
    return message.split('\x00')[0]  # Remove any null characters


choice = input("Enter what d o you want to do (Encrypt/Decrypt): ")
if choice == "Encrypt":
    image_path = input("Enter the path of the image: ")
    message = input("Enter the hidden message: ")
    output_path = input("Enter the path to save the image: ")
    encode_message(image_path, message, output_path)

elif choice == "Decrypt":
    image_path = input("Enter the path of the image which you want to decrypt: ")
    decoded = decode_message(image_path)
    print("Decoded Message is: ", decoded)

else:
    print("Please give a correct input...\nEXIT...")
# image_path = input("Enter image path: ")
# message = input("Enter your hidden Message: ")
# output_path = input("Enter output path: ")
# # Example usage
# encode_message(image_path, message  , output_path)
# # decoded_message = decode_message('output_image.png')
# # print("Decoded message:", decoded_message)
