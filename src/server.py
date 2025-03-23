
import subprocess
import time

spoof_process: subprocess.Popen


def start_spoofing(host_ip: str,target_ip: str,router_ip: str) -> None:
    """
    ths function will start a process that spams spoofed packets.
    """
    global spoof_process
    spoof_process = subprocess.Popen(["python","spoof.py",host_ip,target_ip,router_ip])


def stop_spoofing() -> None:
    """
    stop spoofing, by killing spoofer process.
    """
    print("Killing spoofer....")
    try:
        spoof_process.terminate()
        time.sleep(0.5)
        print("Process killed")
    except Exception as e:
        print("couldn't kill process")
        print(str(e))


def main():
    start_spoofing("1","!","2")
    print("Started process....")
    time.sleep(6)
    stop_spoofing()


if __name__ == "__main__":
    main()