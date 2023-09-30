re_col = "Race/Ethnicity"

def filter_df(df_all, selected_reason, selected_time, selected_gender, selected_residency):
    if selected_residency != 'ALL':
        # This was added in July 2021
        df_all = df_all[df_all['residency']==selected_residency]
    if selected_time != 'ALL':
        if selected_time=='MOST RECENT YEAR':
            df_all = df_all[df_all['Month']>df_all['Month'].max()-12]
        else:
            df_all = df_all[df_all['Month'].dt.year==selected_time]

    mon_min = df_all['Month'].min()
    mon_max = df_all['Month'].max()
    num_months = (mon_max - mon_min).n+1

    if selected_reason != 'ALL':
        df_all = df_all[df_all['reason_for_stop']==selected_reason]
    if selected_gender != 'ALL':
        df_all = df_all[df_all['gender']==selected_gender]  

    return df_all, num_months
    