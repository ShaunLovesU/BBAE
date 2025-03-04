def hex_list_to_bit(hex_list):
    def hex_to_bit(hex_string):
        # Validate the input
        if len(hex_string) % 2 != 0:
            raise ValueError("Hex string length must be even.")

        # Initialize the binary string
        bit_string = ""

        # Convert each byte (2 characters) to binary
        for i in range(0, len(hex_string), 2):
            byte = hex_string[i:i+2]
            bit_string += f"{int(byte, 16):08b}"

        return bit_string

    # Convert each hex string in the list to binary
    bit_list = [hex_to_bit(hex_string) for hex_string in hex_list]

    return bit_list



# # Example usage
# hex_list = ["0467d474e82f7076c31290ffb0100269d04500000101080aa716b4d83e8ecdff0101050ac3129639c312a711"]
# bit_list = hex_list_to_bit(hex_list)
# for index, bit_string in enumerate(bit_list, start=1):
#     # Add space between every byte (8 bits)
#     formatted_bit_string = ' '.join([bit_string[i:i+8] for i in range(0, len(bit_string), 8)])
#     print(f"{index}: {formatted_bit_string}")
