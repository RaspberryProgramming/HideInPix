# HideInPix
Method of stegnography by using individual pixel values to hide some data

Install Dependencies

```pip3 install keras```

Run default script

```python3 HideInPix.py```

Example Code using as library
```
from HideInPix import *

encode(b'hello world', 'input.png', 'output.png')

print(decode('output.png').decode())
```

Reading a file to encode

```
from HideInPix import *

file = open("CoolImage.jpg", 'rb') # Make sure you use rb to read in as byte data
data = file.read()
file.close()

encode(data, 'input.png', 'output.png')
```

Decoding and writing to file

```
from HideInPix import *

data = decode('output.png')

file = open('CoolImage.jpg', 'wb')
file.write(data)
file.close()

```
