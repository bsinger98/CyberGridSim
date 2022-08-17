def MadIoT_attack(power_flow_case, load_factor):
    load_change = 0
    for load in power_flow_case.loads:
        # return load change in MW
        load_change += load.Pd * load_factor - load.Pd
        load.Pd *= load_factor

    return power_flow_case.convert_base_to_mw(load_change)
