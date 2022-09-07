from Simulator.PowerFlowCase import PowerFlowCase


def turn_off_buses(powerflow_case: PowerFlowCase, buses_to_turn_off):
    # Find the indexes for the buses to turn off
    bus_indexes = []
    for bus_to_turn_off in buses_to_turn_off:
        for index, bus in enumerate(powerflow_case.buses):
            if bus.bus_number == bus_to_turn_off:
                bus_indexes.append(index)
                break

    # Remove buses from powerflow case
    parsed_buses = [bus for i, bus in enumerate(powerflow_case.buses) if i not in bus_indexes]
    powerflow_case.buses = parsed_buses

    # Refresh powerflow case because you modified bus values
    powerflow_case.refresh()
