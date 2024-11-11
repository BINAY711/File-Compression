import os
import heapq

class FileCompression:

    def __init__(self, path):
        self.path = path
        self.codes = {}
        self.reverse_codes = {}

    def _build_frequency_dict(self, text):
        """ Builds a frequency dictionary for characters in the text """
        return {char: text.count(char) for char in set(text)}

    def _build_heap(self, freq_dict):
        """ Builds a heap from the frequency dictionary """
        heap = []
        for value, freq in freq_dict.items():
            node = BinaryTreeNode(value, freq)
            heapq.heappush(heap, node)
        return heap

    def _build_huffman_tree(self, heap):
        """ Builds the Huffman tree from the heap """
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = BinaryTreeNode(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            heapq.heappush(heap, merged)
        return heap[0]  # The root node of the Huffman tree

    def _generate_codes(self, node, code=""):
        """ Generate Huffman codes for each character """
        if node is None:
            return
        if node.value is not None:
            self.codes[node.value] = code
            self.reverse_codes[code] = node.value
        self._generate_codes(node.left, code + "0")
        self._generate_codes(node.right, code + "1")

    def _encode_text(self, text):
        """ Encodes the text using the Huffman codes """
        return ''.join(self.codes[char] for char in text)

    def _add_padding(self, encoded_text):
        """ Adds padding to the encoded text to make its length a multiple of 8 """
        padding = 8 - len(encoded_text) % 8
        padded_encoded_text = f"{padding:08b}" + encoded_text + "0" * padding
        return padded_encoded_text

    def _convert_to_bytes(self, padded_encoded_text):
        """ Converts the padded encoded text to bytes """
        return bytearray(int(padded_encoded_text[i:i + 8], 2) for i in range(0, len(padded_encoded_text), 8))

    def compress(self):
        """ Compresses the file and returns the path of the compressed file """
        output_path = os.path.splitext(self.path)[0] + ".bin"
        
        with open(self.path, "r", encoding="utf-8") as file:
            text = file.read()

        # Build frequency dictionary and heap
        freq_dict = self._build_frequency_dict(text)
        heap = self._build_heap(freq_dict)

        # Build the Huffman tree and generate the codes
        root = self._build_huffman_tree(heap)
        self._generate_codes(root)

        # Encode the text
        encoded_text = self._encode_text(text)

        # Add padding and convert to bytes
        padded_encoded_text = self._add_padding(encoded_text)
        byte_data = self._convert_to_bytes(padded_encoded_text)

        # Write to output file
        with open(output_path, "wb") as output_file:
            output_file.write(byte_data)

        print(f"File compressed successfully: {output_path}")
        return output_path

    def _remove_padding(self, bit_string):
        """ Removes padding from the bit string """
        padding_info = bit_string[:8]
        padding_size = int(padding_info, 2)
        return bit_string[8:-padding_size] if padding_size else bit_string[8:]

    def _decode_text(self, bit_string):
        """ Decodes the bit string using the reverse Huffman codes """
        current_code = ""
        decoded_text = ""
        for bit in bit_string:
            current_code += bit
            if current_code in self.reverse_codes:
                decoded_text += self.reverse_codes[current_code]
                current_code = ""
        return decoded_text

    def decompress(self, input_path):
        """ Decompresses the binary file and writes the decompressed text to a new file """
        output_path = os.path.splitext(input_path)[0] + "_decompressed.txt"
        
        with open(input_path, "rb") as file:
            bit_string = ""
            byte = file.read(1)
            while byte:
                bit_string += f"{ord(byte):08b}"
                byte = file.read(1)

        # Remove padding and decode
        bit_string = self._remove_padding(bit_string)
        decompressed_text = self._decode_text(bit_string)

        # Write decompressed text to output file
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(decompressed_text)

        print(f"File decompressed successfully: {output_path}")


class BinaryTreeNode:
    def __init__(self, value, freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        return self.freq == other.freq


def main():
    input_path = input("Enter the file name (path): ")
    file_compression = FileCompression(input_path)

    # Compress the file
    compressed_file_path = file_compression.compress()

    # Decompress the file
    file_compression.decompress(compressed_file_path)


if __name__ == "__main__":
    main()
