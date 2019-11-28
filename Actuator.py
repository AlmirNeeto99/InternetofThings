from Subscriber import Subscriber
import time, threading, json
import tkinter as tk

stop = False # global variable to save actuator state...
actuator = None # global variable to keep actuator instance

def connect_server(args, window):
    # Check if every data typed by user is correct... 
    try:
        port = int(args['port'].get())
    except Exception:
        args['error']['text'] = 'Port field must be a number...'
        return
    host = args['host'].get()
    topic = args['topic'].get()
    if len(host.split(' ')) != 1 or len(host) == 0:
        args['error']['text'] = 'You must specify a host...'
        return
    if len(topic.split(' ')) != 1 or len(topic) == 0:
        args['error']['text'] = 'You must specify a topic to subscribe...'
        return
    args['error']['fg'] = 'green'
    args['error']['text'] = 'Trying to connect to server...'
    global actuator
    # Create an actuator
    actuator = Actuator(topic, host, port)
    try:
        args['button']['state'] = 'disabled'
        # Try to connect to server...
        # If succeed, subscribe actuator to the topic
        actuator.connect(host, port)
        actuator.close()        
        actuator.subscribe_subscriber()
        window.frames[second_screen].set_values()
        window.show_frame(second_screen)
    except Exception as e:
        args['button']['state'] = 'normal'        
        print(e)
        args['error']['fg'] = 'red'
        args['error']['text'] = 'Couldn\'t connect to server...'

def verify(args, window):
    try:
        time = int(args['time'].get())
    except Exception as e:
        args['info']['fg'] = 'red'
        args['info']['text'] = 'Time value must be a number...'
        return
    args['start']['state'] = 'disabled'
    args['stop']['state'] = 'normal'
    global actuator
    args['info']['fg'] = 'green'
    args['info']['text'] = 'Actuator is reading messages...'
    # Start a thread to read messages from server...
    threading.Thread(target=reading, args=(time, actuator, args)).start()

def reading(sleep_time, actuator, args):
    """If the server is unreachable, try to connect again and again..."""
    while True:               
        try:
            status = actuator.start_receiving()
            message = actuator.receive()
            break # If the actuator reads the first message successfully, stop the loop...
        except Exception as e:
            time.sleep(sleep_time)
            continue
    time.sleep(sleep_time)
    global stop
    stop = False
    while True:
        # If the actuator is not stopped, read data every time, based on time typed on GUI...
        if not stop:
            try:
                command = actuator.receive()
                data = json.loads(command)
                command = data['command']
            except Exception as e:
                time.sleep(sleep_time) 
                continue
            if command == 'stop':
                stop = True
                args['info']['fg'] = 'red'
                args['info']['text'] = 'Stopping actuator from reading...'
                args['info']['fg'] = 'green'
                args['info']['text'] = 'Stopped'
                args['stop']['state'] = 'disabled'
                args['start']['state'] = 'normal'
        # If the actuator is stopped, ask the server if someone make him start again...
        # Or if someone press 'receive' button on GUI.
        else:
            try:
                status = actuator.get_status()
            except Exception as e:
                time.sleep(sleep_time) 
                continue            
            if status != 'stop':
                stop = False
                args['info']['fg'] = 'green'
                args['info']['text'] = 'Actuator is reading...'
                args['stop']['state'] = 'normal'
                args['start']['state'] = 'disabled'
        time.sleep(sleep_time) 
def stop_reading(args, window):
    global actuator
    args['info']['fg'] = 'red'
    args['info']['text'] = 'Stopping actuator from receiving...'
    global stop
    stop = True
    """ Try to stop reading from server... If server is unreachable, try again, till it connects """
    #Tell the server, this sensor will stop sending data.
    while True:
        try:
            status = actuator.stop_receiving()
            break
        except Exception as e:
            time.sleep(5) 
            continue

    args['info']['fg'] = 'green'
    args['info']['text'] = 'Stopped'
    args['stop']['state'] = 'disabled'
    args['start']['state'] = 'normal'

class Actuator_Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, 'Internet of Things - Actuator')
        tk.Tk.geometry(self, '500x350')
        #tk.Tk.iconbitmap(self,default='actuator.ico') 
        tk.Tk.resizable(self, False, False)
        container = tk.Frame(self)        

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}

        for F in (first_screen, second_screen):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(first_screen)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class first_screen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        host = tk.Label(self, text="Host", width=10)
        host_txt = tk.Entry(self,width=10)

        port = tk.Label(self, text="Port")
        port_txt = tk.Entry(self,width=10)

        topic = tk.Label(self, text="Topic")
        topic_txt = tk.Entry(self,width=10)

        host.place(height=50, x=183, y=85)
        host_txt.place(height=20, x=250,y=100)
        host_txt.focus()

        port.place(height=50, x=205, y=135)
        port_txt.place(height=20, x=250, y=150)

        topic.place(height=50, x=205, y=185)
        topic_txt.place(height=20, x=250, y=200)

        error = tk.Label(self, text="", fg="red")
        error.place(height=20, x=200, y=300)        
        
        start = tk.Button(self, text="Subscribe and Connect")
        data = {'topic': topic_txt, 'port': port_txt, 'host': host_txt, 'error': error, 'button': start}
        start['command'] = lambda: connect_server(data, controller)
        start.place(height=20, x=200, y=250)

class second_screen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.sensor = ""
        subscribed_topic_label = tk.Label(self, text="Subscribed Topic: ", width=30)
        self.subscribed_topic = tk.Label(self,width=10, text='')

        time_value_label = tk.Label(self, text="Time Interval: ")
        time_value = tk.Entry(self,width=10)

        start = tk.Button(self, text="Read", fg='green')
        stop = tk.Button(self, text="Stop", state='disabled', fg='red')

        subscribed_topic_label.place(height=50, x=95, y=85)
        self.subscribed_topic.place(height=20, x=250,y=100)

        time_value_label.place(height=50, x=151, y=125)
        time_value.place(height=20, x=250, y=140)

        start.place(height=20, x=250, y=180)
        stop.place(height=20, x=200, y=180)

        info = tk.Label(self, text="", fg="red")
        info.place(height=20, x=200, y=300)

        data = {'stop': stop, 'start': start, 'time': time_value,'info': info}
        start['command'] = lambda: verify(data, controller)
        stop['command'] = lambda: stop_reading(data, controller)
    def set_values(self):
        global actuator
        self.subscribed_topic['text'] = actuator.topic

class Actuator(Subscriber):
    def __init__(self, topic, host, port):
        super().__init__(host, port, topic)

window = Actuator_Application()
window.mainloop()