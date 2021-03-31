import pandas as pd
import numpy as np
import numbers

def read_csv():
    enviromental = pd.read_csv("C:/Users/idoef/PycharmProjects/metadata_iso/EnviromentalClinical.csv")
    mlst = pd.read_csv('C:/Users/idoef/PycharmProjects/metadata_iso/mlst.csv')
    strains_info_table = pd.read_csv('C:/Users/idoef/PycharmProjects/metadata_iso/strains_info_table_toDB.csv')
    enviromental = enviromental[['Assembly','Isolation type']]
    mlst = mlst[['Refseq assembly accession','MLST Sequence Type']]
    print(len(mlst))
    print(len(enviromental))
    print(len(strains_info_table))
    mlst.rename(columns={'Refseq assembly accession': 'assembly_RefSeq', 'MLST Sequence Type': 'MLST_Sequence_Type'}, inplace=True)
    enviromental.rename(columns={'Assembly': 'Assembly_GenBank', 'Isolation type': 'Isolation_type'}, inplace=True)
    mlst['MLST_Sequence_Type'] = mlst['MLST_Sequence_Type'].fillna(" | | ")
    mlst['MLST_Sequence_Type'] = mlst['MLST_Sequence_Type'].astype("str")
    for index, row in mlst.iterrows():
        if len(row['MLST_Sequence_Type'].split("|")) == 3:
            if row['MLST_Sequence_Type'].split("|")[2] != '-':
                value = row['MLST_Sequence_Type'].split("|")[2]
                row['MLST_Sequence_Type'] = value
            else:
                row['MLST_Sequence_Type'] = ""
    strains_info_table = strains_info_table.merge(mlst, how="left", on ='assembly_RefSeq')
    strains_info_table = strains_info_table.merge(enviromental, how="left", on ='Assembly_GenBank')
    strains_info_table.to_csv("correct_strains_info_table.csv")


read_csv()

