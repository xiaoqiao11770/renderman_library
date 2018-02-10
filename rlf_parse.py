import re

import rfm.rlf as rlf


class RLookFiles(object):
    def __init__(self, rlf_file):
        self.rlf = rlf_file
        self.scope = rlf.RLFScope()
        self.scope.LoadRlf(rlf_file)
        self.node_types = [
            'Bxdf',
            'Legacybxdf',
            'Pattern',
            'Legacypattern',
            'Displacementpattern',
            'Exclude',
            'Displacement',
            'Light',
            'Lightfilter',
            'Displayfilter',
            'Samplefilter'
        ]

    def shading_groups(self):
        sg_dict = {}
        bindings = self.scope.GetStaticBindings()
        for shape in bindings:
            shape_list = []
            sg = bindings[shape]
            if shape not in shape_list:
                shape_list.append(shape)
            sg_dict[sg] = shape_list
        return sg_dict

    def shader_date(self):
        """
        date = {
            'sg': [
                {
                    'type': '',
                    'name': '',
                    'label': '',
                    'parms': [
                        {
                            'reference': False,
                            'type': '',
                            'name': '',
                            'value': ''
                        },
                    ]
                },
            ]
        }
        """
        date = {}
        inject_payloads = self.scope.GetInjectionPayloads()
        for sg in self.shading_groups():
            sg_list = []
            payload = inject_payloads[sg].get('Payload')
            shader_str_list = re.split(r'"__instanceid" \[.+\]', payload)
            if shader_str_list:
                shader_str_list.pop(-1)
            # pprint(shader_str_list)
            for shader_str in shader_str_list:
                # print shader_str
                type_list = re.findall(r'%s' % '|'.join(self.node_types), shader_str)
                assert type_list, 'Not find shader type.'
                shader_type = type_list[-1]
                shader_dict = re.search(r'"(?P<name>\w+)" "(?P<label>\w+)" (?P<parms>[\s\S]*)',
                                        shader_str).groupdict()
                shader_dict['type'] = shader_type
                shader_parms_str = shader_dict.get('parms')
                # print shader_parms_str
                parms = re.findall(r'"(reference|)\s?(\w+) (\w+)" \[(\d+\.?\d*\s?\d*\.?\d*\s?\d*\.?\d*|".*")\]',
                                   shader_parms_str)
                # ref, parm_type, parm_name, value = parm
                shader_dict['parms'] = parms
                sg_list.append(shader_dict)
            date[sg] = sg_list
        return date

if __name__ == '__main__':
    from pprint import pprint
    rlf_file = 'D:/Project/maya_renderman/renderman/test2/rib/0001/cameraShape1_Final.0001.rlf'
    rf = RLookFiles(rlf_file)
    rib = rf.shader_date()
    pprint(rib)
