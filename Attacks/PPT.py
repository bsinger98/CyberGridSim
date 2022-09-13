from Simulator import PowerFlowCase, ReserveGeneration


def ppt_attack(power_flow_case: PowerFlowCase, gens_to_turn_off, reserve_adder: ReserveGeneration):
    power_lost = 0

    for gen_to_turn_off in gens_to_turn_off:
        # Turn off settings in data
        for gen in power_flow_case.generators:
            if gen_to_turn_off == gen.gen_id:
                power_lost += gen.Pg
                gen.status = 0
                gen.active = False

        # Remove from active generators list
        for i, gen in enumerate(power_flow_case.active_generators):
            if gen_to_turn_off == gen.gen_id:
                del power_flow_case.active_generators[i]

    # Adjust generation to handle lost load
    gen_added = reserve_adder.add_reserve_generation(power_flow_case, power_lost)
    return


def highest_ppt_attack(powerflow_case: PowerFlowCase, reserve_adder: ReserveGeneration, number_of_gens_to_turn_off,
                       gen_offset=10):
    # Sort generators by highest power
    sorted_gens = sorted(powerflow_case.active_generators, key=lambda gen: gen.Pg, reverse=True)

    # TODO ignore slack generator
    # Select generator ids
    gen_contingencies = []
    for gen_to_turn_off in sorted_gens[gen_offset:number_of_gens_to_turn_off + gen_offset]:
        gen_contingencies.append(gen_to_turn_off.gen_id)

    # Turn them off in powerflow case
    ppt_attack(powerflow_case, gen_contingencies, reserve_adder)
