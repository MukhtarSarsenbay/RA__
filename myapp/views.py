# myapp/views.py
import math
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from django.shortcuts import render
import matplotlib
import plotly.graph_objs as go
from scipy.signal import savgol_filter
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline
import numpy as np
import pandas as pd
import scipy
#plotly dash
import plotly.express as px
from scipy import signal
from scipy.interpolate import make_interp_spline
import time
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot, important



def input_values(request):
    if request.method == 'POST':
        #limitation of quantity
        tetta_s = []
        #taking values directly from excel
        values = request.POST['values']
        raw_values = values.strip().split(' ')
        for raw_value in raw_values:
            if raw_value:
        # Replace comma with dot and convert to float
                cleaned_value = raw_value.replace(",", ".")
                tetta_s.append(float(cleaned_value))
        cleaned_values_string = ' '.join(map(str, tetta_s))
        values = cleaned_values_string


        #getting inputs and values
        a = float(request.POST.get('a', 0.1))
        n = float(request.POST.get('n', 0.1))
        m = float(request.POST.get('m', 0.1))
        soil_suction_r = float(request.POST.get('soil_suction_r', 10000))
        e = math.exp(1)
        T_s = 72.75 * (10 ** (-3))
        soil_suction = []


        #getting from excel too
        values1 = request.POST['values1']
        raw_values = values1.strip().split(' ')
        for raw_value in raw_values:
            if raw_value:
                cleaned_value = raw_value.replace(",", ".")
                soil_suction.append(float(cleaned_value))
        cleaned_values_string = ' '.join(map(str, soil_suction))
        values1 = cleaned_values_string

        water_content = []
        pore_radius = []
        derivation = []
        base_soil_suction=[0.01,1.00,2.00,5.00,10.00,20.00,30.00,40.00,50.00,60.0,70.00,80.00,90.00,100.00,200.00,500.00,1000.00,5000.00,10000.00,100000.00,1000000.00]

        base_thetha_s=[]

        # Block of code for the 3rd formula - Water content
        def formula3(value, value2, a, n, m, soil_suction_r):
            ln1 = math.log(1 + float(value) / float(soil_suction_r))
            ln2 = math.log(1 + (10 ** 6) / float(soil_suction_r))
            ln3 = math.log(e + (float(value / float(a))) ** float(n))
            overall_formula = float(value2) * (1 - float(ln1) / float(ln2)) * ((1 / float(ln3)) ** float(m))
            return overall_formula

        # Block of code for the 4th formula - Derivation
        def formula4(value, a, n, m, soil_suction_r, T_s):
            ln1 = math.log(1 + (float(value) / soil_suction_r))
            ln2 = math.log(1 + (10 ** 6) / soil_suction_r)
            ln3 = math.log(e + ((float(value / a)) ** n))
            block1 = float(1 - (ln1 / ln2))
            block2 = float(m * n * ((float(value / a) ** (n - 1))))
            block2_1 = float(a * (e + ((float(value / a)) ** n))) * (ln3 ** (m + 1))
            block2_2 = block2 / block2_1
            block3 = float(1 / (value + soil_suction_r))
            block4 = float(1 / (math.log(1 + (10 ** 6) / soil_suction_r)))
            block5 = float(1 / (ln3 ** m))
            second_formula_1 = block1 * block2_2
            third_formula = block3 * block4 * block5
            second_formula = second_formula_1 + third_formula
            return second_formula, float(2 * T_s) / float(value)

        # Block of code to call the third formula and fourth formula functions

        for value in range(len(tetta_s)):
            water_content.append(formula3(soil_suction[value], tetta_s[0], a, n, m, soil_suction_r))
            derivation_value, pore_radius_value = formula4(tetta_s[value], a, n, m, soil_suction_r, T_s)
            derivation.append(derivation_value)
            pore_radius.append(pore_radius_value)

        # Block of code to finish the 4th formula
        for value in range(len(tetta_s)):
            derivation[value] = derivation[value] * soil_suction[value]


        swcc_trace = go.Scatter(
            x=soil_suction,
            y=water_content,
            mode='lines',
            name='Best-fit'
        )

        # Create a trace for measured data
        measured_trace = go.Scatter(
            x=soil_suction,
            y=tetta_s,
            mode='markers',
            name='Measured Data'
        )

        # Define the layout for the plot
        swcc_layout = go.Layout(
            title='Soil-Water Characteristics Curve with input',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick='auto',
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey"
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick=0.1,
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',
            paper_bgcolor='white'
        )

        # Create a figure with the defined data and layout
        #swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)
        swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)

        # Convert the figure to an HTML div element
        swcc_div1 = swcc_fig.to_html(full_html=False)


        # Define the objective function for optimization
        def objective(variables):
            a, n, m, soil_suction_r = variables
            global error_sum
            error_sum=0
            for i in range(len(soil_suction)):
                predicted_water_content = formula3(soil_suction[i],tetta_s[0], a, n, m, soil_suction_r)
                error = abs(tetta_s[i] - predicted_water_content)
                #if error>=0.00101000:
                #if error>=0.005:
                #if error>=0:
                if error>=0.0001:
                    error_sum+=error #- >even worse
            for i in range(len(soil_suction)):
                predicted_water_content = formula3(soil_suction[i],tetta_s[0], a, n, m, soil_suction_r)
                error = ((tetta_s[i] - predicted_water_content) / tetta_s[i]) ** 2
                print(error)
                #if error>0.4689999999999999:
                if error>0.1:
                #if error>0.5:
                    continue
            error_sum += error

            return error_sum

        # Perform optimization



        # Set initial values for optimization,
        x0 = [0.1, 0.1, 0.1, 0.1]
        # Set bounds for the variables (optional)
        #bounds = [(1,None), (1, 6), (1, 6), (1,None)]
        bounds = [(0.5, None), (0.5, 6), (0.5, 6), (0.5, None)]



        # Perform optimization
        result = minimize(objective, x0, method='SLSQP', bounds=bounds,options={'maxiter': 10000, 'ftol': 1e-10})
        #result = differential_evolution(objective, bounds, maxiter=1000, tol=1e-8)

        optimal_a, optimal_n, optimal_m, optimal_soil_suction_r = result.x

        for value in range(len(base_soil_suction)):
            base_thetha_s.append(formula3(base_soil_suction[value],tetta_s[0],optimal_a,optimal_n,optimal_m,optimal_soil_suction_r))
        #to save input values
        a1=a
        n1=n
        m1=m
        soil_suction_r1=soil_suction_r

        #to draw a new graph
        a=optimal_a
        n=optimal_n
        m=optimal_m
        soil_suction_r=optimal_soil_suction_r
        water_content.clear()
        derivation.clear()
        pore_radius.clear()

        for value in range(len(soil_suction)):
            water_content.append(formula3(soil_suction[value], tetta_s[0], optimal_a, optimal_n, optimal_m, optimal_soil_suction_r))
            derivation_value, pore_radius_value = formula4(soil_suction[value], a, n, m, soil_suction_r, T_s)
            derivation.append(derivation_value)
            pore_radius.append(pore_radius_value)

        # Block of code to finish 4th formula
        for value in range(len(soil_suction)):
            derivation[value] = derivation[value] * soil_suction[value]


        # Graph 2.
        # smoothed_water_content = savgol_filter(water_content, window_length=10, polyorder=8)
        #
        # smoothed_trace = go.Scatter(
        #     x=soil_suction,
        #     y=smoothed_water_content,
        #     mode='lines',
        #     name='Smoothed Best-fit'
        # )

        #smoothed_water_content = scipy.signal.savgol_filter(water_content, window_length=17, polyorder=10)

        # gfg=make_interp_spline(soil_suction, water_content, k=9 )
        # new_water_content=gfg(soil_suction)


        #swcc = go.Scatter(x=soil_suction, y=smoothed_water_content, mode='lines', name='Smoothed Best-fit', line_shape='spline')
        #swcc=go.Scatter(x=soil_suction,y=signal.savgol_filter(water_content,17,13),mode='lines', name='Smoothed Best-fit', line_shape='spline',trendline_options=dict(frac=0.1))#9-11 are good numbers#17 is max for windows
        #swcc = go.Scatter(x=soil_suction, y=new_water_content, mode='lines', name='Best-fit')
        swcc_trace = go.Scatter(x=soil_suction, y=water_content, mode='lines', name='Best-fit')
        measured_trace = go.Scatter(x=soil_suction, y=tetta_s, mode='markers', name='Measured Data')
        swcc_layout = go.Layout(
            title='Soil-Water Characteristics Curve with input',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to black
                dtick='auto',
                linewidth=1, linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to grey
                dtick='0.1',  # Automatically determine the spacing of grid lines
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
        )
        swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)
        swcc_div = swcc_fig.to_html(full_html=False)




        #Graph 3
        new_swcc = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Smoothed Best-fit Extended', line_shape='spline')
        new_swcc_trace = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Best-fit Extended')
        new_measured_trace = go.Scatter(x=soil_suction, y=tetta_s, mode='markers', name='Measured Data')
        optimal_a_text = f"a: {round(optimal_a, 2)}"
        optimal_n_text = f"n: {round(optimal_n, 2)}"
        optimal_m_text = f"m: {round(optimal_m, 2)}"
        optimal_soil_suction_r_text = f"Ψr: {round(optimal_soil_suction_r, 2)}"
        annotations = [
        dict(
        x=1.0,  # Adjust the x position to move the annotation to the right
        y=0.85,  # Adjust the y position to move the annotation upwards
        xref='paper',
        yref='paper',
        text=optimal_a_text,
        showarrow=False,
        font=dict(size=14),  # Increase the font size
        ),
        dict(
        x=1.0,  # Adjust the x position
        y=0.80,   # Adjust the y position
        xref='paper',
        yref='paper',
        text=optimal_n_text,
        showarrow=False,
        font=dict(size=14),  # Increase the font size
        ),
        dict(
        x=1.0,  # Adjust the x position
        y=0.75,  # Adjust the y position
        xref='paper',
        yref='paper',
        text=optimal_m_text,
        showarrow=False,
        font=dict(size=14),  # Increase the font size
        ),
        dict(
        x=1.0,  # Adjust the x position
        y=0.70,   # Adjust the y position
        xref='paper',
        yref='paper',
        text=optimal_soil_suction_r_text,
        showarrow=False,
        font=dict(size=14),  # Increase the font size
        ),
        ]

        new_swcc_layout = go.Layout(
        title='New Soil-Water Characteristics Curve with input',
        xaxis=dict(
            type='log',
            title='Soil Suction (kPa)',
            showgrid=True,  # Show the grid lines
            gridwidth=0.4,     # Set the grid line width
            gridcolor='grey',  # Set the grid line color to black
            dtick='auto',
            linewidth=1, linecolor='black',
            zeroline=True,
            zerolinecolor="grey",
        ),
        yaxis=dict(
            title='Volumetric Water Content (w)',
            showgrid=True,  # Show the grid lines
            gridwidth=0.4,  # Set the grid line width
            gridcolor='grey',  # Set the grid line color to grey
            dtick='0.1',  # Automatically determine the spacing of grid lines
            linewidth=1,
            linecolor='black',
            zeroline=True,
            zerolinecolor="grey",
            rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
            annotations=annotations
        )
        new_swcc_fig = go.Figure(data=[new_swcc_trace, new_measured_trace,new_swcc], layout=new_swcc_layout)
        new_swcc_div = new_swcc_fig.to_html(full_html=False)




        context = {
        'tetta_s': values,
        'soil_suction': values1,
        'a': a1,
        'n': n1,
        'm': m1,
        'soil_suction_r': soil_suction_r1,
        'optimal_a': round(optimal_a,2),
        'optimal_n': round(optimal_n,2),
        'optimal_m': round(optimal_m,2),
        'optimal_soil_suction_r': round(optimal_soil_suction_r,2),
        'error_sum': error_sum,
        'swcc_div': swcc_div,  # Pass the Soil-Water Characteristics Curve as HTML div
        'new_swcc_div':new_swcc_div,
        'swcc_div1':swcc_div1,
        }
        # return render(request, 'myapp/input_values.html', context)
        return render(request, 'myapp/output_graph.html', context)
    else:
        #return render(request, 'myapp/input_values.html')
        return render(request, 'myapp/input_values.html')

def show_graph (request):
    # return render(request, 'myapp/input_values.html')
    return render(request, 'myapp/input_values.html')


def second_formula(request):
    if request.method == 'POST':
        # limitation of quantity
        soil_suction = []
        # taking values directly from excel
        vol_wat_values = request.POST['values']
        raw_values = vol_wat_values.strip().split(' ')

        vol_water = []
        clean_vol_water = []
        for raw_value in raw_values:
            if raw_value:
                # Replace comma with dot and convert to float
                cleaned_value = raw_value.replace(",", ".")
                vol_water.append(float(cleaned_value))

        # Now, vol_wat_values should be a list of floats
        vol_wat_values = vol_water

        # getting inputs and values
        a = float(request.POST.get('a', 0.1))
        n = float(request.POST.get('n', 0.1))
        m = float(request.POST.get('m', 0.1))
        e = math.exp(1)

        suc_values1 = request.POST['values1']
        raw_values = suc_values1.strip().split(' ')
        soil_suction = []

        for raw_value in raw_values:
            if raw_value:
                cleaned_value = raw_value.replace(",", ".")
                soil_suction.append(float(cleaned_value))

        cleaned_values_string = ' '.join(map(str, soil_suction))
        suc_values1 = cleaned_values_string
        suc_values1 = [float(value) for value in soil_suction if value]

        water_content = []
        pore_radius = []
        derivation = []
        base_soil_suction = [0.01, 1.00, 2.00, 5.00, 10.00, 20.00, 30.00, 40.00, 50.00, 60.00, 70.00, 80.00, 90.00, 100.00, 200.00, 500.00, 1000.00, 5000.00, 10000.00, 100000.00, 1000000.00]
        base_thetha_s = []

        corr_fact = 1
        #volumentric_tetta_s

        # TODO: matric suction find
        def main_formula(suc_value, vol_wat_values, a, n, m):
            ans = float(vol_wat_values) / float(((math.log(e + (float(suc_value) / a) ** n, e)) ** m))
            return ans


        for suc in suc_values1:
            clean_vol_water.append(float(main_formula(suc, vol_wat_values[0], a, n, m)))
        print(vol_water)

        swcc_trace = go.Scatter(
            x=suc_values1,
            y=clean_vol_water,
            mode='lines',
            name='Best-fit'
        )

        # Create a trace for measured data
        measured_trace = go.Scatter(
            x=suc_values1,
            y=vol_water,
            mode='markers',
            name='Measured Data'
        )

        # Define the layout for the plot
        swcc_layout = go.Layout(
            title='Soil-Water Characteristics Curve with input',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick='auto',
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey"
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick=0.1,
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',
            paper_bgcolor='white'
        )

        # Create a figure with the defined data and layout
        #
        swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)

        # Convert the figure to an HTML div element
        swcc_div1 = swcc_fig.to_html(full_html=False)

        # Define the objective function for optimization
        def objective(variables):
            a, n, m = variables
            global error_sum
            error_sum = 0
            for i in range(len(suc_values1)):
                predicted_water_content = main_formula(suc_values1[i], vol_wat_values[0], a, n, m)
                error = abs(vol_wat_values[i] - predicted_water_content)
                if error >= 0.0001:
                    error_sum += error  # - >even worse
            for i in range(len(suc_values1)):
                predicted_water_content = main_formula(suc_values1[i], vol_wat_values[0], a, n, m)
                error = ((vol_wat_values[i] - predicted_water_content) / vol_wat_values[i]) ** 2
                #print(error)
                if error > 0.1:
                    continue
            error_sum += error

            return error_sum

        # Perform optimization

        # Set initial values for optimization,
        x0 = [0.1, 0.1, 0.1]
        bounds = [(0.1, None), (0.1, 6), (0.1, 6)] # Should be constant

        # Perform optimization

        start = time.time()
        #result = minimize(objective, x0, method='Powell', bounds=bounds)
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, options={'maxiter': 10000, 'ftol': 1e-10})
        # result = differential_evolution(objective, bounds, maxiter=1000, tol=1e-8)

        optimal_a, optimal_n, optimal_m = result.x
        end = time.time()
        print(end - start)
        optimized_volume = []
        for value in range(len(base_soil_suction)):
            base_thetha_s.append(main_formula(base_soil_suction[value], vol_wat_values[0], optimal_a, optimal_n, optimal_m))

        for value in range(len(suc_values1)):
            optimized_volume.append(main_formula(suc_values1[value], vol_wat_values[0], optimal_a, optimal_n, optimal_m))
        # to save input values
        a1 = a
        n1 = n
        m1 = m

        # to draw a new graph
        a = optimal_a
        n = optimal_n
        m = optimal_m
        water_content.clear()
        derivation.clear()
        pore_radius.clear()

        swcc_trace = go.Scatter(x=suc_values1, y=optimized_volume, mode='lines', name='Best-fit')
        measured_trace = go.Scatter(x=suc_values1, y=vol_wat_values, mode='markers', name='Measured Data')
        swcc_layout = go.Layout(
            title='Soil-Water Characteristics Curve',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to black
                dtick='auto',
                linewidth=1, linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to grey
                dtick='0.1',  # Automatically determine the spacing of grid lines
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
        )
        swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)
        swcc_div = swcc_fig.to_html(full_html=False)

        # Graph 3

        new_swcc = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Smoothed Best-fit Extended',
                              line_shape='spline')
        new_swcc_trace = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Best-fit Extended')
        new_measured_trace = go.Scatter(x=suc_values1, y=vol_wat_values, mode='markers', name='Measured Data')
        optimal_a_text = f"a: {round(optimal_a, 2)}"
        optimal_n_text = f"n: {round(optimal_n, 2)}"
        optimal_m_text = f"m: {round(optimal_m, 2)}"
        annotations = [
            dict(
                x=1.0,  # Adjust the x position to move the annotation to the right
                y=0.85,  # Adjust the y position to move the annotation upwards
                xref='paper',
                yref='paper',
                text=optimal_a_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
            dict(
                x=1.0,  # Adjust the x position
                y=0.80,  # Adjust the y position
                xref='paper',
                yref='paper',
                text=optimal_n_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
            dict(
                x=1.0,  # Adjust the x position
                y=0.75,  # Adjust the y position
                xref='paper',
                yref='paper',
                text=optimal_m_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
        ]

        new_swcc_layout = go.Layout(
            title='New Soil-Water Characteristics Curve',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to black
                dtick='auto',
                linewidth=1, linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to grey
                dtick='0.1',  # Automatically determine the spacing of grid lines
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
            annotations=annotations
        )
        new_swcc_fig = go.Figure(data=[new_swcc_trace, new_measured_trace, new_swcc], layout=new_swcc_layout)
        new_swcc_div = new_swcc_fig.to_html(full_html=False)


        # Graph 5
        psd_trace_smooth = go.Scatter(x=pore_radius, y=derivation, mode='lines', name='Smooth PSD', line_shape="spline")
        psd_trace = go.Scatter(x=pore_radius, y=derivation, mode='lines', name='PSD')
        psd_layout = go.Layout(
            title='Pore-Size Distribution',
            xaxis=dict(
                type='log',
                title='Pore Radius (mm)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick='auto',
                linewidth=1,
                linecolor='black',  # Change the x-axis color to black
                zeroline=True,  # Start the x-axis from 0
                zerolinecolor='grey',  # Change the c
                # olor of the zero line
            ),
            yaxis=dict(
                title='Derivation',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick=0.1,  # Change dtick to a specific value
                linewidth=1,
                linecolor='black',

                zeroline=True,
                zerolinecolor='grey',
                rangemode='tozero'
            ),
            plot_bgcolor='#f7f6f5',
            paper_bgcolor='white',
        )

        psd_fig = go.Figure(data=[psd_trace_smooth], layout=psd_layout)
        psd_div = psd_fig.to_html(full_html=False)

        context = {
            'tetta_s': vol_wat_values,
            'soil_suction': suc_values1,
            'a': a1,
            'n': n1,
            'm': m1,
            'optimal_a': round(optimal_a, 2),
            'optimal_n': round(optimal_n, 2),
            'optimal_m': round(optimal_m, 2),
            'error_sum': error_sum,
            'swcc_div': swcc_div,  # Pass the Soil-Water Characteristics Curve as HTML div
            'psd_div': psd_div,  # Pass the Pore-Size Distribution as HTML div
            'new_swcc_div': new_swcc_div,
            'swcc_div1': swcc_div1,
        }
        # return render(request, 'myapp/input_values.html', context)
        return render(request, 'second_assignment/output_graph.html', context)
    else:
        # return render(request, 'myapp/input_values.html')
        return render(request, 'second_assignment/input_values.html')


def main_page(request):
    return render(request, 'myapp/main_page.html')

def third_formula(request):
    if request.method == 'POST':
        vol_wat_values = request.POST['values']
        raw_values = vol_wat_values.strip().split(' ')

        vol_water = []
        clean_vol_water = []
        for raw_value in raw_values:
            if raw_value:
                # Replace comma with dot and convert to float
                cleaned_value = raw_value.replace(",", ".")
                vol_water.append(float(cleaned_value))

        # Now, vol_wat_values should be a list of floats
        vol_wat_values = vol_water

        # getting inputs and values
        a = float(request.POST.get('a', 0.1))
        n = float(request.POST.get('n', 0.1))
        m = float(request.POST.get('m', 0.1))
        e = math.exp(1)

        suc_values1 = request.POST['values1']
        raw_values = suc_values1.strip().split(' ')
        soil_suction = []

        for raw_value in raw_values:
            if raw_value:
                cleaned_value = raw_value.replace(",", ".")
                soil_suction.append(float(cleaned_value))

        cleaned_values_string = ' '.join(map(str, soil_suction))
        suc_values1 = cleaned_values_string
        suc_values1 = [float(value) for value in soil_suction if value]

        water_content = []
        pore_radius = []
        derivation = []
        base_soil_suction = [0.01, 1.00, 2.00, 5.00, 10.00, 20.00, 30.00, 40.00, 50.00, 60.00, 70.00, 80.00, 90.00, 100.00, 200.00, 500.00, 1000.00, 5000.00, 10000.00, 100000.00, 1000000.00]
        base_thetha_s = []

        corr_fact = 1
        #volumentric_tetta_s

        # TODO: matric suction find
        def main_formula(suc_value, vol_wat_values, a, n, m):
            ans = float(vol_wat_values) / float(((math.log(e + (float(suc_value) / a) ** n, e)) ** m))
            return ans


        for suc in suc_values1:
            clean_vol_water.append(float(main_formula(suc, vol_wat_values[0], a, n, m)))
        print(vol_water)

        swcc_trace = go.Scatter(
            x=suc_values1,
            y=clean_vol_water,
            mode='lines',
            name='Best-fit'
        )

        # Create a trace for measured data
        measured_trace = go.Scatter(
            x=suc_values1,
            y=vol_water,
            mode='markers',
            name='Measured Data'
        )

        # Define the layout for the plot
        swcc_layout = go.Layout(
            title='Soil-Water Characteristics Curve with input',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick='auto',
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey"
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick=0.1,
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',
            paper_bgcolor='white'
        )

        # Create a figure with the defined data and layout
        #
        swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)

        # Convert the figure to an HTML div element
        swcc_div1 = swcc_fig.to_html(full_html=False)

        # Define the objective function for optimization
        def objective(variables):
            a, n, m = variables
            global error_sum
            error_sum = 0
            for i in range(len(suc_values1)):
                predicted_water_content = main_formula(suc_values1[i], vol_wat_values[0], a, n, m)
                error = abs(vol_wat_values[i] - predicted_water_content)
                if error >= 0.0001:
                    error_sum += error  # - >even worse
            for i in range(len(suc_values1)):
                predicted_water_content = main_formula(suc_values1[i], vol_wat_values[0], a, n, m)
                error = ((vol_wat_values[i] - predicted_water_content) / vol_wat_values[i]) ** 2
                #print(error)
                if error > 0.1:
                    continue
            error_sum += error

            return error_sum

        # Perform optimization

        # Set initial values for optimization,
        x0 = [0.1, 0.1, 0.1]
        bounds = [(0.1, None), (0.1, 6), (0.1, 6)] # Should be constant

        # Perform optimization

        start = time.time()
        #result = minimize(objective, x0, method='Powell', bounds=bounds)
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, options={'maxiter': 10000, 'ftol': 1e-10})
        # result = differential_evolution(objective, bounds, maxiter=1000, tol=1e-8)

        optimal_a, optimal_n, optimal_m = result.x
        end = time.time()
        print(end - start)
        optimized_volume = []
        for value in range(len(base_soil_suction)):
            base_thetha_s.append(main_formula(base_soil_suction[value], vol_wat_values[0], optimal_a, optimal_n, optimal_m))

        for value in range(len(suc_values1)):
            optimized_volume.append(main_formula(suc_values1[value], vol_wat_values[0], optimal_a, optimal_n, optimal_m))
        # to save input values
        a1 = a
        n1 = n
        m1 = m

        # to draw a new graph
        a = optimal_a
        n = optimal_n
        m = optimal_m
        water_content.clear()
        derivation.clear()
        pore_radius.clear()

        swcc_trace = go.Scatter(x=suc_values1, y=optimized_volume, mode='lines', name='Best-fit')
        measured_trace = go.Scatter(x=suc_values1, y=vol_wat_values, mode='markers', name='Measured Data')
        swcc_layout = go.Layout(
            title='Soil-Water Characteristics Curve',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to black
                dtick='auto',
                linewidth=1, linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to grey
                dtick='0.1',  # Automatically determine the spacing of grid lines
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
        )
        swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)
        swcc_div = swcc_fig.to_html(full_html=False)

        # Graph 3

        new_swcc = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Smoothed Best-fit Extended',
                              line_shape='spline')
        new_swcc_trace = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Best-fit Extended')
        new_measured_trace = go.Scatter(x=suc_values1, y=vol_wat_values, mode='markers', name='Measured Data')
        optimal_a_text = f"a: {round(optimal_a, 2)}"
        optimal_n_text = f"n: {round(optimal_n, 2)}"
        optimal_m_text = f"m: {round(optimal_m, 2)}"
        annotations = [
            dict(
                x=1.0,  # Adjust the x position to move the annotation to the right
                y=0.85,  # Adjust the y position to move the annotation upwards
                xref='paper',
                yref='paper',
                text=optimal_a_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
            dict(
                x=1.0,  # Adjust the x position
                y=0.80,  # Adjust the y position
                xref='paper',
                yref='paper',
                text=optimal_n_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
            dict(
                x=1.0,  # Adjust the x position
                y=0.75,  # Adjust the y position
                xref='paper',
                yref='paper',
                text=optimal_m_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
        ]

        new_swcc_layout = go.Layout(
            title='New Soil-Water Characteristics Curve',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to black
                dtick='auto',
                linewidth=1, linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to grey
                dtick='0.1',  # Automatically determine the spacing of grid lines
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
            annotations=annotations
        )
        new_swcc_fig = go.Figure(data=[new_swcc_trace, new_measured_trace, new_swcc], layout=new_swcc_layout)
        new_swcc_div = new_swcc_fig.to_html(full_html=False)


        # Graph 5
        psd_trace_smooth = go.Scatter(x=pore_radius, y=derivation, mode='lines', name='Smooth PSD', line_shape="spline")
        psd_trace = go.Scatter(x=pore_radius, y=derivation, mode='lines', name='PSD')
        psd_layout = go.Layout(
            title='Pore-Size Distribution',
            xaxis=dict(
                type='log',
                title='Pore Radius (mm)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick='auto',
                linewidth=1,
                linecolor='black',  # Change the x-axis color to black
                zeroline=True,  # Start the x-axis from 0
                zerolinecolor='grey',  # Change the c
                # olor of the zero line
            ),
            yaxis=dict(
                title='Derivation',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick=0.1,  # Change dtick to a specific value
                linewidth=1,
                linecolor='black',

                zeroline=True,
                zerolinecolor='grey',
                rangemode='tozero'
            ),
            plot_bgcolor='#f7f6f5',
            paper_bgcolor='white',
        )

        psd_fig = go.Figure(data=[psd_trace_smooth], layout=psd_layout)
        psd_div = psd_fig.to_html(full_html=False)

        context = {
            'tetta_s': vol_wat_values,
            'soil_suction': suc_values1,
            'a': a1,
            'n': n1,
            'm': m1,
            'optimal_a': round(optimal_a, 2),
            'optimal_n': round(optimal_n, 2),
            'optimal_m': round(optimal_m, 2),
            'error_sum': error_sum,
            'swcc_div': swcc_div,  # Pass the Soil-Water Characteristics Curve as HTML div
            'psd_div': psd_div,  # Pass the Pore-Size Distribution as HTML div
            'new_swcc_div': new_swcc_div,
            'swcc_div1': swcc_div1,
        }
        # return render(request, 'myapp/input_values.html', context)
        return render(request, 'second_assignment/output_graph.html', context)
    else:
        # return render(request, 'myapp/input_values.html')
        return render(request, 'second_assignment/input_values.html')


def dashnoard(request):
    return render(request, 'dashboard/index.html')

def test(request):
    return render(request, 'myapp/test.html')



def difficult_formula(request):
    import math
    from scipy.optimize import differential_evolution
    if request.method == 'POST':
        volumetric_water_content = request.POST['values']
        raw_values = volumetric_water_content.strip().split(' ')

        vol_water = []
        clean_vol_water = []
        for raw_value in raw_values:
            if raw_value:
                # Replace comma with dot and convert to float
                cleaned_value = raw_value.replace(",", ".")
                vol_water.append(float(cleaned_value))

        # Now, vol_wat_values should be a list of floats
        volumetric_water_content = vol_water

        psi_array = request.POST['values1']
        raw_values = psi_array.strip().split(' ')
        soil_suction = []

        tetta_max = float(request.POST.get('tetta_max', 0.1))
        tetta_mid = tetta_max / 2
        tetta_min = 0.01
        psi_ws1 = 2
        psi_ws2 = 10
        psi_we2 = 10
        psi_max = 10
        psi_wd = 10

        for raw_value in raw_values:
            if raw_value:
                cleaned_value = raw_value.replace(",", ".")
                soil_suction.append(float(cleaned_value))

        cleaned_values_string = ' '.join(map(str, soil_suction))
        psi_array = cleaned_values_string
        psi_array = [float(value) for value in soil_suction if value]

        water_content = []
        pore_radius = []
        derivation = []
        base_soil_suction = [0.01, 1.00, 2.00, 5.00, 10.00, 20.00, 30.00, 40.00, 50.00, 60.00, 70.00, 80.00, 90.00, 100.00, 200.00, 500.00, 1000.00, 5000.00, 10000.00, 100000.00, 1000000.00]
        base_thetha_s = []

        # Function to prevent overflow in exponential calculations
        def safe_exp(x):
            max_exp_arg = 700  # Define a max value to prevent overflow
            return math.exp(max(-max_exp_arg, min(x, max_exp_arg)))

        # Soil water characteristic function with given parameters
        def third_form(psi, tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max):
            psi_wd = psi_ws1 ** 0.3 * psi_ws2 ** 0.7  # weighted average of psi_ws1 and psi_ws2

            if psi < psi_ws1:
                first_exp = safe_exp(0)
            else:
                first_exp_arg = (-4.75 * ((psi - psi_ws1) / (psi_wd - psi_ws1)))
                first_exp = round(safe_exp(first_exp_arg), 2)

            if psi < psi_ws2:
                second_exp = safe_exp(0)
            else:
                second_exp_arg = (-4.75 * ((psi - psi_ws2) / (psi_max - psi_ws2)))
                second_exp = round(safe_exp(second_exp_arg), 2)

            CF = round((1 - (math.log(1 + psi / psi_we2)) / math.log(1 + (10 ** 6) / psi_we2)), 4)

            tetta = round(((tetta_max - tetta_mid) * first_exp + (tetta_mid - tetta_min) * second_exp + tetta_min) * CF,
                          3)
            return tetta


        # for suc in psi_array:
        #     clean_vol_water.append(float(third_form(suc, tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max)))
        print(vol_water)


        # Define the objective function for optimization
        def objective(variables):
            tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max = variables
            global mse
            mse = sum((volumetric_water_content[i] - third_form(psi_array[i], tetta_max, tetta_mid, tetta_min, psi_ws1,
                                                                psi_ws2, psi_we2, psi_max)) ** 2 for i in
                      range(len(psi_array))) / len(psi_array)
            return mse

        # Initial guesses and bounds for parameters
        x0 = [tetta_max-0.09 , tetta_mid/2,0.01, 0.01, 100, 100, 1000]
        bounds = [(tetta_max-0.09, tetta_max), (tetta_mid/2, tetta_max), (0.01, 100), (100, 2000), (100, 2000),
                  (1000, 10000)]

        # Perform optimization using differential evolution
        # result = differential_evolution(
        #     objective,
        #     bounds=bounds,
        #     strategy='best1bin',
        #     maxiter=100,  # Increased number of iterations
        #     popsize=12,  # Larger population size to explore more solutions
        #     tol=1e-10,  # Smaller tolerance for more precise convergence
        #     mutation=(0.6, 1.2),  # Fine-tune mutation
        #     recombination=0.7,  # Higher recombination rate
        #     polish=True,  # Enable polishing to refine the final solution
        #     seed=42  # Optional: Set seed for reproducible results
        # )
        # result = differential_evolution(objective, bounds)
        result = differential_evolution(objective, bounds, strategy='best1bin', maxiter=100, popsize=15, tol=1e-6)

        # Extract the optimized parameters
        opt_tetta_mid, opt_tetta_min, opt_psi_ws1, opt_psi_ws2, opt_psi_we2, opt_psi_max = result.x

        # Print optimized parameters
        print("Optimized Parameters:")
        print("Theta_mid:", opt_tetta_mid)
        print("Theta_min:", opt_tetta_min)
        print("Psi_ws1:", opt_psi_ws1)
        print("Psi_ws2:", opt_psi_ws2)
        print("Psi_we2:", opt_psi_we2)
        print("Psi_max:", opt_psi_max)

        # Perform optimization
        optimized_volume = []
        for value in range(len(base_soil_suction)):
            base_thetha_s.append(third_form(base_soil_suction[value],tetta_max, opt_tetta_mid, opt_tetta_min, opt_psi_ws1, opt_psi_ws2, opt_psi_we2, opt_psi_max))

        for value in range(len(psi_array)):
            optimized_volume.append(third_form(psi_array[value], tetta_max, opt_tetta_mid, opt_tetta_min, opt_psi_ws1, opt_psi_ws2, opt_psi_we2, opt_psi_max))
        # to save input values
        tetta_mid1 = tetta_mid
        tetta_min1 = tetta_min
        psi_ws11 = psi_ws1
        psi_ws21 = psi_ws2
        psi_we21 = psi_we2
        psi_max1 = psi_max

        # to draw a new graph
        tetta_mid = opt_tetta_mid
        tetta_min = opt_tetta_min
        psi_ws1 = opt_psi_ws1
        psi_ws2 = opt_psi_ws2
        psi_we2 = opt_psi_we2
        psi_max = opt_psi_max

        water_content.clear()
        derivation.clear()
        pore_radius.clear()

        swcc_trace = go.Scatter(x=psi_array, y=optimized_volume, mode='lines', name='Best-fit')
        measured_trace = go.Scatter(x=psi_array, y=volumetric_water_content, mode='markers', name='Measured Data')
        swcc_layout = go.Layout(
            title='Soil-Water Characteristics Curve',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to black
                dtick='auto',
                linewidth=1, linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to grey
                dtick='0.1',  # Automatically determine the spacing of grid lines
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
        )
        swcc_fig = go.Figure(data=[swcc_trace, measured_trace], layout=swcc_layout)
        swcc_div = swcc_fig.to_html(full_html=False)

        # Graph 3

        new_swcc = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Smoothed Best-fit Extended',
                              line_shape='spline')
        new_swcc_trace = go.Scatter(x=base_soil_suction, y=base_thetha_s, mode='lines', name='Best-fit Extended')
        new_measured_trace = go.Scatter(x=psi_array, y=volumetric_water_content, mode='markers', name='Measured Data')

        opt_tetta_mid_text = f"tetta_mid: {round(opt_tetta_mid, 2)}"
        opt_tetta_min_text= f"tetta_min: {round(opt_tetta_min, 2)}"
        opt_psi_ws1_text = f"psi_ws1: {round(opt_psi_ws1, 2)}"
        opt_psi_ws2_text = f"psi_ws2: {round(opt_psi_ws2, 2)}"
        opt_psi_we2_text = f"psi_we2: {round(opt_psi_we2, 2)}"
        opt_psi_max_text = f"psi_max: {round(opt_psi_max, 2)}"
        annotations = [
            dict(
                x=1.0,  # Adjust the x position to move the annotation to the right
                y=0.85,  # Adjust the y position to move the annotation upwards
                xref='paper',
                yref='paper',
                text=opt_tetta_mid_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
            dict(
                x=1.0,  # Adjust the x position
                y=0.80,  # Adjust the y position
                xref='paper',
                yref='paper',
                text=opt_tetta_min_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
            dict(
                x=1.0,  # Adjust the x position
                y=0.75,  # Adjust the y position
                xref='paper',
                yref='paper',
                text=opt_psi_ws1_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
            dict(
                x=1.0,  # Adjust the x position
                y=0.65,  # Adjust the y position
                xref='paper',
                yref='paper',
                text=opt_psi_ws2_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
            dict(
                x=1.0,  # Adjust the x position
                y=0.60,  # Adjust the y position
                xref='paper',
                yref='paper',
                text=opt_psi_we2_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
            dict(
                x=1.0,  # Adjust the x position
                y=0.55,  # Adjust the y position
                xref='paper',
                yref='paper',
                text=opt_psi_max_text,
                showarrow=False,
                font=dict(size=14),  # Increase the font size
            ),
        ]

        new_swcc_layout = go.Layout(
            title='New Soil-Water Characteristics Curve',
            xaxis=dict(
                type='log',
                title='Soil Suction (kPa)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to black
                dtick='auto',
                linewidth=1, linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
            ),
            yaxis=dict(
                title='Volumetric Water Content (w)',
                showgrid=True,  # Show the grid lines
                gridwidth=0.4,  # Set the grid line width
                gridcolor='grey',  # Set the grid line color to grey
                dtick='0.1',  # Automatically determine the spacing of grid lines
                linewidth=1,
                linecolor='black',
                zeroline=True,
                zerolinecolor="grey",
                rangemode='tozero',
            ),
            plot_bgcolor='#f7f6f5',  # Set the background color to white
            paper_bgcolor='white',  # Set the paper (bdtick=0.1rder) color to white
            annotations=annotations
        )
        new_swcc_fig = go.Figure(data=[new_swcc_trace, new_measured_trace, new_swcc], layout=new_swcc_layout)
        new_swcc_div = new_swcc_fig.to_html(full_html=False)


        # Graph 5
        psd_trace_smooth = go.Scatter(x=pore_radius, y=derivation, mode='lines', name='Smooth PSD', line_shape="spline")
        psd_trace = go.Scatter(x=pore_radius, y=derivation, mode='lines', name='PSD')
        psd_layout = go.Layout(
            title='Pore-Size Distribution',
            xaxis=dict(
                type='log',
                title='Pore Radius (mm)',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick='auto',
                linewidth=1,
                linecolor='black',  # Change the x-axis color to black
                zeroline=True,  # Start the x-axis from 0
                zerolinecolor='grey',  # Change the c
                # olor of the zero line
            ),
            yaxis=dict(
                title='Derivation',
                showgrid=True,
                gridwidth=0.4,
                gridcolor='grey',
                dtick=0.1,  # Change dtick to a specific value
                linewidth=1,
                linecolor='black',

                zeroline=True,
                zerolinecolor='grey',
                rangemode='tozero'
            ),
            plot_bgcolor='#f7f6f5',
            paper_bgcolor='white',
        )

        psd_fig = go.Figure(data=[psd_trace_smooth], layout=psd_layout)
        psd_div = psd_fig.to_html(full_html=False)

        tetta_mid1 = tetta_mid
        tetta_min1 = tetta_min
        psi_ws11 = psi_ws1
        psi_ws21 = psi_ws2
        psi_we21 = psi_we2
        psi_max1 = psi_max
        context = {
            'tetta_s': volumetric_water_content,
            'soil_suction': psi_array,
            'tetta_mid': tetta_mid1,
            'tetta_min': tetta_min1,
            'psi_ws1': psi_ws11,
            'psi_ws2': psi_ws21,
            'psi_we2': psi_we21,
            'psi_max': psi_max1,
            'optimal_tetta_mid': round(opt_tetta_mid, 2),
            'optimal_tetta_min': round(opt_tetta_min, 2),
            'optimal_psi_ws1': round(opt_psi_ws1, 2),
            'optimal_psi_ws2': round(opt_psi_ws2, 2),
            'optimal_psi_we2': round(opt_psi_we2, 2),
            'optimal_psi_max': round(opt_psi_max, 2),
            'error_sum': mse,
            'swcc_div': swcc_div,  # Pass the Soil-Water Characteristics Curve as HTML div
            'psd_div': psd_div,  # Pass the Pore-Size Distribution as HTML div
            'new_swcc_div': new_swcc_div,
        }




        return render(request, 'difficult/output_graph.html', context)
    else:
        # return render(request, 'myapp/input_values.html')
        return render(request, 'difficult/input_values.html')
