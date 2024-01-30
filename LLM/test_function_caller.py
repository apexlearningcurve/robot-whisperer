import json

from LLM.function_caller import FunctionCaller

user_query_tests = [
    "Move robot tcp left for 1000mm",
    "Move robot sixth joint for 30 degrees left",
    "Give me robot joint info",
    "Tell me info about robot",
    "Rotate robot base for 45 and move TCP along x axis for 50 milimeters.",
    "Rotate joint 2 for 30 and joint 7 for 45 degrees then joint 2 40 degrees",
]

if __name__ == "__main__":
    fn_caller = FunctionCaller()
    for query in user_query_tests:
        fn_call = fn_caller.generate(query)
        print(json.dumps(fn_call, indent=4))
