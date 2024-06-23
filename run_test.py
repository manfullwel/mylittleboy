import subprocess

def run_tests():
    subprocess.run(["pytest", "--disable-warnings", "--maxfail=1"])
    subprocess.run(["coverage", "run", "-m", "pytest"])
    subprocess.run(["coverage", "report", "-m"])

if __name__ == "__main__":
    run_tests()
