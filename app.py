# Import from libraries
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg

# Define reactive calc
UPDATE_INTERVAL_SECS: int = 3

DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp":temp, "timestamp":timestamp}
    reactive_value_wrapper.get().append(new_dictionary_entry)
    deque_snapshot = reactive_value_wrapper.get()
    df = pd.DataFrame(deque_snapshot)
    latest_dictionary_entry = new_dictionary_entry
    return deque_snapshot, df, latest_dictionary_entry

# Define the Shiny UI Page layout
ui.page_opts(title="PyShiny Express: Live Data Example", fillable=True, style="background-color: lightblue; font-family: 'Comic Sans MS'")

# Define the Shiny UI Page sidebar
with ui.sidebar(open="open", style="background-color: lightblue; font-family: 'Comic Sans MS'"):
    ui.h2("Antarctic Explorer", class_="text-center text-white")
    ui.p(
        "A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center text-white",
    )
    ui.hr()
    ui.h6(class_="text-white")
    ui.span("Links:", class_="text-white")
    ui.a(
        "GitHub Source",
        href="https://github.com/denisecase/cintel-05-cintel",
        target="_blank",
        class_="text-white"
    )
    ui.a(
        "GitHub App",
        href="https://denisecase.github.io/cintel-05-cintel/",
        target="_blank",
        class_="text-white"
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank", class_="text-white")
    ui.a(
        "PyShiny Express",
        href="hhttps://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
        class_="text-white"
    )

# Define the Shiny UI Page main panel
with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("sun"),
        style="background-color: lightyellow; font-family: 'Comic Sans MS'",
    ):
        "Current Temperature"
        @render.text
        def display_temp():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"
        "warmer than usual"

    with ui.card(full_screen=True, style="background-color: lightyellow; font-family: 'Comic Sans MS'"):
        ui.card_header("Current Date and Time")
        @render.text
        def display_time():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

with ui.card(full_screen=True, style="background-color: lightyellow; font-family: 'Comic Sans MS'"):
    ui.card_header("Most Recent Readings")
    @render.data_frame
    def display_df():
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option('display.width', None)
        return render.DataGrid( df,width="100%")

with ui.card(style="background-color: lightyellow; font-family: 'Comic Sans MS'"):
    ui.card_header("Chart with Current Trend")
    @render_plotly
    def display_plot():
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        
            fig = px.scatter(df,
            x="timestamp",
            y="temp",
            title="Temperature Readings with Regression Line",
            labels={"temp": "Temperature (°C)", "timestamp": "Time"},
            color_discrete_sequence=["blue"] )

            sequence = range(len(df))
            x_vals = list(sequence)
            y_vals = df["temp"]

            slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
            df['best_fit_line'] = [slope * x + intercept for x in x_vals]

            fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

            fig.update_layout(xaxis_title="Time",yaxis_title="Temperature (°C)")

        return fig
