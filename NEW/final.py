from PIL import Image
import numpy as np
import cv2

step = 8

def get_bit_position(x, y, step):
    bit1 = (x + y) % step  
    bit2 = bit1+1
    
    return bit1, bit2

def ssim_manual(img1, img2):
    C1 = 6.5025
    C2 = 58.5225

    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)

    kernel = np.ones((3, 3), np.float64) / 9
    mu1 = cv2.filter2D(img1, -1, kernel)
    mu2 = cv2.filter2D(img2, -1, kernel)

    mu1_sq = mu1 ** 2
    mu2_sq = mu2 ** 2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = cv2.filter2D(img1 ** 2, -1, kernel) - mu1_sq
    sigma2_sq = cv2.filter2D(img2 ** 2, -1, kernel) - mu2_sq
    sigma12 = cv2.filter2D(img1 * img2, -1, kernel) - mu1_mu2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    return ssim_map.mean()

def calculate_metrics(original_img_path, encoded_img_path):

    original = cv2.imread(original_img_path, cv2.IMREAD_GRAYSCALE)
    encoded = cv2.imread(encoded_img_path, cv2.IMREAD_GRAYSCALE)

    mse = np.mean((original - encoded) ** 2)

    if_score = 1 - (mse / np.mean(original ** 2))

    max_pixel = 255.0
    if mse == 0:
        psnr = float('inf')
    else:
        psnr = 20 * np.log10(max_pixel) - 10 * np.log10(mse)

    ssim_score = ssim_manual(original, encoded)

    return {
        'MSE': mse,
        'IF': if_score,
        'PSNR': psnr,
        'SSIM': ssim_score
    }


def encode_message(image_path, message, output_path, step):
    
    original_img = Image.open(image_path)

    if original_img.mode != 'RGB':
        original_img = original_img.convert('RGB')

    img = original_img.copy()

    binary_message = ''.join(format(ord(char), '08b') for char in message)
    binary_message += '00000000'  # End delimiter

    data_index = 0

    for x in range(img.width):
        for y in range(img.height):
            if data_index >= len(binary_message):
                break

            pixel = list(img.getpixel((x, y)))
            bit_pos1, bit_pos2 = get_bit_position(x, y, step)

            for n in range(3):  # Iterate over R, G, B channels
                if data_index < len(binary_message) - 1:
                    pixel[n] = pixel[n] & ~(1 << bit_pos1)  # Clear bit_pos1
                    pixel[n] |= (int(binary_message[data_index]) << bit_pos1)  # Set bit_pos1
                    data_index += 1

                    pixel[n] = pixel[n] & ~(1 << bit_pos2)  # Clear bit_pos2
                    pixel[n] |= (int(binary_message[data_index]) << bit_pos2)  # Set bit_pos2
                    data_index += 1

            img.putpixel((x, y), tuple(pixel))

        if data_index >= len(binary_message):
            break

    img.save(output_path)

    # Calculate and return quality metrics
    metrics = calculate_metrics(image_path, output_path)
    return metrics



def decode_message(image_path, step):
    """Decodes a hidden message from an image."""
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
    for i in range(0, len(binary_message) - 8, 8):
        message += chr(int(binary_message[i:i + 8], 2))

    return message.split('\x00')[0]


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
            print("\nImage Quality Metrics:")
            print(f"MSE: {metrics['MSE']:.4f}")
            print(f"Image Fidelity (IF): {metrics['IF']:.4f}")
            print(f"PSNR: {metrics['PSNR']:.2f} dB")
            print(f"SSIM: {metrics['SSIM']:.4f}")
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
            print("\nImage Quality Metrics:")
            print(f"MSE: {metrics['MSE']:.4f}")
            print(f"Image Fidelity (IF): {metrics['IF']:.4f}")
            print(f"PSNR: {metrics['PSNR']:.2f} dB")
            print(f"SSIM: {metrics['SSIM']:.4f}")
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")

    elif choice == "4":
        print("Exiting program...")
        break

    else:
        print("Invalid choice! Please enter 1, 2, 3, or 4.")
