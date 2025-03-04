'''
This file is Sliding Window, use for detect the boundaries using the calculation of entropy.
Made by Shawn Zhang(V00931372) from University of Victoria
'''

from collections import defaultdict
import math
import numpy as np
from collections import Counter
'''
pre_def
'''
def calculate_entropy(bit_window):
    """Calculate the entropy for a given bit window."""
    bit_count = len(bit_window)*1.0
    qty = Counter(bit_window)

    entropy= 0.0
    for i in qty:
        v = qty[i]*1.0
        pb = (v/bit_count)
        assert(pb<=1)
        if pb >=0:
            entropy+=(pb*math.log2(pb))
    return abs(-entropy)
def binary_string_to_bit_list(binary_string):
    """Convert a binary string (e.g., '1101') to a list of bits (e.g., [1, 1, 0, 1])."""
    return [int(bit) for bit in binary_string]

def aggregate_entropy_across_messages(binary_strings, window_size):
    """Calculate aggregated entropy for each segment across multiple binary messages."""
    entropy_dict = defaultdict(list)  # Dictionary to store entropy lists for each start position
    entropy_list=[]

    # Convert all binary strings into a single list of bits
    bitstreams = [binary_string_to_bit_list(binary_string) for binary_string in binary_strings]

    # Find the maximum length of the bitstreams to align all messages
    max_length = max(len(bitstream) for bitstream in bitstreams)

    # Pad shorter bitstreams with zeros (if necessary) to align all bitstreams
    padded_bitstreams = [
        bitstream + [0] * (max_length - len(bitstream)) for bitstream in bitstreams
    ]

    num_windows = (max_length ) // window_size
    for i in range(num_windows):
        # Extract the bit window across all messages
        e_list=[]
        a = [padded_bitstreams[j][i * window_size:i * window_size + window_size] for j in range(len(padded_bitstreams))]
        for i in a:
            sa = ''.join(str(e) for e in i)
            e_list.append(sa)
        # print(len(e_list))
        # quit()
        # aggregated_window = list(np.ravel(a))

    



        # Calculate entropy for this aggregated window
        entropy = calculate_entropy(e_list)
        entropy_list.append(entropy)
    return entropy_list

def find_significant_changes(entropy_dict, threshold=0.2):
    """Find and store segment boundaries where the entropy change exceeds the given threshold."""
    boundary_list = []

    for start_pos, entropy_values in entropy_dict.items():
        for i in range(1, len(entropy_values)):
            prev_entropy, prev_start, prev_end = entropy_values[i - 1]
            curr_entropy, curr_start, curr_end = entropy_values[i]

            # Handle the special case where the previous entropy is 0
            if prev_entropy == 0 or curr_entropy == 0:
                relative_change = abs(curr_entropy-prev_entropy)  # Consider this as a significant change
            elif prev_entropy != 0 and curr_entropy != 0:
                # Calculate relative change in entropy
                relative_change = abs(curr_entropy - prev_entropy) / prev_entropy
            else:
                continue

            # Check if the relative change exceeds the threshold
            if relative_change > threshold:
                boundary_list.append( curr_start)
    
    return boundary_list
