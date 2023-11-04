import taipy as tp
from taipy import Config, Core, Gui

################################################################
#            Configure application                             #
################################################################
def build_message(name):
    return f"Hello {name}!"

# A first data node configuration to model an input name.
input_name_data_node_cfg = Config.configure_data_node(id="input_name", value="Taipy")
# A second data node configuration to model the message to display.
message_data_node_cfg = Config.configure_data_node(id="message")
# A task configuration to model the build_message function.
build_msg_task_cfg = Config.configure_task("build_msg", build_message, input_name_data_node_cfg, message_data_node_cfg)
# The scenario configuration represents the whole execution graph.
scenario_cfg = Config.configure_scenario("scenario", task_configs=[build_msg_task_cfg])

################################################################
#            Design graphical interface                        #
################################################################

def submit_scenario(state):
    state.scenario.input_name.write(state.input_name)
    state.scenario.submit()
    state.message = state.scenario.message.read()

data = []
max_traffic = 0

# Define airport coordinates
airports = {
    "ATL": {"lat": 33.64086185344307, "lon": -84.43600501711686},
    "DFW": {"lat": 34.437119809208546, "lon": -108.7573508575816}
}

# Define flight data
flights = [
    {"from": "ATL", "to": "DFW", "traffic": 580}
]

for flight in flights:
    airport_from = airports[flight["from"]]
    airport_to = airports[flight["to"]]
    # Define data source to plot this flight
    data.append({
        "lat": [airport_from["lat"], airport_to["lat"]],
        "lon": [airport_from["lon"], airport_to["lon"]]
    })
    # Store the maximum traffic
    if flight["traffic"] > max_traffic:
        max_traffic = flight["traffic"]

properties = {
    # Chart data
    "data": data,
    # Chart type
    "type": "scattergeo",
    # Keep lines only
    "mode": "lines",
    # Flights display as red lines
    "line": {
        "width": 2,
        "color": "red"
    },
    "layout": {
        # Focus on the USA region
        "geo": {
            "scope": "usa"
        }
    }
}

# Set the proper data source and opacity for each trace
for i, flight in enumerate(flights):
    # lat[trace_index] = "[index_in_data]/lat"
    properties[f"lat[{i+1}]"] = f"{i}/lat"
    # lon[trace_index] = "[index_in_data]/lon"
    properties[f"lon[{i+1}]"] = f"{i}/lon"
    # Set flight opacity (max traffic -> max opacity)
    # Hide legend for all flights
    properties[f"options[{i+1}]"] = {
        "opacity": flight["traffic"]/max_traffic,
        "showlegend": False
    }

# Define the page with chart data
page = f"""<taipy:chart type="{properties['type']}" mode="{properties['mode']}" lat="lat" lon="lon" layout="{properties['layout']}">{properties['data']}</taipy:chart>"""

if __name__ == "__main__":
    ################################################################
    #            Instantiate and run Core service                  #
    ################################################################
    Core().run()

    ################################################################
    #            Manage scenarios and data nodes                   #
    ################################################################
    scenario = tp.create_scenario(scenario_cfg)

    ################################################################
    #            Instantiate and run Gui service                   #
    ################################################################

    Gui(page).run()

