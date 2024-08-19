# This script will serve to create the visualization of the scenario.

import plotly.graph_objects as go
import os


def create_visualization_output_files(data_frame, output_path, scenario_name):
    time_stamps = data_frame['timestamp'].drop_duplicates()

    list_of_columns_to_plot = []
    
    for col in columns_dict.keys():
        if col not in columns_to_remove:
            list_of_columns_to_plot.append(col)

    #Plotly graph
    boundary_colors = [
                'rgba(31, 119, 180, 0.075)',        # muted blue
                'rgba(255, 127, 14, 0.075)',        # safety orange
                'rgba(44, 160, 44, 0.075)',         # cooked asparagus green
                'rgba(214, 39, 40, 0.075)',         # brick red
                'rgba(148, 103, 189, 0.075)',       # muted purple
                'rgba(140, 86, 75, 0.075)',         # chestnut brown
                'rgba(227, 119, 194, 0.075)',       # raspberry yogurt pink
                'rgba(127, 127, 127, 0.075)',       # middle gray
                'rgba(188, 189, 34, 0.075)',        # curry yellow-green
                'rgba(23, 190, 207, 0.075)'         # blue-teal
            ]

    line_colors =  [
                'rgba(31, 119, 180, 1)',            # muted blue
                'rgba(255, 127, 14, 1)',            # safety orange
                'rgba(44, 160, 44, 1)',             # cooked asparagus green
                'rgba(214, 39, 40, 1)',             # brick red
                'rgba(148, 103, 189, 1)',           # muted purple
                'rgba(140, 86, 75, 1)',             # chestnut brown
                'rgba(227, 119, 194, 1)',           # raspberry yogurt pink
                'rgba(127, 127, 127, 1)',           # middle gray
                'rgba(188, 189, 34, 1)',            # curry yellow-green
                'rgba(23, 190, 207, 1)'             # blue-teal
            ]

    color_index = 0

    fig = go.Figure()

    for col in list_of_columns_to_plot:
        c_max = data_frame.groupby('timestamp')[col].max()
        c_mean = data_frame.groupby('timestamp')[col].mean()
        c_min = data_frame.groupby('timestamp')[col].min()        

        # Adds MU bands
        # fig.add_trace(go.Scatter(x=time_stamps, y = c_max, fill = None, mode = 'lines', line_color = boundary_colors[color_index], legendgroup=col, legendgrouptitle_text=col, name=col + ' max'))
        # fig.add_trace(go.Scatter(x=time_stamps, y = c_min, fill='tonexty', mode = 'lines', line_color = boundary_colors[color_index], legendgroup=col, name = col + ' min and fill', fillcolor = boundary_colors[color_index]))

        fig.add_trace(go.Scatter(x=time_stamps, y = c_mean, fill = None, mode = 'lines', line_color = line_colors[color_index], legendgroup=col, name = col))# + ' average'))

        color_index = (color_index + 1) % 10

    fig.update_layout(title = scenario_name + ' Interactive Data Visualization', xaxis_title='Time (seconds)', yaxis_title='Value', legend_title='Legend')
    try:
        fig.write_html(os.path.join(output_path, 'Interactive_DV-' + scenario_name + '.html'))
        print('Plotly plot was saved successfully.')
    except:
        print('ERROR: Plotly plot was not saved successfully.')