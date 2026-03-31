import os
from abc import ABC, abstractmethod

class GenericFile(ABC):
    @abstractmethod
    def get_path(self):
        pass
    @abstractmethod
    def get_freq(self):
        pass


class TextASCII(GenericFile):
    def __init__(self, path):
        self.path = path
        self.freq = [0] * 256
    def get_path(self):
        return f"{self.path}"
    def get_freq(self):
        return f"{self.freq}"


class TextUNICODE(GenericFile):
    def __init__(self, path):
        self.path = path
        self.freq = [0] * 256
    def get_path(self):
        return f"{self.path}"
    def get_freq(self):
        return f"{self.freq}"


class Binary(GenericFile):
    def __init__(self, path):
        self.path = path
        self.freq = [0] * 256
    def get_path(self):
        return f"{self.path}"
    def get_freq(self):
        return f"{self.freq}"

class XMLFile(TextASCII):
    def __init__(self, path):
        super().__init__(path)
        self.first_tag = None

    def extract_tag(self, content):
        try:
            text = content.decode('ascii', errors='ignore')
            start = text.find('<')
            end = text.find('>')
            if start != -1 and end != -1:
                self.first_tag = text[start:end+1]
        except:
            pass

    def get_path(self):
        return f"{self.path}"
    def get_freq(self):
        return f"{self.freq}"


class BMP(Binary):
    def __init__(self, path):
        super().__init__(path)
        self.width = None
        self.height = None
        self.bpp = None

    def extract_info(self, content):
        try:
            if content[:2] == b'BM':
                self.width = int.from_bytes(content[18:22], 'little')
                self.height = int.from_bytes(content[22:26], 'little')
                self.bpp = int.from_bytes(content[28:30], 'little')
        except:
            pass

    def get_path(self):
        return f"{self.path}"
    def get_freq(self):
        return f"{self.freq}"


def classify_file(path, content):
    if len(content) == 0:
        return None

    freq = [0] * 256
    for char in content:
        freq[char] += 1

    total = len(content)

    ASCIICount = sum(freq[i] for i in list(range(9, 14)) + list(range(32, 128)))
    zeroCount = freq[0]

    if ASCIICount / total > 0.9:
        if content.startswith(b'<'):
            xml = XMLFile(path)
            xml.freq=freq;
            xml.extract_tag(content)
            return xml

        obj = TextASCII(path)
        obj.freq=freq
        return obj

    if zeroCount / total >= 0.3:
        obj = TextUNICODE(path)
        obj.freq=freq
        return obj

    else:
        if content[:2] == b'BM':
            bmp = BMP(path)
            bmp.freq=freq;
            bmp.extract_info(content)
            return bmp

        obj = Binary(path)
        obj.freq=freq;
        return obj


def scan_directory(root_dir):
    ASCIIFiles = []
    unicodeFiles = []
    bmpFiles = []
    XMLFiles = []
    bmpFiles = []
    
    for root_dir, subdirs, files in os.walk(root_dir):
        for file in os.listdir(root_dir):
            file_path = os.path.join(root_dir, file)
            if os.path.isfile(file_path):
            # deschide fișierul spre acces binar
                f = open(file_path, 'rb')
                    
                try:
                    content = f.read()
                    obj = classify_file(file_path, content)

                    if obj is None:
                        continue
                    if isinstance(obj, XMLFile):
                        XMLFiles.append(obj.get_path())
                    elif isinstance(obj, TextASCII):
                        ASCIIFiles.append(obj.get_path())
                    elif isinstance(obj, TextUNICODE):
                        unicodeFiles.append(obj.get_path())
                    elif isinstance(obj, BMP):
                        bmpFiles.append([obj.width, obj.height, obj.bpp, obj.get_path()])

                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                finally:
                    f.close();

    print("\nASCII files:")
    for f in ASCIIFiles:
        print(f)

    print("\nXML files:")
    for f in XMLFiles:
        print(f)

    print("\nUNICODE files:")
    for f in unicodeFiles:
        print(f)

    print("\nBMP files:")
    for f in bmpFiles:
        print(f)


if __name__ == "__main__":
    directory = input("Enter directory path: ")
    scan_directory(directory)