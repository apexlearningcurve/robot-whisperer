classifier_prompt = """
# CONTEXT
You will be presented with user query and your job is to classifie the function that will be executed based on user query. 
Function names and explanations:
- move_robot_tcp: move robot tool center point (TCP) to location.
- move_joint: rotate or move specific robot joint.
- get_joint_values: get information about robot joints (eg. angles, position etc.). 

Choose ONLY from the list of functions provided.
Your output MUST BE only function name.
STOP AFTER GIVING FUNCTION NAME

# USER QUERY:
{user_query}
"""

