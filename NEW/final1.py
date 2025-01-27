from PIL import Image
import numpy as np
from sewar.full_ref import mse, psnr, ssim, uqi, ergas
import cv2

step = 5

def get_bit_position(x, y, step):
    """Hash function to determine which bit to use in each pixel"""
    return (x + y) % step

def calculate_metrics(original_img_path, encoded_img_path):
    """Calculate various image quality metrics using SEWAR"""
    # Read images
    original = cv2.imread(original_img_path)
    encoded = cv2.imread(encoded_img_path)
    
    # Calculate metrics using SEWAR
    mse_value = mse(original, encoded)
    psnr_value = psnr(original, encoded)
    ssim_value = ssim(original, encoded)[0]  # SSIM returns a tuple, we take first value
    uqi_value = uqi(original, encoded)  # Universal Quality Index
    ergas_value = ergas(original, encoded)  # Relative dimensionless global error
    
    # Calculate IF (Image Fidelity)
    if_score = 1 - (mse_value / np.mean(original.astype(float) ** 2))
    
    return {
        'MSE': mse_value,
        'PSNR': psnr_value,
        'SSIM': ssim_value,
        'IF': if_score,
        'UQI': uqi_value,
        'ERGAS': ergas_value
    }

def encode_message(image_path, message, output_path, step):
    """Encode message and calculate quality metrics"""
    # Store original image for comparison
    original_img = Image.open(image_path)
    
    if original_img.mode != 'RGB':
        original_img = original_img.convert('RGB')
    
    img = original_img.copy()
    
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
            bit_pos = get_bit_position(x, y, step)
            
            for n in range(3):
                if data_index < len(binary_message):
                    pixel[n] = pixel[n] & ~(1 << bit_pos)
                    pixel[n] = pixel[n] | (int(binary_message[data_index]) << bit_pos)
                    data_index += 1
            
            img.putpixel((x, y), tuple(pixel))
            
        if data_index >= len(binary_message):
            break
    
    img.save(output_path)
    
    # Calculate and return quality metrics
    metrics = calculate_metrics(image_path, output_path)
    return metrics

def decode_message(image_path, step):
    """Decode message from image"""
    img = Image.open(image_path)
    binary_message = ""
    
    for x in range(img.width):
        for y in range(img.height):
            pixel = img.getpixel((x, y))
            bit_pos = get_bit_position(x, y, step)
            
            for n in range(3):
                binary_message += str((pixel[n] >> bit_pos) & 1)
            
            if binary_message[-8:] == '00000000':
                break
        if binary_message[-8:] == '00000000':
            break
    
    message = ""
    for i in range(0, len(binary_message)-8, 8):
        message += chr(int(binary_message[i:i+8], 2))
    
    return message.split('\x00')[0]

def print_metrics(metrics):
    """Print all metrics in a formatted way"""
    print("\nImage Quality Metrics:")
    print(f"Mean Squared Error (MSE): {metrics['MSE']:.4f}")
    print(f"Peak Signal-to-Noise Ratio (PSNR): {metrics['PSNR']:.2f} dB")
    print(f"Structural Similarity Index (SSIM): {metrics['SSIM']:.4f}")
    print(f"Image Fidelity (IF): {metrics['IF']:.4f}")
    print(f"Universal Quality Index (UQI): {metrics['UQI']:.4f}")
    print(f"ERGAS: {metrics['ERGAS']:.4f}")

# Enhanced user interface
while True:
    print("\nAdvanced Image Steganography Menu:")
    print("1. Encrypt")
    print("2. Decrypt")
    print("3. Calculate Image Quality Metrics")
    print("4. Exit")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        image_path = input("Enter the path of the image: ")
        message = input("Enter the hidden message: ")
        output_path = input("Enter the path to save the image: ")
        try:
            metrics = encode_message(image_path, message, output_path, step)
            print("\nMessage encrypted successfully!")
            print(f"To decrypt, use the step value: {step}")
            print_metrics(metrics)
        except Exception as e:
            print(f"Error during encryption: {str(e)}")
            
    elif choice == "2":
        image_path = input("Enter the path of the image which you want to decrypt: ")
        try:
            decoded = decode_message(image_path, step)
            print("Decoded Message is:", decoded)
        except Exception as e:
            print(f"Error during decryption: {str(e)}")
            
    elif choice == "3":
        original_path = input("Enter the path of the original image: ")
        encoded_path = input("Enter the path of the encoded image: ")
        try:
            metrics = calculate_metrics(original_path, encoded_path)
            print_metrics(metrics)
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            
    elif choice == "4":
        print("Exiting program...")
        break
        
    else:
        print("Invalid choice! Please enter 1, 2, 3, or 4.")