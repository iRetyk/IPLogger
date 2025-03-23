
import subprocess


spoof_process: subprocess.Popen


def start_spoofing(host_ip: str,target_ip: str,router_ip: str) -> None:
    """
    ths function will start a process that spams spoofed packets.
    """
    subprocess.Popen(["python","spoof.py",host_ip,target_ip,router_ip])


def stop_spoofing() -> None:
    """
    stop spoofing, by killing spoofer process.
    """
    print("Killing spoofer....")
    try:
        spoof_process.kill()
        print("Process killed")
    except:
        print("couldn't kill process")


def main():
    start_spoofing("1","!","2")
    print("Started process....")
    


if __name__ == "__main__":
    main()