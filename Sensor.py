from Publisher import Publisher
import tkinter as tk
import random, time, threading

stop = False
sensor = None

def connect_server(args, window):
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
    global sensor
    sensor = Sensor(topic, host, port)
    try:
        args['button']['state'] = 'disabled'
        sensor.connect(host, port)
        sensor.close()        
        sensor.subscribe_publisher(topic)
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
    try:
        initial = int(args['initial'].get())
    except Exception as e:
        args['info']['fg'] = 'red'
        args['info']['text'] = 'Initial value must be a number...'
        return
    args['start']['state'] = 'disabled'
    args['stop']['state'] = 'normal'
    global sensor
    args['info']['fg'] = 'green'
    args['info']['text'] = 'Sensor is publishing...'
    threading.Thread(target=publishing, args=(time, initial, sensor)).start()

def publishing(sleep_time, starting_value, sensor):
    sensor.publish({'message': starting_value})
    time.sleep(sleep_time)
    global stop
    stop = False
    while not stop:
        sensor.publish({'message': random.randint(20, 40)})
        time.sleep(sleep_time)

def stop_publishing(args, window):
    args['info']['fg'] = 'red'
    args['info']['text'] = 'Stopping sensor from publishing...'
    global stop
    stop = True
    while len(threading.enumerate()) > 1:
        for t in threading.enumerate():
            if t.name != 'MainThread':
                t.join(0.1)

    args['info']['fg'] = 'green'
    args['info']['text'] = 'Stopped'
    args['stop']['state'] = 'disabled'
    args['start']['state'] = 'normal'

class Sensor(Publisher):
    def __init__(self, topic, host, port):
        super().__init__(topic, host, port)   

class Sensor_Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, 'Internet of Things - Sensor')
        tk.Tk.geometry(self, '500x350')
        tk.Tk.iconbitmap(self,default='sensor.ico') 
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

        initial_value_label = tk.Label(self, text="Initial Value: ")
        initial_value = tk.Entry(self,width=10)

        time_value_label = tk.Label(self, text="Time Interval: ")
        time_value = tk.Entry(self,width=10)

        start = tk.Button(self, text="Publish", fg='green')
        stop = tk.Button(self, text="Stop", state='disabled', fg='red')

        subscribed_topic_label.place(height=50, x=95, y=85)
        self.subscribed_topic.place(height=20, x=250,y=100)

        initial_value_label.place(height=50, x=151, y=125)
        initial_value.place(height=20, x=250, y=140)

        time_value_label.place(height=50, x=151, y=165)
        time_value.place(height=20, x=250, y=180)

        start.place(height=20, x=250, y=220)
        stop.place(height=20, x=200, y=220)

        info = tk.Label(self, text="", fg="red")
        info.place(height=20, x=200, y=300)

        data = {'stop': stop, 'start': start, 'time': time_value, 'initial': initial_value,'info': info}
        start['command'] = lambda: verify(data, controller)
        stop['command'] = lambda: stop_publishing(data, controller)
    def set_values(self):
        global sensor
        self.subscribed_topic['text'] = sensor.topic

window = Sensor_Application()
window.mainloop()