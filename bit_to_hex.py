def bit_list_to_hex(bit_list):
    def bit_to_hex(bit_string):
        # Validate the input
        if len(bit_string) % 4 != 0:
            raise ValueError("Bit string length must be a multiple of 4.")

        # Initialize the hex string
        hex_string = ""

        # Convert each 4-bit segment to hex
        for i in range(0, len(bit_string), 4):
            bit_segment = bit_string[i:i+4]
            hex_digit = f"{int(bit_segment, 2):X}"
            hex_string += hex_digit

        return hex_string

    # Convert each bit string in the list to hex
    hex_list = [bit_to_hex(bit_string) for bit_string in bit_list]

    return hex_list


binary_string = '0000001011111111111111111001010101011001'

# Convert to hex
hex_output = bit_list_to_hex([binary_string])
print(hex_output)