from Simulator.PowerFlowCase import PowerFlowCase


def calculate_generator_ramp_limits(powerflow_case, droop_ramp=0.05, agc_ramp=0.1, agc_gens=None, rrg_gens=None,
                                    enable_droop_limit=True, ignore_gen_boundaries=False):
    generators = powerflow_case.active_generators

    # calculate ramp limits for all generators
    ramp_low_limits = {}
    ramp_high_limits = {}
    agc_load_max = 0
    agc_load_min = 0
    droop_load_max = 0
    droop_load_min = 0
    reserve_load_max = 0
    reserve_load_min = 0
    for generator in generators:
        if enable_droop_limit:
            # Reserve generators are not limited at all
            if generator.id in rrg_gens:
                low_limit = 0
                high_limit = generator.Pmax
            # AGC and droop limited by their ramps limit assumptions
            elif generator.id in agc_gens:
                low_limit = generator.Pg - (generator.Pg * agc_ramp)
                high_limit = generator.Pg + (generator.Pg * agc_ramp)
            else:
                low_limit = generator.Pg - (generator.Pg * droop_ramp)
                high_limit = generator.Pg + (generator.Pg * droop_ramp)
        else:
            low_limit = generator.Pmin
            high_limit = generator.Pmax

        if ignore_gen_boundaries:
            # If under 20MW not participating in droop so you can ignore
            if generator.Pmax < powerflow_case.convert_mw_to_base(20):
                if low_limit < generator.Pmin:
                    low_limit = generator.Pmin
                if high_limit > generator.Pmax:
                    high_limit = generator.Pmax
        else:
            if generator.id not in rrg_gens and generator.id not in agc_gens:
                # Cap ramp limit at generator boundaries if disabled
                if low_limit < generator.Pmin:
                    low_limit = generator.Pmin
                if high_limit > generator.Pmax:
                    high_limit = generator.Pmax

        # Always cap low limit at 0
        if low_limit < 0:
            low_limit = 0

        # Polish grid has generators with P below their low limit, for these just ignore because it is unclear what to do
        if high_limit < low_limit:
            high_limit = generator.Pg
            low_limit = generator.Pg

        ramp_low_limits[generator.id] = low_limit
        ramp_high_limits[generator.id] = high_limit

        # Store total reserve generation
        if generator.id in rrg_gens:
            reserve_load_max += high_limit - generator.Pg
            reserve_load_min += generator.Pg - low_limit
        elif generator.id in agc_gens:
            agc_load_max += high_limit - generator.Pg
            agc_load_min += generator.Pg - low_limit
        else:
            droop_load_max += high_limit - generator.Pg
            droop_load_min += generator.Pg - low_limit

    return ramp_low_limits, ramp_high_limits


# Default Settings
# Generators under 100 MW 5% reserve (No AGC)
# Generators over 100 MW 10% reserve (AGC)
def add_reserve_generation(powerflow_case: PowerFlowCase, total_load_change,
                                         enable_droop_limit=True,
                                         ignore_gen_boundaries=False,
                                         droop_ramp=.05,
                                         agc_ramp=0.1,
                                         agc_gens=[]):
    """
    :param powerflow_case: The powerflow case to adjust simulate reserves on
    :param total_load_change: The change in load (MW) to simulate reserves for
    :param enable_droop_limit: If true, limit droop based on the droop ramp
    :param ignore_gen_boundaries: If true, ignore generator power limits
    :param droop_ramp: The change in generation allowed from droop. For example, if 5%,
    allow droop generators to change within 5% of power output
    :param agc_ramp: The change in geenration from agc
    :param agc_gens: TODO
    :return:
    """
    # Calculate limits of all generators
    ramp_low_limits, ramp_high_limits = calculate_generator_ramp_limits(powerflow_case, droop_ramp,
                                                                        agc_ramp, agc_gens=[], rrg_gens=[],
                                                                        enable_droop_limit=enable_droop_limit,
                                                                        ignore_gen_boundaries=ignore_gen_boundaries)
    # Distribute the load change evenly based on generator size and limit
    total_generation_change = 0.0
    load_remaining = True
    # Convert total_load_change to case's units
    total_load_change = powerflow_case.convert_mw_to_base(total_load_change)
    while load_remaining:
        load_change_previous = total_load_change

        # Calculate sum of maximum available power
        max_power_sum = 0.0
        for generator in powerflow_case.active_generators:
            ramp_low_limit = ramp_low_limits[generator.id]
            ramp_high_limit = ramp_high_limits[generator.id]

            # Only sum non-full generators
            if generator.Pg < ramp_high_limit:
                max_power_sum += ramp_high_limit

        # Change power proportional to their pmax
        if max_power_sum != 0:
            for generator in powerflow_case.active_generators:
                ramp_low_limit = ramp_low_limits[generator.id]
                ramp_high_limit = ramp_high_limits[generator.id]

                # Skip if generator is at capacity
                if generator.Pg >= ramp_high_limit:
                    continue

                # Figure out proportional share
                delta_P = (ramp_high_limit / max_power_sum) * total_load_change

                if generator.Pg + delta_P < ramp_low_limit:
                    delta_P = ramp_low_limit - generator.Pg
                    generator.Pg = ramp_low_limit
                elif generator.Pg + delta_P > ramp_high_limit:
                    delta_P = ramp_high_limit - generator.Pg
                    generator.Pg = ramp_high_limit
                else:
                    generator.Pg += delta_P

                total_load_change -= delta_P
                total_generation_change += delta_P

        if abs(total_load_change) <= 0.01 or total_load_change == load_change_previous:
            load_remaining = False

    return powerflow_case.convert_base_to_mw(total_generation_change)
