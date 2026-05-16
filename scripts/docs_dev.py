import subprocess

def main():
    subprocess.run(["sphinx-autobuild", ".\docs\\", ".\\build\\"])