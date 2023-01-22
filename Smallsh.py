# Author: Dylan Smith
# Description: A conversion of a previous project, Smallsh.c, into Python.
#               Made with guidance from the following tutorial:
#               https://danishpraka.sh/2018/09/27/shell-in-python.html
#               Credit: Danish Prakash

import subprocess
import os


def run_commands(cmd):
    """
    Runs the user's command, piping if necessary
    :param cmd: String, the command to be run
    :return: Integer, the exit value of the successful or failed command
    """
    try:
        if '|' in cmd:
            # Command includes piping, send to pipe_commands()
            status = pipe_commands(cmd)
            return status.returncode
        else:
            # No piping, run command
            status = subprocess.run(cmd, shell=True)
            return status.returncode
    except Exception:
        print("psh: command not found: {}".format(cmd))
        

def pipe_commands(cmd):
    """
    Handles piping for piped commands
    :param cmd: String, the command to be run
    :return: Integer, the exit value of the successful or failed command
    """
    # Save default stdin and stdout to restore when command is done
    stdin = os.dup(0)
    stdout = os.dup(1)
    
    # First command pulled from stdin
    fdin = os.dup(stdin)
    
    for command in cmd.split('|'):
        # Iterate over all piped commands
        os.dup2(fdin, 0)
        os.close(fdin)
        
        if command == cmd.split('|')[-1]:
            # Last command, restore stdout
            fdout = os.dup(stdout)
        else:
            fdin, fdout = os.pipe()
        
        # Redirect stdout to pipe
        os.dup2(fdout, 1)
        os.close(fdout)
        
        try:
            # Run current piped command, tracking exit value
            status = subprocess.run(cmd.strip().split(), shell=True)
        except Exception:
            print("psh: command not found: {}".format(command.strip()))
    
    # Piped commands done, restore stdin and stdout
    os.dup2(stdin, 0)
    os.dup2(stdout, 1)
    os.close(stdin)
    os.close(stdout)
    
    return status
    
        
def change_dir(path):
    """
    Converts path to absolute pathway and changes directory
    :param path: String, the pathway for cd
    :return: None
    """
    try:
        os.chdir(os.path.abspath(path))
    except Exception:
        # File or directory doesn't exist, return error message
        print("cd: no such file or directory: {}".format(path))


if __name__ == '__main__':
    status = 0
    while True:
        # Runs until 'exit' is input
        command = input(': ')
        if command == 'exit':
            # Built in exit command, break loop and end program
            break
        elif command == 'status':
            # Built in status command, returns most recent exit value
            print('Exit value {}'.format(status))
        elif command[:3] == 'cd ':
            # Built in cd command, forwards path to change_dir
            change_dir(command[3:])
        else:
            # Command other than a built-in, send to run_commands()
            status = run_commands(command)
