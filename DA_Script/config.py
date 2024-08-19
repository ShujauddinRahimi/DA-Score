# This script will serve to define all the configuration details so that they are all in one place and can be easily changed.

import pandas as pd

create_record_output_folders = True
time_tracking = False

class processed_df:
    def __init__(self, df: pd.DataFrame, da_score_dict: dict, overall_da_score: float):
        self.df = df

        self.da_score_dict = da_score_dict

        self.overall_da_score = overall_da_score


