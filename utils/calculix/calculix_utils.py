import re
import warnings
import data_IO


def read_setting_from_str(text_line, setting_flag):
    x = re.search(setting_flag, text_line, re.IGNORECASE)
    if x is None:
        warning_msg = 'Cannot find \"{}\" in line \"{}\"'.format(setting_flag, text_line)
        print(warning_msg)
        warnings.warn(warning_msg)
        return None
    setting = text_line[x.end():].split(',')[0]
    return setting.rstrip()


class Set:
    """Stores set name and members"""
    def __init__(self, set_type, name='', members=[]):
        self.type = set_type
        self.name = name
        self.members = members
        self.set_type = set_type

    def num_members(self):
        return len(self.members)

    def read_set_name_from_line(self, line):
        self.name = read_setting_from_str(line, self.set_type + '=')

    def read_members_from_inp(self, inp_file):
        self. members = data_IO.read_ints_from_file_line_offset(
            inp_file, '*' + self.type + ',' + self.set_type + '=' + self.name,
            delimiter=',', end_flag='*')


class ElementSet(Set):
    """Stores element set name and element numbers"""
    def __init__(self, name='', members=[]):
        Set.__init__(self, 'ELSET', name, members)


class NodeSet(Set):
    """Stores node set name and node numbers"""
    def __init__(self, name='', members=[]):
        Set.__init__(self, 'NSET', name, members)


def extract_sets_from_inp(finp, set_type):
    finp.seek(0)
    all_lines = finp.readlines()
    line_num = 0
    finp_sets = []
    while line_num is not None:
        line_num = data_IO.get_index_in_str_list(all_lines,
                                                 '*' + set_type, start_from=line_num)
        if line_num:
            set = Set(set_type)
            set.read_set_name_from_line(all_lines[line_num])
            set.read_members_from_inp(finp)
            finp_sets.append(set)
            line_num = line_num + 1

    return finp_sets


class Mesh:
    """Reads/Stores Node sets and element sets"""
    def __init__(self, element_sets=[], node_sets=[]):
        self.element_sets = element_sets
        self.node_sets = node_sets

    def read_element_sets_from_inp(self, inp_file):
        fin = data_IO.open_file(inp_file)
        self.element_sets = extract_sets_from_inp(fin, 'ELSET')
        fin.close()

    def read_node_sets_from_inp(self, inp_file):
        fin = data_IO.open_file(inp_file)
        self.node_sets = extract_sets_from_inp(fin, 'NSET')
        fin.close()

    def read_mesh_from_inp(self, inp_file):
        self.read_node_sets_from_inp(inp_file)
        self.read_element_sets_from_inp(inp_file)

    def element_set_names(self):
        return [element_set.name for element_set in self.element_sets]

    def node_set_names(self):
        return [node_set.name for node_set in self.node_sets]

    def num_element_sets(self):
        return len(self.element_sets)

    def num_node_sets(self):
        return len(self.node_sets)

    def num_elements_in_sets(self):
        return [element_set.num_members() for element_set in self.element_sets]

    def num_nodes_in_sets(self):
        return [node_set.num_members() for node_set in self.node_sets]

    def num_all_elements(self):
        num_elements = self.num_elements_in_sets()
        return sum(num_elements)

    def num_all_nodes(self):
        num_nodes = self.num_nodes_in_sets()
        return sum(num_nodes)

    def get_all_elements(self):
        all_elements = []
        for elem_set in self.element_sets:
            all_elements.extend(elem_set.members)
        return all_elements

    def get_all_nodes(self):
        all_nodes = []
        for elem_set in self.node_sets:
            all_nodes.extend(elem_set.members)
        return all_nodes

    def remove_element_set_by_name(self, set_name_2_del):
        names = self.element_set_names()
        set_index = data_IO.get_index_in_str_list(names, set_name_2_del)
        self.element_sets.pop(set_index)

    def remove_node_set_by_name(self, set_name_2_del):
        names = self.node_set_names()
        set_index = data_IO.get_index_in_str_list(names, set_name_2_del)
        self.node_sets.pop(set_index)


class WeldPasses:
    """Reads and stores the weld pass coordinate information"""
    def __init__(self, pass_coor_path):
        self.pass_coor_path = pass_coor_path
        self.read_num_layers_from_pass_coor_file()
        self.read_passes_from_pass_coor_file()

    def read_num_layers_from_pass_coor_file(self):
        fcp = data_IO.open_file(self.pass_coor_path)

        # First get the number of layers:
        num_layers = data_IO.read_int_from_file_line_offset(fcp,'Number-of-Layers')
        fcp.close()
        self.num_layers = num_layers

    def read_passes_from_pass_coor_file(self):
        fcp = data_IO.open_file(self.pass_coor_path)
        # Then, read the passes in each layer
        num_passes = 0
        for layer in range(self.num_layers):
            data = data_IO.read_ints_from_file_line_offset(fcp,'Layer,Number-of-Passes',
                                                           delimiter=',', offset=layer,
                                                           end_line=1)
            num_passes = num_passes + data[1]
        fcp.close()
        self.num_passes = num_passes


def read_uncoupled_step_time_from_inp(inp_file_path):
    """Read time period of UNCOUPLED TEMPERATURE-DISPLACEMENT steps from ccx input file"""

    finp = data_IO.open_file(inp_file_path)
    lines = finp.readlines()
    finp.close()

    line_num = 0
    times = []
    while line_num is not None:
        line_num = data_IO.get_index_in_str_list(lines,
                                                 'UNCOUPLED TEMPERATURE-DISPLACEMENT',
                                                 start_from=line_num)
        if line_num is not None:
            times.append(data_IO.read_floats_from_string(lines[line_num+1], ',')[1])
            line_num = line_num + 1

    return times
