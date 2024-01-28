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

# JSON PARAMETER VALUES
- functions: This is an array that represents all the function calls needed to perform the actions requested buy the USER QUERY. The structure of each function is defined below. These
functions are separated in the USER QUERY by words like "and", "then" ... you need to fill the array using all the actions defined by the USER QUERY while respectiong all the rules defined below.
- function_name: Which function does the robot need to perform. Can be only one of these: move_tcp, move_joint, get_joint_values
- input_name: Input parameter name for the function. Every function has a defined set of input parameters, what they mean, how they are named and what type of value they can be.
- input_value: The value of the previously mentioned function input parameter. It's type is defined within the function explaination
- inputs: An array of input_name, input_value pairs. One inputs array defines all the input parameters for a function call. This array must be complete according to the definition of the chosen function_name 

# FUNCTION MEANING
- move_tcp: Moves the robot's tool center point (TCP). This function takes as inputs: x, y, z, q1, q2, q3, q4
x, y ,z can only have number values, they represent the desired position of the TCP for each axis and are expressed in milimeters, this unit is implicit. Example: "Move TCP to the right by 0.1m" results in input_name: x and input_value: 10 
q1, q2, q3, q4 can only have number values and represent the quaternion value of the TCP orientation, defalut should be the TCP pointing down with it's z axis 
- move_joint: Rotates or moves a specific robot joint. This funciton takes as inputs joint, angle 
joint is the index of the joint that needs to rotate. Joints are indext 0, 1, 2 ... The joint 0 is also often reffered to as "base joint", "robot base" or just "base"
angle is the amount the specified joint needs to rotate and is expressed in radians
Example: "Rotate the third joint by 90 degrees." results in joint: 2 angle: 1.5708
- get_joint_values: Retrieves current status of the robot's joints. This function takes no input parameters! Example: "What is the position of the fifth joint?"

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
split_actions = """
<s>[INST]
# TASK DESCRIPTION
You are to analyze user queries regarding industrial robotic operations and translate these into specific function calls. Your role is to bridge human instructions and the technical execution of a robot.
You will extract the information and values from the USER QUERY and form a JSON output which will represent a list of actions, you will fill in the JSON 
with the necessary information. 

# JSON PARAMETER VALUES
- actions: an array of action, action_description pairs
- action: name of the action to be performed by the robot, it can only have values: move_tcp, move_joint, get_joint_values
- action_description: the part of the USER QUERY that describes this action

# ACTION MEANING
- move_tcp: Moves the robot's tool center point (TCP). This function takes as inputs: x, y, z, q1, q2, q3, q4
x, y ,z can only have number values, they represent the desired position of the TCP for each axis and are expressed in milimeters, this unit is implicit.
q1, q2, q3, q4 can only have number values and represent the quaternion value of the TCP orientation
- move_joint: Rotates or moves a specific robot joint. This funciton takes as inputs joint, angle 
joint is the index of the joint that needs to rotate. Joints are indext 0, 1, 2 ... The joint 0 is also often reffered to as "base joint", "robot base" or just "base"
angle is the amount the specified joint needs to rotate and is expressed in radians
- get_joint_values: Retrieves current status of the robot's joints. This function takes no input parameters! Example: "What is the position of the fifth joint?"


USER QUERY: {user_query}
[/INST]
"""
# TODO: We shouldn't provide formatting instructions, this is is jsonformer's responsibility
# prompt template <s>[INST] {prompt} [/INST]

# TODO: Functions that require movement can be expressed as relative or absolute positions, find a way to include this information and act accordingly

# TODO: Change joint angels to be joints in list and angles in list
if __name__ == "__main__":
    import json

    with open("./LLM/prompts.json", "w", encoding="utf-8") as file:
        json.dump([{"classifier_prompt": classifier_prompt}], file)
