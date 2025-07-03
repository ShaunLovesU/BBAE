from hex_to_bit import hex_list_to_bit
from bit_to_hex import bit_list_to_hex
from slidingWindow import aggregate_entropy_across_messages,find_significant_changes
import matplotlib.pyplot as plt
import numpy as np
# from PM import PM
# from etlv import ETLV
'''
main code excution
'''



def normalize(arr,t_min, t_max):
    norm_arr = []
    diff = t_max-t_min
    diff_arr = max(arr)-min(arr)
    for i in arr:
        temp = (((i-min(arr))*diff)/diff_arr)+t_min
        norm_arr.append(temp)
    return norm_arr



def pad_to_byte_alignment(data):
    """
    Pad zeros at the front of each bit string in the data to make it byte-aligned.

    Parameters:
    data (list of lists): The input data containing bit strings.

    Returns:
    list of lists: The data with each bit string padded to be byte-aligned.
    """
    padded_data = []
    for sublist in data:
        padded_sublist = []
        for bit_string in sublist:
            length = len(bit_string)
            padding_needed = (8 - (length % 8)) % 8
            padded_bit_string = '0' * padding_needed + bit_string
            padded_sublist.append(padded_bit_string)
        padded_data.append(padded_sublist)
    return padded_data



# def remove_padding(merged_data, padding_positions):
#     """
#     Remove padded zeros from the merged bit string based on the given padding positions.

#     Parameters:
#     merged_data (str): The merged bit string containing padded zeros.
#     padding_positions (list of int): The positions of the padded zeros in the merged string.

#     Returns:
#     str: The original bit string without padding.
#     """
#     # Convert the merged string into a list (strings are immutable)
#     merged_list = list(merged_data)

#     # Remove the padding positions
#     for pos in sorted(padding_positions, reverse=True):
#         del merged_list[pos]  # Remove the padded zero at the specified position

#     # Join the list back into a string
#     original_data = ''.join(merged_list)

#     return original_data



def split_bit_data(bit_data, intervals):
    """
    Split bit_data into segments according to intervals.

    Parameters:
    bit_data (str or list): A sequence of bits (e.g., '10110011').
    intervals (list of tuples): A list of (start, end) positions.

    Returns:
    list: A list of bit segments corresponding to the intervals.
    """
    segments = []
    for start, end in intervals:
        # Ensure that the interval is within the bit_data length
        segment = bit_data[start:end+1]  # Include the end position
        segments.append(segment)
    segments.append(bit_data[end+1:])
    return segments

def boundaries_to_intervals(boundaries):
    """
    Convert a list of boundary values into a list of tuples representing intervals.

    Parameters:
    boundaries (list of int): A list of integer boundary values.

    Returns:
    list of tuples: A list where each tuple represents an interval as (start, end).
    """
    intervals = []
    n = len(boundaries)
    for i in range(n - 1):
        start = boundaries[i]
        # For the last interval, include the end boundary without subtracting 1
        if i == n - 2:
            end = boundaries[-1] -1
        else:
            end = boundaries[i + 1] - 1
        intervals.append((start, end))
    return intervals

def sig_change(list1, list2,threshold):

    changes = []

    # Loop through both lists and calculate the relative change or absolute difference
    for i in range(1, len(list1)):
        # Handle list1
        if list1[i-1] == 0:
            change1 = abs(list1[i])
        else:
            change1 = abs(list1[i] - list1[i-1]) / list1[i-1]

        # Handle list2
        if list2[i-1] == 0:
            change2 = abs(list2[i])
        else:
            change2 = abs(list2[i] - list2[i-1]) / list2[i-1]

        # Collect both changes in a tuple
        if change1 >= threshold or change2 >= threshold:
        # if change1 >= threshold :
            changes.append(i)

    return changes




def bit_congruence(seg1, seg2):
    # Count how many bits are the same in both bytes
    c_agree = sum(b1 == b2 for b1, b2 in zip(seg1, seg2))
    
    # Bit congruence is the number of matching bits divided by 8
    bit_congruence_value = c_agree / len(seg1)
    return bit_congruence_value

def average_bit_congruence(messages, segment_start, segment_length):
    total_congruence = 0
    num_comparisons = 0
    # Compare each pair of segments using bit congruence
    for i in range(len(messages)):
        for j in range(i + 1, len(messages)):
            # Check if both messages are long enough for the segment
            if len(messages[i]) >= segment_start + segment_length and len(messages[j]) >= segment_start + segment_length:
                segment1 = messages[i][segment_start:segment_start + segment_length]
                segment2 = messages[j][segment_start:segment_start + segment_length]
                
                congruence = bit_congruence(segment1, segment2)
                total_congruence += congruence
                num_comparisons += 1

    # Calculate and return the average bit congruence
    if num_comparisons == 0:
        return 0  # If there's only one message, return 0
    else:
        return (total_congruence / num_comparisons)
    



def initialize_dic(credit_dict,first_list):
    for i in first_list:
        if i not in credit_dict.keys():
            credit_dict[i] = 0



def update_dic(input_list, credits_dict):
    for i in input_list:
        if i in credits_dict.keys():
            credits_dict[i] += 1
        else:
            credits_dict[i] = 0

def main():
    # file = "tcp_messages.txt" Change to your dataset path
    # TCP
    # file = 'First_Try_diversity.txt' Change to your dataset path
    #  MQTT
    raw_data = []
    with open(file) as file:
        # open raw data file, and store into a list line by line
        for line in file:
            each_line = line.rstrip()
            raw_data.append(each_line)
    file.close()

    # convert raw data into bit-oriented
    bit_data = hex_list_to_bit(raw_data)
    #
    # packet_manager = PM()
    # etlv_instance = ETLV(bit_data, packet_manager, filter_rate=0.4)
    # print(etlv_instance)
    # quit()
    # res = min(len(ele) for ele in bit_data)
    
    # # printing result
    # print("Length of minimum string is : " + str(res))
    # quit()

    # calculate entropy for a fixed window of size 8
    eight_bit_window = aggregate_entropy_across_messages(bit_data,8)
    en_win8_header = eight_bit_window[:21] #uncomment for TCPHEADER
    
    # find significant changes when use window size 8
    # return a tuple, (a,b) the boundary shows in the middle of these two pos
    # size_8_boundaries = find_significant_changes(eight_bit_window)


    # do the same thing to 4 bit window, 2 bit, 1 bit
    four_bit_window = aggregate_entropy_across_messages(bit_data,4)
    two_bit_window = aggregate_entropy_across_messages(bit_data,2)
    one_bit_window = aggregate_entropy_across_messages(bit_data,1)
    #
    en_win4_header = four_bit_window[:41]#uncomment for TCPHEADER
    en_win2_header = two_bit_window[:81]#uncomment for TCPHEADER
    en_win1_header = one_bit_window[:161]#uncomment for TCPHEADER
    # print(en_win2_header)
    # quit()
    # en_win8_header = eight_bit_window[:3]
    # en_win4_header = four_bit_window[:5]
    # en_win2_header = two_bit_window[:9]
    # en_win1_header = one_bit_window[:17] #for mqtt

    



    '''
    bit-congruence
    
    '''
     # calculate the Bit congruence for each byte, each iteration shift 1 bit left
    window_8 = []
    max_length = max(len(message) for message in bit_data)
    start_pos =0
    while start_pos + 8 <= max_length:
        average_con_8bit= average_bit_congruence(bit_data,start_pos,8)
        window_8.append(average_con_8bit)
        start_pos+=8
    # win8_header = window_8[:3] #uncomment for MQTTheader
    win8_header = window_8[:21]   #uncomment for TCPHEADER
    # print(win8_header)

    window_4 = []
    start_pos =0
    while start_pos + 4 <= max_length:
        average_con_4bit= average_bit_congruence(bit_data,start_pos,4)
        window_4.append(average_con_4bit)
        start_pos+=4
    # win4_header = window_4[:5] #uncomment for MQTTheader
    win4_header = window_4[:41] #uncomment for TCPHEADER
    # print(window_4)

    window_2 = []
    start_pos =0
    while start_pos + 2 <= max_length:
        average_con_2bit= average_bit_congruence(bit_data,start_pos,2)
        window_2.append(average_con_2bit)
        start_pos+=2
    # win2_header = window_2[:9] #uncomment for MQTTheader
    win2_header = window_2[:81] #uncomment for TCPHEADER

    window_1 = []
    start_pos =0
    while start_pos + 1 <= max_length:
        average_con_1bit= average_bit_congruence(bit_data,start_pos,1)
        window_1.append(average_con_1bit)
        start_pos+=1
    # win1_header = window_1[:17] #uncomment for MQTTheader
    win1_header = window_1[:161] #uncomment for TCPHEADER

    threshold = 0.5
    win8_b= sig_change(win8_header,en_win8_header,threshold)
    win4_b = sig_change(win4_header,en_win4_header,threshold)
    win2_b= sig_change(win2_header,en_win2_header,threshold)
    win1_b = sig_change(win1_header,en_win1_header,threshold)
    # print(win8_header)
    # quit()
    # print(win4_b)
    # quit()
    print(win1_b)

    for i in range(len(win8_b)):
        win8_b[i] = win8_b[i] *8

    for i in range(len(win4_b)):
        win4_b[i] = win4_b[i] *4
    for i in range(len(win2_b)):
        win2_b[i] = win2_b[i] *2


    # print(win1_b)
    # print(win2_b)
    # print(win4_b)
    # print(win8_b)
    # quit()

    
    credit_dict = {}
    initialize_dic(credit_dict,win8_b)
    # print(win4_b)
    # quit()
    # update the credit if the different window size verified the boundary
    update_dic(win4_b,credit_dict)
    update_dic(win2_b,credit_dict)
    update_dic(win1_b,credit_dict)

    # # sort the dict by keys for better observe
    my_keys = list(credit_dict.keys())
    my_keys.sort()
    sorted_credit_dict = {i:credit_dict[i] for i in my_keys}

    # print(sorted_credit_dict)

    check_list=[0]
    # true_TCP = [16,32,64,96,100,106,112,124,140,156]
    # true_MQTT= [0,4,8,16]
    for key in credit_dict:
        if credit_dict[key] >= 1:
            check_list.append(key)
    check_list.sort()
    print(check_list)
    intervals = boundaries_to_intervals(check_list)
    # print(intervals)
    # intervals = [(0, 1), (2, 3), (4, 5), (6, 6), (7, 7), (8, 8), (9, 9),(10,14),(15,15)]
    # quit()
    # Split the bit data according to the intervals
    segments=[]
    for i in bit_data:
        segment = split_bit_data(i, intervals)
        segments.append(segment)
    # print(segments[0])
    # print(segments[0])
    padded_data = pad_to_byte_alignment(segments)
    # print(padded_data[0])

    reseambled_data = []
    # Print the padded data
    for i, sublist in enumerate(padded_data):
        # print(f"Sublist {i+1}:")
        sub = ''
        for bit_string in sublist:
            sub+= str(bit_string)
        reseambled_data.append(sub)
        # print()  # Add a blank line between sublists
    # print(reseambled_data[0])

    '''
    translate bit string back to hex-stream for Binary-inferno
    
    '''

    hex_list = bit_list_to_hex(reseambled_data)
    # print(hex_list[0])







    # Open the file in write mode
    file = open("output.txt", "w")

    # Loop through the list and write each string to the file
    for string in hex_list:
        file.write(string + "\n")  # Adding a newline after each string
    print("sucessfully write into txt file")
    # Close the file
    file.close()

    print("All strings have been written to 'output.txt'")

    quit()
    x1 = list(range(len(win8_header)))
    x2 = list(range(len(win4_header)))
    x3 = list(range(len(win2_header)))
    x4 = list(range(len(win1_header)))

    '''
    Normalize
    '''
    en_win1_header = normalize(en_win1_header,0,1)
    en_win2_header = normalize(en_win2_header,0,1)
    en_win4_header = normalize(en_win4_header,0,1)
    en_win8_header = normalize(en_win8_header,0,1)


    plt.figure(figsize=(10, 6))
    plt.plot(x1, win8_header,label = 'Blue Line: Bit Congrunence', marker='o', linestyle='-', color='b')
    plt.plot(x1, en_win8_header, label = 'Red Line = Shannon Entropy',marker='x', linestyle='-', color='r')

    plt.legend(loc='upper left')
    plt.title("Entropy VS Similarity for window size 8")
    plt.xlabel("Segment Index")
    plt.ylabel("Similarity and Entropy")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(x2, win4_header,label = 'Blue Line: Bit Congrunence', marker='o', linestyle='-', color='b')
    plt.plot(x2, en_win4_header, label = 'Red Line = Shannon Entropy',marker='x', linestyle='-', color='r')
    plt.title("Entropy VS Similarity for window size 4")
    plt.xlabel("Segment Index")
    plt.ylabel("Similarity and Entropy")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(x3, win2_header,label = 'Blue Line: Bit Congrunence', marker='o', linestyle='-', color='b')
    plt.plot(x3, en_win2_header, label = 'Red Line = Shannon Entropy',marker='x', linestyle='-', color='r')
    plt.title("Entropy VS Similarity for window size 2")
    plt.xlabel("Segment Index")
    plt.ylabel("Similarity and Entropy")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(x4, win1_header,label = 'Blue Line: Bit Congrunence', marker='o', linestyle='-', color='b')
    plt.plot(x4, en_win1_header, label = 'Red Line = Shannon Entropy',marker='x', linestyle='-', color='r')
    plt.title("Entropy VS Similarity for window size 1")
    plt.xlabel("Segment Index")
    plt.ylabel("Similarity and Entropy")
    plt.grid(True)
    plt.show()

    

if __name__ == "__main__":
    main()