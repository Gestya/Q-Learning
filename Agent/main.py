import threading
from future.moves import tkinter

# My stuff
from agent import Agent
from msgqueue import MsgQueue
from server import Server
from ui import UI


def server_thread(msg_queue):
    Server(msg_queue)


def main():
    # Message queue is an argument for both server and agent
    msg_queue = MsgQueue()

    # Agent
    stop_flag = threading.Event()
    agent = Agent(msg_queue, stop_flag)
    agent.start()   # <== stop_flag.set()

    # WS-Server
    server_thread_handler = threading.Thread(target=server_thread, args=(msg_queue,))
    server_thread_handler.daemon = True
    server_thread_handler.start()

    # UI
    window = tkinter.Tk()
    window.geometry('920x860+10+10')
    window.title('Q-Learning :: Agent')
    ui = UI(window, agent)
    while True:
        ui.update()
        window.update_idletasks()
        window.update()


if __name__ == '__main__':
    main()
