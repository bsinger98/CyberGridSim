from Simulator.PowerFlowCase import PowerFlowCase


def ppt_attack(power_flow_case: PowerFlowCase, gens_to_turn_off):
    for gen_to_turn_off in gens_to_turn_off:
        # Turn off settings in data
        for gen in power_flow_case.generators:
            if gen_to_turn_off == gen.id:
                gen.status = 0
                gen.active = False

        # Remove from active generators list
        for i, gen in enumerate(power_flow_case.active_generators):
            if gen_to_turn_off == gen.id:
                del power_flow_case.active_generators[i]


def highest_ppt_attack(powerflow_case: PowerFlowCase, number_of_gens_to_turn_off, gen_offset=10):
    # Sort generators by highest power
    sorted_gens = sorted(powerflow_case.active_generators, key=lambda gen: gen.Pg, reverse=True)

    # TODO ignore slack generator
    # Select generator ids
    gen_contingencies = []
    for gen_to_turn_off in sorted_gens[gen_offset:number_of_gens_to_turn_off+gen_offset]:
        gen_contingencies.append(gen_to_turn_off.id)

    # Turn them off in powerflow case
    ppt_attack(powerflow_case, gen_contingencies)
