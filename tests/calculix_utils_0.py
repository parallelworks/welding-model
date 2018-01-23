import re
import warnings
from . import data_IO


def read_setting_from_str(text_line, setting_flag):
    x = re.search(setting_flag, text_line, re.IGNORECASE)
    if x is None:
        warnings.warn('Cannot find \"{}\" in line \"{}\"'.format(setting_flag, text_line))
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
            inp_file, self.set_type + '=' + self.name, ',', end_flag='*')


class ElementSetTest(Set):
    """Stores element set name and element numbers"""
    def __init__(self, name='', members=[]):
        Set.__init__(self, 'ELSET', name, members)


class ElementSet:
    """Stores element set name and element numbers"""
    def __init__(self, name='', elements=[]):
        self.name = name
        self.elements = elements

    def num_elements(self):
        return len(self.elements)

    def read_element_set_name_from_line(self,line):
        self.name = read_setting_from_str(line, 'ELSET=')

    def read_elements_from_inp(self, inp_file):
        self. elements = \
            data_IO.read_ints_from_file_line_offset(inp_file, 'ELSET=' + self.name, ',',
                                                    end_flag='*')


class NodeSet:
    """Stores node set name and node numbers"""
    def __init__(self, name='', nodes=[]):
        self.name = name
        self.nodes = nodes

    def num_nodes(self):
        return len(self.nodes)

    def read_node_set_name_from_line(self, line):
        self.name = read_setting_from_str(line, 'NSET=')

    def read_nodes_from_inp(self, inp_file):
        self. nodes = \
            data_IO.read_ints_from_file_line_offset(inp_file, 'NSET=' + self.name, ',',
                                                    end_flag='*')


def extract_set_from_inp_test(finp):
    finp.seek(0)
    all_lines = finp.readlines()
    line_num = 0
    element_sets = []
    while line_num is not None:
        line_num = data_IO.get_index_in_str_list(all_lines, '*ELSET', start_from=line_num)
        if line_num:
            element_set = ElementSetTest()
            element_set.read_set_name_from_line(all_lines[line_num])
            element_set.read_members_from_inp(finp)
            element_sets.append(element_set)
            line_num = line_num + 1

    return element_sets



def extract_set_from_inp_test(finp):
    finp.seek(0)
    all_lines = finp.readlines()
    line_num = 0
    element_sets = []
    while line_num is not None:
        line_num = data_IO.get_index_in_str_list(all_lines, '*ELSET', start_from=line_num)
        if line_num:
            element_set = ElementSetTest()
            element_set.read_set_name_from_line(all_lines[line_num])
            element_set.read_members_from_inp(finp)
            element_sets.append(element_set)
            line_num = line_num + 1

    return element_sets


def extract_element_sets_from_inp(finp):
    finp.seek(0)
    all_lines = finp.readlines()
    line_num = 0
    element_sets = []
    while line_num is not None:
        line_num = data_IO.get_index_in_str_list(all_lines, '*ELSET', start_from=line_num)
        if line_num:
            element_set = ElementSet()
            element_set.read_element_set_name_from_line(all_lines[line_num])
            element_set.read_elements_from_inp(finp)
            element_sets.append(element_set)
            line_num = line_num + 1

    return element_sets


def extract_node_sets_from_inp(finp):
    finp.seek(0)
    all_lines = finp.readlines()
    line_num = 0
    node_sets = []
    while line_num is not None:
        line_num = data_IO.get_index_in_str_list(all_lines, '*NSET', start_from=line_num)
        if line_num:
            node_set = NodeSet()
            node_set.read_node_set_name_from_line(all_lines[line_num])
            node_set.read_nodes_from_inp(finp)
            node_sets.append(node_set)
            line_num = line_num + 1

    return node_sets


class Mesh:
    """Reads/Stores Node sets and element sets"""
    def __init__(self, element_sets=[], node_sets=[]):
        self.element_set = element_sets
        self.node_set = node_sets
