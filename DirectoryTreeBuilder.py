def is_cmd(item):
    return(item[0]=='$')

def step_into(item):
    return(item[0:4]=='$ cd' and item[5:]== '..')

def step_out(item):
    return(item=='$ cd ..')

def get_dir_name(item):
    return(item[4:])

def get_cd_name(item):
    return(item[5:])

def is_dir(item):
    return(item[0:3]=='dir')

def is_file(item):
    return(not is_dir(item) and not is_cmd(item))

def get_file_size(item):
    if not is_cmd(item) and not is_dir(item):
        return(int(item[0:item.index(" ")]))

def get_file_name(item):
    return(item[item.index(" ")+1:])

def count_layers(inputlist):
    max_layers = 0
    current_layer = 0
    for item in inputlist:
            
        if item[0:4] == '$ cd' and item != '$ cd ..':
            current_layer += 1
            print(item, current_layer, max_layers)
        elif item == '$ cd ..':
            current_layer -= 1
            print(item, current_layer, max_layers)
        elif item == '$ ls':
            continue
            
        if current_layer > max_layers:
            max_layers += 1

    return(max_layers)

def list_directories(input_list):

    list_of_directories = []
    for item in input_list:
        if item[0:3]=='dir' and item[3:] not in list_of_directories:
            list_of_directories.append(item[3:])

    return(list_of_directories)

def build_tree(input_list):

    tree = {}
    
 
        
def build_dir(working_dir):
    
    global inputs
    global tree #call the entire tree dictionary into this function's local scope
    dir_contents = {}
    position = inputs.index(working_dir)

    i = position + 2
    while not is_cmd(inputs[i]): # iterate thru items until a '$' is reached
        if is_dir(inputs[i]):
            dir_name = get_dir_name(inputs[i])
            dir_contents[dir_name]='' # add the subdir as a key in the dictionary
        elif is_file(inputs[i]):
            file_name = get_file_name(inputs[i])
            file_size = get_file_size(inputs[i])
            dir_contents[file_name]=file_size # add the file name as key in a dictionary and the file size as the value
        i += 1
        
    return(dir_contents) #this function returns a dictionary

def create_dir(level, working_dir, sub_dir):
    if sub_dir in level[working_dir]:
        build_dir(sub_dir)
    else:
        for key in working_dir.keys:
            if sub_dir in key:
                create_dir(key, sub_dir)
            
    


if __name__ == '__main__':
    
    inputs = ['$ cd /','$ ls','dir a','14848514 b.txt','8504156 c.dat','dir d','$ cd a','$ ls','dir e','29116 f','2557 g','62596 h.lst','$ cd e','$ ls','584 i','$ cd ..','$ cd ..','$ cd d','$ ls','4060174 j','8033020 d.log','5626152 d.ext','7214296 k']
    tree = {}
    tree[get_cd_name(inputs[0])] = build_dir(inputs[0])
    print(tree)
    
    working_dir = '/'
    working_dict = tree
    for _input in inputs:
        if (step_into(_input)):
            sub_dir = get_cd_name(_input)
            sub_dict = create_dir(working_dict, working_dir,sub_dir)
            working_dict = sub_dict
            working_dir = get_cd_name(_input)
            
    
