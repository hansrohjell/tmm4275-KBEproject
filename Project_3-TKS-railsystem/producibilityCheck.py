def producibilityCheck(params):
    variable_range = {
        "seat_depth": [35, 55],
        "chair_width": [30, 50],
        "back_height": [40, 60],
        "leg_side": [1, 10],
        "seat_height": [35, 55],
    }
    not_producible = False
    error_message = {}
    for param_pair in params:
        param = param_pair[0]
        value = float(param_pair[1])
        min_value = variable_range[param][0]
        max_value = variable_range[param][1]
        if value < min_value or value > max_value:
            not_producible = True
            error_message[param] = [" Please insert a value between " +
                                    str(round(min_value)) + " and " + str(round(max_value)), value]
    return not_producible, error_message