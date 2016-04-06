
import subprocess
try:
    result = subprocess.check_output(["sh", "/home/gabi/proyectos/web/test/ardulab/app/scripts/prepareFiles.sh", "3037b2d4-bb35-4ad6-a9c8-daa2f489ae69"], stderr=subprocess.STDOUT)
    print "Success!"

except subprocess.CalledProcessError, ex:
    print "Error 1"
    # error code <> 0
#    return {'current': 100, 'total': 100, 'status': 'Task completed!',
#        'result': "Error preparing files"}


try:
    result = subprocess.check_output(["sh", "/home/gabi/proyectos/web/test/ardulab/app/scripts/build.sh",'leonardo', '3037b2d4-bb35-4ad6-a9c8-daa2f489ae69'], stderr=subprocess.STDOUT)
    print "Success!"

except subprocess.CalledProcessError, ex: # error code <> 0
    print "--------errors------"
    lines = ex.output.split("\n")
    index = 0
    errors = ""
    for line in lines:
        #print line
        if "error" in line:
            errors = errors + line + ";" + lines[index+1] + ";" + lines[index+2]+";"
            print "\t"+line
            print "\t"+lines[index+1]
            print "\t"+lines[index+2]
        if "main" in line:
             print "\t"+line
             errors = errors + line + ";"
        index=index+1

try:
    result = subprocess.check_output(["sh", "/home/gabi/proyectos/web/test/ardulab/app/scripts/moveBinary.sh", "leonardo"], stderr=subprocess.STDOUT)
    print "Success!"

except subprocess.CalledProcessError, ex:
    # error code <> 0
    print "Error 2"

