
def get_from_list(filename):
    with open(filename, 'r') as f:
        file_content = f.readlines()

    file_content.sort()
    final_list = []
    for element in file_content:
        display_name = element.strip()
        fl_element = [display_name, display_name.lower().replace(' ', '+')]
        final_list.append(fl_element)

    return final_list

def get_cuisines():
    '''
    Return a list of pairs, where index 0 is the name that will be displayed
    to the user and index 1 will be the value passed in the form.
    '''
    return get_from_list("diet_optimizer_website/lists/cuisines")


def get_foodgroups():
    '''
    Return a list of pairs, where index 0 is the name that will be displayed
    to the user and index 1 will be the value passed in the form.
    '''
    return get_from_list("diet_optimizer_website/lists/food_groups")
