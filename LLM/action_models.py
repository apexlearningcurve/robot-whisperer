choose_function = {
    "type": "object",
    "properties": {
        "function_name": {"type": "array", "items": {"type": "string"}},
    },
}
generic_function = {
    "type": "object",
    "properties": {
        "functions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "function_name": {"type": "string"},
                    "inputs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "input_name": {
                                    "type": "string",
                                },
                                "input_value": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    },
}
action_list = {
    "type": "object",
    "properties": {
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "action_description": {"type": "string"},
                },
            },
        }
    },
}
