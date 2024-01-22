# TODO: export function list definition to json
classifier_prompt = """
<s>[INST]
# TASK DESCRIPTION
Analyze user queries related to robotic operations/tasks and determine the necessary functions to execute these operations. Each query involves actions to be performed by a robotic system.

# FUNCTION LIST
- move_tcp: Moves the robot's tool center point (TCP) to a specified location or along specified axis (eg. x, y, z axis).
- move_joint: Rotates or moves a specific robot joint/base/motor/actuator.
- get_joint_values: Retrieves information about the robot's joints (e.g., angles, positions).

# RESPONSE FORMAT
- Answer in the form of a LIST of function names.
- Only include function names from the provided list.
- For a single function requirement, list only one. 
- For multiple functions, list all that apply.
- A function may appear multiple times in the list if the query calls for its repeated use.
- Preserve the sequence of functions as they appear in the query.
- Do not add any function not explicitly required by the query.

# ADDITIONAL RESTRICTIONS
- Avoid assumptions: If the query lacks clear information, do not infer or guess.
- Be precise: Ensure the functions match the specific actions requested in the query.
- Ignore irrelevant details: Focus only on details that directly influence function choice.

# GUIDANCE
- Pay close attention to action verbs and technical terms in the query, as they often indicate required functions.
- If a query involves movement or rotation not specified by 'TCP' or a 'joint', do not select any function.
- In cases of compound queries (multiple actions), break down each action to decide the appropriate function.
- "base" is same as first robot "joint".

# EXAMPLES

1. USER QUERY: "Move the TCP 100 millimeters along the y-axis."
   RESPONSE: [move_tcp]

2. USER QUERY: "Move the TCP 73 millimeters along the negative y-axis, then rotate the last robot joint by 90 degrees."
   RESPONSE: [move_tcp, move_joint]

3. USER QUERY: "What are the current angles of the robot's joints?"
   RESPONSE: [get_joint_values]

4. USER QUERY: "Move robot base for -30 degrees then move fifth joint for 120"
   RESPONSE: [move_joint, move_joint]

5. USER QUERY: {user_query}
   RESPONSE: 
[/INST]
"""
classifier_prompt_1 = """
<s>[INST]
# TASK DESCRIPTION
You are to analyze user queries regarding industrial robotic operations and translate these into specific function calls. Your role is to bridge human instructions and the technical execution of a robot.
You will extract the information and values from the USER QUERY and form a JSON output which will represent a fuction call, you will fill in the JSON 
with the necessary information. 

# FUNCTION LIST
- move_tcp: Moves the robot's tool center point (TCP). Example: "Move TCP to the right by 50mm."
- move_joint: Rotates or moves a specific robot joint. Example: "Rotate the third joint by 90 degrees."
- get_joint_values: Retrieves current status of the robot's joints. Example: "What is the position of the fifth joint?"

# RESPONSE FORMAT
- Include only the necessary functions directly implied by the query.
- Maintain the order of functions as implied by the sequence of actions in the query.
- In case of ambiguity, provide the most likely function while noting the uncertainty.

# ADDITIONAL GUIDANCE
- Focus on the verbs and technical terms in the query to determine the appropriate function.
- If a query involves actions not covered by the functions, such as maintenance requests, indicate that the query falls outside the function list.
- Consider the practical aspects of robotic operations when interpreting instructions.
- Treat "base" as equivalent to the first robot "joint".

USER QUERY: {user_query}
[/INST]
"""
# TODO: We shouldn't provide formatting instructions, this is is jsonformer's responsibility
# prompt template <s>[INST] {prompt} [/INST]


if __name__ == "__main__":
    import json

    with open("./LLM/prompts.json", "w", encoding="utf-8") as file:
        json.dump([{"classifier_prompt": classifier_prompt}], file)
