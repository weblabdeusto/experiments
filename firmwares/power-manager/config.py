DEBUG=False

if DEBUG:
    labs = [
        {'name': 'zumoline', 'ip':'weblab.deusto.es', 'path':'/labs/zumoline/test', 'relay':0 ,'lastDown':None},
        {'name': 'fakeLab', 'ip':'weblab.deusto.es', 'path':'/labs/zumoline/test', 'relay': 1,'lastDown': None}
    ]
else:
    labs = [
        {'name': 'zumoline', 'ip':'192.168.0.130', 'path':'/labs/zumoline/test', 'relay':0 ,'lastDown': None}

