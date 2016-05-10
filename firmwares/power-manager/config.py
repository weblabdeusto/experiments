DEBUG=True

if DEBUG:
    labs = [
        {'name': 'zumoline', 'ip':'weblab.deusto.es', 'path':'/labs/zumoline/test', 'relay':0 },
        {'name': 'fakeLab', 'ip':'weblab.deusto.es', 'path':'/labs/ardulab/test', 'relay':1 }
    ]
else:
    labs = [
        {'name': 'zumoline', 'ip':'192.168.0.130', 'path':'/labs/zumoline', 'relay':0 }
    ]