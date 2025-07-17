import config
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import utils

def create_visualizations(df, output_path, scenario_name):
    time_stamps = df['timestamp'].drop_duplicates()

    list_of_columns_to_plot = []
    
    for col in config.metrics_dict.keys():
        if col not in config.columns_to_remove:
            list_of_columns_to_plot.append(col)

    if config.enable_matplotlib_graph:
        #Matplotlib graph  
        for col in list_of_columns_to_plot:
            c_max = df.groupby('timestamp')[col].max()
            c_mean = df.groupby('timestamp')[col].mean()
            c_min = df.groupby('timestamp')[col].min()

            plt.fill_between(time_stamps, c_min, c_max,
                            alpha=0.2)
            
            plt.plot(time_stamps, c_mean)

        plt.legend(list_of_columns_to_plot, bbox_to_anchor = (1, 0.5), loc='center left')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Value')
        plt.suptitle(scenario_name + ' Data Visualization')
        figure = plt.gcf().set_size_inches(25.6, 14.4)
        try:
            plt.savefig(os.path.join(output_path, 'DV-' + scenario_name + '.png'), dpi = 100)
            utils.debug_print('visualizations.py: Matplotlib plot was saved successfully.')
        except:
            utils.debug_print('visualizations.py: Matplotlib plot could not be saved.')


    if config.enable_plotly_graph:
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
            c_max = df.groupby('timestamp')[col].max()
            c_mean = df.groupby('timestamp')[col].mean()
            c_min = df.groupby('timestamp')[col].min()        

            # Adds MU bands
            if config.enable_mu_bands:
                fig.add_trace(go.Scatter(x=time_stamps, y = c_max, fill = None, mode = 'lines', line_color = boundary_colors[color_index], legendgroup=col, legendgrouptitle_text=col, name=col + ' max'))
                fig.add_trace(go.Scatter(x=time_stamps, y = c_min, fill='tonexty', mode = 'lines', line_color = boundary_colors[color_index], legendgroup=col, name = col + ' min and fill', fillcolor = boundary_colors[color_index]))

            fig.add_trace(go.Scatter(x=time_stamps, y = c_mean, fill = None, mode = 'lines', line_color = line_colors[color_index], legendgroup=col, name = col))# + ' average'))

            color_index = (color_index + 1) % 10

        fig.update_layout(title = scenario_name + ' Interactive Data Visualization', xaxis_title='Time (seconds)', yaxis_title='Value', legend_title='Legend')
        try:
            fig.write_html(os.path.join(output_path, 'Interactive_DV-' + scenario_name + '.html'))
            utils.debug_print('visualizations.py: Plotly plot was saved successfully.')
        except:
            utils.debug_print('visualizations.py: Plotly plot was not saved successfully.')

def draw_scenario(timestamp, ego_vehicle, challenger_vehicle, x_lim_min, x_lim_max, y_lim_min, y_lim_max):
    # Plotting options: 1: minimal, 2: d_lon_min + d_lat_min, 3: full
    plot_option = 3

    # Viewing options: 1: step-by-step, 2: automatic
    view_option = 1
    
    plt.xlim(x_lim_min - 20, x_lim_max + 20)
    plt.ylim(y_lim_min - 20, y_lim_max + 20)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.legend([timestamp])

    plt.show(block=False)
    
    # Regular Bounding Boxes
    x1,y1 = ego_vehicle.get_bbox().exterior.xy
    x2,y2 = challenger_vehicle.get_bbox().exterior.xy
    
    plt.plot(x1, y1)
    plt.plot(x2, y2)
    
    # Path Polygon
    if config.global_debug:
        x1,y1 = ego_vehicle.path_polygon().exterior.xy
        x2,y2 = challenger_vehicle.path_polygon().exterior.xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)
        
    # Front Bumpers
    plt.plot(ego_vehicle.front_bumper()[0].x, ego_vehicle.front_bumper()[0].y, 'b.')
    plt.plot(challenger_vehicle.front_bumper()[0].x, challenger_vehicle.front_bumper()[0].y, 'r.')

    x1,y1 = ego_vehicle.front_bumper().line.xy
    x2,y2 = challenger_vehicle.front_bumper().line.xy
    plt.plot(x1, y1)
    plt.plot(x2, y2)

    if (plot_option > 2):
        # Heading Vectors
        x1,y1 = ego_vehicle.heading_vector().xy
        x2,y2 = challenger_vehicle.heading_vector().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Front Bumper Lines
        x1,y1 = ego_vehicle.front_bumper_line().xy
        x2,y2 = challenger_vehicle.front_bumper_line().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Rear Bumper Lines
        x1,y1 = ego_vehicle.rear_bumper_line().xy
        x2,y2 = challenger_vehicle.rear_bumper_line().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Left Side Lines
        x1,y1 = ego_vehicle.left_side_line().xy
        x2,y2 = challenger_vehicle.left_side_line().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Right Side Lines
        x1,y1 = ego_vehicle.right_side_line().xy
        x2,y2 = challenger_vehicle.right_side_line().xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

    if (plot_option > 1):
        # Rear Bumpers
        # plt.plot(ego_vehicle.rear_bumper().x, ego_vehicle.rear_bumper().y, 'y.')
        # plt.plot(challenger_vehicle.rear_bumper().x, challenger_vehicle.rear_bumper().y, 'y.')

        x1,y1 = ego_vehicle.rear_bumper().line.xy
        x2,y2 = challenger_vehicle.rear_bumper().line.xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # # Left Sides
        # plt.plot(ego_vehicle.left_side().x, ego_vehicle.left_side().y, 'm.')
        # plt.plot(challenger_vehicle.left_side().x, challenger_vehicle.left_side().y, 'm.')

        x1,y1 = ego_vehicle.left_side().line.xy
        x2,y2 = challenger_vehicle.left_side().line.xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # # Right Sides
        # plt.plot(ego_vehicle.right_side().x, ego_vehicle.right_side().y, 'c.')
        # plt.plot(challenger_vehicle.right_side().x, challenger_vehicle.right_side().y, 'c.')

        x1,y1 = ego_vehicle.right_side().line.xy
        x2,y2 = challenger_vehicle.right_side().line.xy
        plt.plot(x1, y1)
        plt.plot(x2, y2)

        # Centers
        plt.plot(ego_vehicle.center.x, ego_vehicle.center.y, 'g.')
        plt.plot(challenger_vehicle.center.x, challenger_vehicle.center.y, 'g.')

    if (view_option == 1):
        plt.waitforbuttonpress()

    plt.pause(0.00000000000001)
    plt.clf()

        # d_lon
        #x1,y1 = utils.calculate_d_lon(ego_vehicle, challenger_vehicle)[2].xy
        #x1,y1 = ego_vehicle.d_lon(challenger_vehicle)[2].xy
        #plt.plot(x1,y1, 'r')
        
        # d_lat
        #x1,y1 = sm.d_lat(ego_vehicle, challenger_vehicle)[2].xy
        #x1,y1 = ego_vehicle.d_lat(challenger_vehicle)[2].xy
        #plt.plot(x1,y1, 'r')

        # for point in sm.d_lat(ego_vehicle, challenger_vehicle)[2].boundary.geoms:
        #     line = tangent_line(ego_vehicle, point)

        #     x1, y1 = line.xy
        #     plt.plot(x1, y1, 'y')
        
        
    
        
    
        
    

# def draw_scenario(timestamp, ego_vehicle, challenger_vehicle, x_lim_min, x_lim_max, y_lim_min, y_lim_max):
#     # Plot the scenario 

#     # Plotting options: 1: minimal, 2: d_lon_min + d_lat_min, 3: full
#     plot_option = 2

#     # Viewing options: 1: step-by-step, 2: automatic
#     view_option = 2

#     # Bboxes
#     x1,y1 = ego_vehicle.get_bbox().exterior.xy
#     x2,y2 = challenger_vehicle.bbox.exterior.xy

#     plt.plot(x1, y1)
#     plt.plot(x2, y2)

#     # MM BBoxes
#     x1,y1 = ego_vehicle.mm_bbox.exterior.xy
#     x2,y2 = challenger_vehicle.mm_bbox.exterior.xy

#     plt.plot(x1, y1)
#     plt.plot(x2, y2)

#     # Ped BBox
#     x1,y1 = challenger_vehicle.rss_bbox.exterior.xy

#     plt.plot(x1, y1)

#     # Vehicle RSS BBox
#     x1,y1 = ego_vehicle.rss_bbox.exterior.xy

#     plt.plot(x1, y1)

#     # Path polygon

#     x1,y1 = ego_vehicle.path_polygon().exterior.xy
#     x2,y2 = challenger_vehicle.path_polygon().exterior.xy
#     plt.plot(x1, y1)
#     plt.plot(x2, y2)

#     # Front Bumpers
#     plt.plot(ego_vehicle.front_bumper()[0].x, ego_vehicle.front_bumper()[0].y, 'b.')
#     plt.plot(challenger_vehicle.front_bumper()[0].x, challenger_vehicle.front_bumper()[0].y, 'r.')

#     x1,y1 = ego_vehicle.front_bumper().line.xy
#     x2,y2 = challenger_vehicle.front_bumper().line.xy
#     plt.plot(x1, y1)
#     plt.plot(x2, y2)

#     if (plot_option > 2):
#         # Heading Vectors
#         x1,y1 = ego_vehicle.heading_vector().xy
#         x2,y2 = challenger_vehicle.heading_vector().xy
#         plt.plot(x1, y1)
#         plt.plot(x2, y2)

#         # Front Bumper Lines
#         x1,y1 = ego_vehicle.front_bumper_line().xy
#         x2,y2 = challenger_vehicle.front_bumper_line().xy
#         plt.plot(x1, y1)
#         plt.plot(x2, y2)

#         # Rear Bumper Lines
#         x1,y1 = ego_vehicle.rear_bumper_line().xy
#         x2,y2 = challenger_vehicle.rear_bumper_line().xy
#         plt.plot(x1, y1)
#         plt.plot(x2, y2)

#         # Left Side Lines
#         x1,y1 = ego_vehicle.left_side_line().xy
#         x2,y2 = challenger_vehicle.left_side_line().xy
#         plt.plot(x1, y1)
#         plt.plot(x2, y2)

#         # Right Side Lines
#         x1,y1 = ego_vehicle.right_side_line().xy
#         x2,y2 = challenger_vehicle.right_side_line().xy
#         plt.plot(x1, y1)
#         plt.plot(x2, y2)

#     if (plot_option > 1):
#         # Rear Bumpers
#         # plt.plot(ego_vehicle.rear_bumper().x, ego_vehicle.rear_bumper().y, 'y.')
#         # plt.plot(challenger_vehicle.rear_bumper().x, challenger_vehicle.rear_bumper().y, 'y.')

#         x1,y1 = ego_vehicle.rear_bumper().line.xy
#         x2,y2 = challenger_vehicle.rear_bumper().line.xy
#         plt.plot(x1, y1)
#         plt.plot(x2, y2)

#         # # Left Sides
#         # plt.plot(ego_vehicle.left_side().x, ego_vehicle.left_side().y, 'm.')
#         # plt.plot(challenger_vehicle.left_side().x, challenger_vehicle.left_side().y, 'm.')

#         x1,y1 = ego_vehicle.left_side().line.xy
#         x2,y2 = challenger_vehicle.left_side().line.xy
#         plt.plot(x1, y1)
#         plt.plot(x2, y2)

#         # # Right Sides
#         # plt.plot(ego_vehicle.right_side().x, ego_vehicle.right_side().y, 'c.')
#         # plt.plot(challenger_vehicle.right_side().x, challenger_vehicle.right_side().y, 'c.')

#         x1,y1 = ego_vehicle.right_side().line.xy
#         x2,y2 = challenger_vehicle.right_side().line.xy
#         plt.plot(x1, y1)
#         plt.plot(x2, y2)

#         # Centers
#         plt.plot(ego_vehicle.center.x, ego_vehicle.center.y, 'g.')
#         plt.plot(challenger_vehicle.center.x, challenger_vehicle.center.y, 'g.')

        

#         # d_lon
#         #x1,y1 = utils.calculate_d_lon(ego_vehicle, challenger_vehicle)[2].xy
#         #x1,y1 = ego_vehicle.d_lon(challenger_vehicle)[2].xy
#         #plt.plot(x1,y1, 'r')
        
#         # d_lat
#         #x1,y1 = sm.d_lat(ego_vehicle, challenger_vehicle)[2].xy
#         #x1,y1 = ego_vehicle.d_lat(challenger_vehicle)[2].xy
#         #plt.plot(x1,y1, 'r')

#         # for point in sm.d_lat(ego_vehicle, challenger_vehicle)[2].boundary.geoms:
#         #     line = tangent_line(ego_vehicle, point)

#         #     x1, y1 = line.xy
#         #     plt.plot(x1, y1, 'y')
        
    