import subprocess
import sys

def grid(arg):
    container_name = "wt-selenium-grid"

    cmd_dict = {
        'start':'podman run --name {0} -d --shm-size=2g -p 4444:4444 -p 5999:5999 quay.io/redhatqe/selenium-standalone'.format(container_name),
        'stop':'podman stop {0}'.format(container_name),
        'remove':'podman rm -f {0}'.format(container_name),
        'status': "podman container inspect -f '{{.State.Running}}' "+container_name
    }

    if arg in cmd_dict.keys():
        cmd = cmd_dict[arg].split(" ")
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        if arg == "status":
            if "true" in str(result.stdout):
                print("selenium grid container is up")
            elif "false" in str(result.stdout):
                print("selenium grid container is down, do..\n1. wtrobot grid remove\n2. wtrobot grid start'")
            else:
                print(result.stdout)
        else:
            print(result.stdout)
    else:
        print("Invalid parameter passed, it should be either 'start','stop','remove' or 'status' only")

if __name__ == "__main__":
    grid(sys.argv[1])
