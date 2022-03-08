from keras.preprocessing.image import load_img, save_img, img_to_array, array_to_img
import argparse
from math import sqrt

def byte2bin(data):
    """
    byte2bin: Converts python byte data to a string of binary 1s and 0s

    Takes:
        data: the byte data that we'll convert
    
    Returns:
        string of binary 1s and 0s
    """
    out = ""
    for byte in data:
        out += f'{byte:0>8b}'
    return out

def bin2byte(data):
    """
    bin2byte: Converts a string of 1s and 0s to python byte data

    Takes:
        data: string of1s and 0s
    
    Returns:
        python byte data 
    """

    v = int(data, 2)
    b = bytearray()

    while v:
        b.append(v & 0xff)
        v >>= 8
    
    return bytes(b[::-1])

def encode(data, input_path, output_path="output.png", bit_size=1):
    """
    encode:
        Encode some data into an image. encode converts some byte data to be inserted into an image.
        png files are favored as they use lossless compression. Lossy compression may remove some encoded data.
    
    
    Takes:
        data: the byte data that is to be inserted into the input image
        input_path: path to the input image
        output_path: path for where to write output image file. default to output.png and should stay as a png as it uses lossless compression
        bit_size: number of pixels that each bit should take up. This can only be a square (we need to square root this number) Default: 1

    Writes:
        image to output_path

    """
    img = load_img(input_path) # Load input image data

    data = byte2bin(data)

    size = str(len(data)).rjust(64, '0').encode() # Format size of data and convert to byte data
    
    size = byte2bin(size) # Convert to binary

    # TODO: Implement options to function as a way to store information such as compression used before insertion

    options = "None Right Now Bucko".ljust(64, ' ').encode() # format options and convert to byte data

    options = byte2bin(options) # Convert to binary

    data = size + options + data # Combine data with head info

    data = list(data) # Convert to list to make increase encoding speed
                      # Using a list to access each item was faster than using a string

    bit_size = int(sqrt(bit_size))

    imdata = img_to_array(img) # convert image to np array

    print("")
    d = 0 # Control variabe for the data array
    datalen = len(data) # Used to determine progress and stores length of data

    # break wasn't working so using try was necessary
    try:
        # Iterate through entirety of the image data
        for i in range(0,len(imdata), bit_size):
            # Print the progress
            print("\r", 100*(d/datalen), "% left", end="")

            for j in range(0, len(imdata[i]), bit_size):

                # If we have more data to insert to the image
                if d < datalen:
                    
                    # Check if current color in our pixel is even/odd
                    imdata = oddify_group((i, j), (bit_size, bit_size), data[d], imdata)

                    # Increment d
                    d += 1

                else:
                    # Finished inserting data to image
                    raise StopIteration
    except StopIteration:
        pass

    print("")

    img_pil = array_to_img(imdata) # Convert back to image

    save_img(output_path, img_pil, quality=100, optimize=False, progressive=False) # Save output to output_path

def decode(input_path, bit_size=1):
    """
    decode: decodes data inserted into image

    Takes:
        input_path: path to file with inserted data
        bit_size: number of pixels that each bit should take up. This can only be a square (we need to square root this number) Default: 1
    
    Returns:
        Byte data containing data that was encoded within input image file.
    """

    img = load_img(input_path) # Read image file

    imdata = img_to_array(img) # Convert to numpy array

    header = imread(imdata, 1024, bit_size)# header data

    # Read first half of header which is the size
    size = int(bin2byte(header[:512])) # Extract data size from header section

    options = bin2byte(header[512:]).decode() # Extract options from header section
    # TODO: Implement options to function as a way to store information such as compression used before insertion

    print("Options: ", options)

    outsize = 1024+size # Used to keep track of how big the output should be

    output = imread(imdata, outsize, bit_size) # Reset output
    
    # Skipping the header, read the data from our output
    output = bin2byte(output[1024:])

    return output

def imread(imdata, length, bit_size=1):
    """
    imread: read binary from image

    Takes:
        imdata: numpy array containing image data
        length: length of the data we're reading
    """

    bit_size = int(sqrt(bit_size))

    output = ""

    try:
        for i in range(0, len(imdata), bit_size):
            for j in range(0, len(imdata[i]), bit_size):

                # get remainder of k/2 and convert to int->str
                output += str(int(imdata[i][j][0]%2))

                if len(output) >= length: # Only read first 1024 bits since this is the header
                    raise StopIteration
    except StopIteration:
        pass
    

    return output

def oddify_group(start, dim, val, data):
    """
    oddify_group: change group value based on start pos and dimensions
    
    start: start position in data
    dim: dimensions to change
    val: value (1 or 0) used for truth in oddify
    data: data to modify
    """

    for i in range(start[0], start[0]+dim[0]):
        for j in range(start[1], start[1]+dim[1]):
            
            for k in range(len(data[0][0])):
                
                data[i][j][k] = oddify(data[i][j][k], val)

    return data

def oddify(val, truth="0"):
    """
    oddify: makes a number odd if truth is 1

    truth: used to determine if this value should be odd or not, 
           using binary to represent truth. This value is also taken as a string.
    """

    odd = val % 2 == 1
                    
    # If Odd and data is 0, make data even
    if odd and truth == "0":
        return val - 1
        
    
    # If NOT Odd and data is 1, make data odd
    elif not odd and truth == "1":
        if val == "0":
            return val + 1
        else:
            return val - 1

    return val


def main():
    parser = argparse.ArgumentParser(description='Program for hiding binary data within images.')

    parser.add_argument('-e', '--encode', help='Encode Data into an image')
    parser.add_argument('-d', '--decode', help='Decode Data from an image')
    parser.add_argument('-t', '--text', help='Text input that will be used to encode')
    parser.add_argument('-f', '--file', help='File input that will be used to encode or decode')
    parser.add_argument('-bs', '--bit_size', help="""Number of pixels each bit will take up. This can be used to help obfuscate the data.
                                                     This will result in increased compute time and decreased usable space. Also, this must
                                                     be a squared number.""")
    parser.add_argument('-of', '--outputfile', help="""The filename used as output. If encoding, the file will be the image with encoded data,
                                                       if decoding the file will store the output of the decoding process""")

    args = parser.parse_args()

    if args.bit_size:
        bit_size = args.bit_size
    else:
        bit_size = 1

    if args.encode:
        if args.text:
            
            # Store text from parameter
            data = args.text.encode()

        elif args.file:
            
            # Read file
            f = open(args.file, 'rb')
            data = f.read()
            f.close()

        else:

            # Some parameter is necessary to encode
            print('[!] Please use --text or --file argument to pass input')
            parser.print_help()
            return None

        # Encode data into file
        encode(data, args.encode, args.outputfile)

    elif args.decode:

        data = decode(args.decode, bit_size=bit_size) # Decode the data

        if args.outputfile:
            # Write data to file

            f = open(args.outputfile, 'wb')
            
            f.write(data)
            
            f.close()
        else:
            # Print output of decode
            print(data)

    else:
        parser.print_help()

if __name__ in '__main__':
    main()
