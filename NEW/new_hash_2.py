from PIL import Image
step =5
def get_bit_position(x, y, step):
    """Hash function to determine which bit to use in each pixel"""
    return (x + y) % step

def encode_message(image_path, message, output_path, step):
    img = Image.open(image_path)
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert the message to binary
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    binary_message += '00000000'  # delimiter

    data_index = 0
    # Iterate through each pixel
    for x in range(img.width):
        for y in range(img.height):
            if data_index >= len(binary_message):
                break
                
            pixel = list(img.getpixel((x, y)))
            bit_pos = get_bit_position(x, y, step)  # Get the bit position to modify
            
            # Modify the specified bit of each color channel
            for n in range(3):
                if data_index < len(binary_message):
                    # Clear the bit at bit_pos
                    pixel[n] = pixel[n] & ~(1 << bit_pos)
                    # Set the bit at bit_pos to the message bit
                    pixel[n] = pixel[n] | (int(binary_message[data_index]) << bit_pos)
                    data_index += 1
            
            # Put modified pixel back in the image
            img.putpixel((x, y), tuple(pixel))
            # print(f"Message part stored in pixel ({x},{y}) at bit position {bit_pos}")
            
        if data_index >= len(binary_message):
            break
    
    img.save(output_path)
    # print(f"Encoding completed successfully! Used bit positions up to {step-1}")

def decode_message(image_path, step):
    img = Image.open(image_path)
    binary_message = ""
    
    for x in range(img.width):
        for y in range(img.height):
            pixel = img.getpixel((x, y))
            bit_pos = get_bit_position(x, y, step)  # Get the bit position to read
            
            # Extract the specified bit from each color channel
            for n in range(3):
                binary_message += str((pixel[n] >> bit_pos) & 1)
            
            # Check for delimiter
            if binary_message[-8:] == '00000000':
                break
        if binary_message[-8:] == '00000000':
            break
    
    # Convert binary to ASCII
    message = ""
    for i in range(0, len(binary_message)-8, 8):
        message += chr(int(binary_message[i:i+8], 2))
    
    return message.split('\x00')[0]  # Remove any null characters

# User interface
while True:
    print("\nAdvanced Image Steganography Menu:")
    print("1. Encrypt")
    print("2. Decrypt")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        image_path = input("Enter the path of the image: ")
        message = input("Enter the hidden message: ")
        output_path = input("Enter the path to save the image: ")
        # step = int(input("Enter step value (1-8) "))
        try:
            encode_message(image_path, message, output_path, step)
            print("Message encrypted successfully!")
            print(f"To decrypt, use the step value: {step}")
        except Exception as e:
            print(f"Error during encryption: {str(e)}")
            
    elif choice == "2":
        image_path = input("Enter the path of the image which you want to decrypt: ")
        # step = int(input("Enter the step value used during encryption: "))
        try:
            decoded = decode_message(image_path, step)
            print("Decoded Message is:", decoded)
        except Exception as e:
            print(f"Error during decryption: {str(e)}")
            
    elif choice == "3":
        print("Exiting program...")
        break
        
    else:
        print("Invalid choice! Please enter 1, 2, or 3.")
        
        
        
    