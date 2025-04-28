import numpy as np
from collections import defaultdict
import math
import numpy as np
from collections import Counter
import time
from multiprocessing import Pool, cpu_count

def hex_list_to_bit(hex_list):
    def hex_to_bit(hex_string):
        if len(hex_string) % 2 != 0:
            raise ValueError("Hex string length must be even.")
        bit_string = ""
        for i in range(0, len(hex_string), 2):
            byte = hex_string[i:i+2]
            bit_string += f"{int(byte, 16):08b}"
        return bit_string
    return [hex_to_bit(hx) for hx in hex_list]

def bit_list_to_hex(bit_list):
    def bit_to_hex(bit_string):
        if len(bit_string) % 4 != 0:
            raise ValueError("Bit string length must be a multiple of 4.")
        hex_string = ""
        for i in range(0, len(bit_string), 4):
            hex_string += f"{int(bit_string[i:i+4], 2):X}"
        return hex_string
    return [bit_to_hex(bits) for bits in bit_list]

def optimized_calculate_entropy_for_window(bit_window):
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

def average_bit_congruence_from_segments(segments):
    mat = np.array([[int(b) for b in s] for s in segments], dtype=bool)
    total = 0
    count = 0
    for i in range(len(mat)):
        equal_counts = np.sum(mat[i+1:] == mat[i], axis=1)
        total += np.sum(equal_counts)
        count += len(equal_counts) * mat.shape[1]
    return total / count if count else 0

def _process_segment_entropy_congruence(args):
    i, bit_array, all_segments, window_size = args
    win_bits = bit_array[:, i * window_size:(i + 1) * window_size]
    entropy = optimized_calculate_entropy_for_window([''.join(row) for row in win_bits])
    avg_cong = average_bit_congruence_from_segments(all_segments[i])
    return entropy, avg_cong

def compute_entropy_and_congruence(bit_data, window_sizes):
    max_len = max(len(msg) for msg in bit_data)
    bit_array = np.array([list(msg.ljust(max_len, '0')) for msg in bit_data], dtype='U1')
    dict_entropy, dict_congruence = {}, {}
    for window_size in window_sizes:
        num_windows = max_len // window_size
        all_segments = [
            [msg[i * window_size:(i + 1) * window_size] for msg in bit_data if len(msg) >= (i + 1) * window_size]
            for i in range(num_windows)
        ]
        args = [(i, bit_array, all_segments, window_size) for i in range(num_windows)]
        with Pool(processes=cpu_count()) as pool:
            results = pool.map(_process_segment_entropy_congruence, args)
        entropy_list, congruence_list = zip(*results)
        dict_entropy[window_size] = list(entropy_list)
        dict_congruence[window_size] = list(congruence_list)
    return dict_entropy, dict_congruence

def slice_entropy_congruence(entropy_dict, congruence_dict, protocol='TCP'):
    length_map = {
        'TCP': {8: 21, 4: 41, 2: 81, 1: 161},
        'MQTT': {8: 3, 4: 5, 2: 9, 1: 17}
    }
    entropy_sliced = {}
    congruence_sliced = {}
    for win in [8, 4, 2, 1]:
        cutoff = length_map[protocol][win]
        entropy_sliced[win] = entropy_dict[win][:cutoff] if cutoff else entropy_dict[win]
        congruence_sliced[win] = congruence_dict[win][:cutoff] if cutoff else congruence_dict[win]
    return entropy_sliced, congruence_sliced

def sig_change(list1, list2, threshold):
    changes = []
    for i in range(1, len(list1)):
        if list1[i - 1] == 0:
            change1 = abs(list1[i])
        else:
            change1 = abs(list1[i] - list1[i - 1]) / list1[i - 1]
        if list2[i - 1] == 0:
            change2 = abs(list2[i])
        else:
            change2 = abs(list2[i] - list2[i - 1]) / list2[i - 1]
        if change1 >=threshold or change2 >= threshold:
            changes.append(i)
    return changes

def initialize_and_update_credit_dict(changes_dict, scales):
    credit_dict = {}
    for idx, (window, indices) in enumerate(changes_dict.items()):
        for pos in [i * scales[idx] for i in indices]:
            if pos not in credit_dict:
                credit_dict[pos] = 0
            else:
                credit_dict[pos] += 1
    return credit_dict

def boundaries_to_intervals(boundaries):
    boundaries = sorted(set(boundaries))
    return [(boundaries[i], boundaries[i+1] - 1) for i in range(len(boundaries) - 1)]

def split_bit_data(bit_data, intervals):
    return [[msg[start:end + 1] for (start, end) in intervals] + [msg[intervals[-1][1] + 1:]] for msg in bit_data]

def pad_to_byte_alignment(data):
    return [[('0' * ((8 - len(bits) % 8) % 8)) + bits for bits in sub] for sub in data]

def flatten_segments(padded_data):
    return [''.join(sublist) for sublist in padded_data]

def main():
    # file = "/Users/leijiezhang/Desktop/BBAE/Data_txt/tcp_messages.txt"
    file = "/Users/leijiezhang/Desktop/BBAE/Data_txt/First_Try_diversity.txt"
    with open(file) as f:
        raw_data = [line.strip() for line in f.readlines()]

    bit_data = hex_list_to_bit(raw_data)
    start_time = time.time()
    entropy_dict, congruence_dict = compute_entropy_and_congruence(bit_data, [8, 4, 2, 1])

    protocol = 'MQTT'
    entropy_dict, congruence_dict = slice_entropy_congruence(entropy_dict, congruence_dict, protocol)
    threshold = 0.5
    change_dict = {
        8: sig_change(congruence_dict[8], entropy_dict[8], threshold),
        4: sig_change(congruence_dict[4], entropy_dict[4], threshold),
        2: sig_change(congruence_dict[2], entropy_dict[2], threshold),
        1: sig_change(congruence_dict[1], entropy_dict[1], threshold)
    }
    credit_dict = initialize_and_update_credit_dict(change_dict, [8,4,2,1])
    trusted_boundaries = [0] + sorted(k for k, v in credit_dict.items() if v >= 1)
    change_dict = {
        1: sig_change(congruence_dict[1], entropy_dict[1], threshold),
    }
    print(trusted_boundaries)
    print(change_dict[1])
    intervals = boundaries_to_intervals(trusted_boundaries)
    segments = split_bit_data(bit_data, intervals)
    padded = pad_to_byte_alignment(segments)
    reassembled_bits = flatten_segments(padded)
    end_time = time.time()
    print(f"Congruence and entropy computation took {end_time - start_time:.2f} seconds.")
    hex_list = bit_list_to_hex(reassembled_bits)
    with open("output.txt", "w") as f:
        for line in hex_list:
            f.write(line + "\n")
    print("Output written to output.txt")

if __name__ == "__main__":
    main()