import pandas as pd
import numpy as np
import numbers

def read_csv():
    data_cluster = pd.read_csv('C:/Users/idoef/PycharmProjects/cluster_script/clstrSummary_with_SorekSystems.csv')
    new_df = data_cluster.select_dtypes([np.number])
    list_columns = list(new_df.columns)
    list_numbers = [num for num in list_columns if num.isdigit()]
    data_numbers = new_df.loc[:, list_numbers]
    dict_number = data_numbers.to_dict('index')
    list_num_dict = []
    for row in dict_number:
        numbers = dict_number[row]
        dict_index = {}
        for num in numbers:
            if numbers[num] > 0:
                dict_index[num] = numbers[num]
        list_num_dict.append(dict_index)
    print(list_num_dict)
    data_cluster['combined_index'] = list_num_dict
    data_cluster = data_cluster.drop(columns=list_numbers)
    data_cluster.to_csv("correct_cluster.csv")

read_csv()

