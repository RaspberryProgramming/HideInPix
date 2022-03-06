from keras.preprocessing.image import load_img, save_img, img_to_array, array_to_img
import argparse

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

def encode(data, input_path, output_path="output.png"):
    """
    encode:
        Encode some data into an image. encode converts some byte data to be inserted into an image.
        png files are favored as they use lossless compression. Lossy compression may remove some encoded data.
    
    
    Takes:
        data: the byte data that is to be inserted into the input image
        input_path: path to the input image
        output_path: path for where to write output image file. default to output.png and should stay as a png as it uses lossless compression

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

    imdata = img_to_array(img) # convert image to np array

    print("")
    d = 0 # Control variabe for the data array
    datalen = len(data) # Used to determine progress and stores length of data

    # break wasn't working so using try was necessary
    try:
        # Iterate through entirety of the image data
        for i in range(len(imdata)):
            for j in range(len(imdata[i])):
                # Print Progress each pixel of image
                print("\r", 100*(d/datalen), "% left", end="")
                for k in range(len(imdata[i][j])):
                    # If we have more data to insert to the image
                    if d < datalen:

                        # Check if current color in our pixel is even/odd
                        tmpdat = imdata[i][j][k]
                        odd = tmpdat % 2 == 1
                        
                        # If Odd and data is 0, make data even
                        if odd and data[d] == "0":
                            imdata[i][j][k] = tmpdat - 1
                        
                        # If NOT Odd and data is 1, make data odd
                        elif not odd and data[d] == "1":                        
                            if tmpdat == 0:
                                imdata[i][j][k] = tmpdat + 1
                            else:
                                imdata[i][j][k] = tmpdat - 1

                        # Increment d
                        d += 1

                    else:
                        # Finished inserting data to image
                        raise StopIteration
    except StopIteration:
        pass

    print("")

    img_pil = array_to_img(imdata) # Convert back to image

    save_img(output_path, img_pil) # Save output to output_path

def decode(input_path):
    """
    decode: decodes data inserted into image

    Takes:
        input_path: path to file with inserted data
    
    Returns:
        Byte data containing data that was encoded within input image file.
    """

    img = load_img(input_path) # Read image file

    imdata = img_to_array(img) # Convert to numpy array

    header = imread(imdata, 1024)# header data

    # Read first half of header which is the size
    size = int(bin2byte(header[:512])) # Extract data size from header section

    options = bin2byte(header[512:]).decode() # Extract options from header section
    # TODO: Implement options to function as a way to store information such as compression used before insertion

    print("Options: ", options)

    outsize = 1024+size # Used to keep track of how big the output should be

    output = imread(imdata, outsize) # Reset output
    
    # Skipping the header, read the data from our output
    output = bin2byte(output[1024:])

    return output

def imread(imdata, length):
    """
    imread: read binary from image

    Takes:
        imdata: numpy array containing image data
        length: length of the data we're reading
    """

    output = ""

    try:
        for i in imdata:
            for j in i:
                for k in j:

                    # get remainder of k/2 and convert to int->str
                    output += str(int(k%2))

                    if len(output) >= length: # Only read first 1024 bits since this is the header
                        raise StopIteration
    except StopIteration:
        pass

    return output


def main():
    parser = argparse.ArgumentParser(description='Program for hiding binary data within images.')

    parser.add_argument('-e', '--encode', help='Encode Data into an image')
    parser.add_argument('-d', '--decode', help='Decode Data from an image')
    parser.add_argument('-t', '--text', help='Text input that will be used to encode')
    parser.add_argument('-f', '--file', help='File input that will be used to encode or decode')
    parser.add_argument('-of', '--outputfile', help='The filename used as output. If encoding, the file will be the image with encoded data, if decoding the file will store the output of the decoding process')

    args = parser.parse_args()

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
            args.print_help()
            return None

        # Encode data into file
        encode(data, args.encode, args.outputfile)

    elif args.decode:
        if args.file:
            filename = args.file
        else:
            # File must be passed when decoding
            print("Please pass --file parameter")
            args.print_help()
            return None
            
        data = decode(filename) # Decode the data

        if args.outputfile:
            # Write data to file

            f = open(args.outfile, 'wb')
            
            f.write(data)
            
            f.close()
        else:
            # Print output of decode
            print(data)

    else:
        args.print_help()

if __name__ in '__main__':
    main()
