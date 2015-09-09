from tkinter import *
import paho.mqtt.client as mqtt

__author__ = 'Niels'


class App:

    def __init__(self, master):
        self.frame = master
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.last_connection = ""
        root.title("MQTT Client")

        label = Label(root, text="MQTT Broker URL")
        label.grid(row=0, column=0, columnspan=2)

        self.connecting_entry = Entry(root)
        self.connecting_entry.grid(row=0, column=2, columnspan=2)

        self.connection_button = Button(root, text="Connect", command=self.connect)
        self.connection_button.grid(row=0, column=4, columnspan=1)

        username_label = Label(root, text="Username")
        username_label.grid(row=1, column=0, columnspan=2)

        self.username_entry = Entry(root)
        self.username_entry.grid(row=1, column=2, columnspan=2)

        password_label = Label(root, text="Password")
        password_label.grid(row=2, column=0, columnspan=2)

        self.password_entry = Entry(root, show="*")
        self.password_entry.grid(row=2, column=2, columnspan=2)

        self.connection_text = StringVar()
        connection_label = Label(root, textvariable=self.connection_text)
        connection_label.grid(row=3, column=0, columnspan=2)

        topic_label = Label(root, text="Subscribe to topic")
        topic_label.grid(row=4, column=0, columnspan=2)

        self.topic_entry = Entry(root, state=DISABLED)
        self.topic_entry.grid(row=4, column=2, columnspan=2)

        self.topic_button = Button(root, text="Subscribe", state=DISABLED, command=self.subscribe)
        self.topic_button.grid(row=4, column=4, columnspan=1)

        self.subscription_list = Listbox(root)
        self.subscription_list.grid(row=5, column=0, columnspan=5, rowspan=2, sticky=W+E+N+S, padx=5, pady=5)

        self.unsubscribe_button = Button(root, text="Unsubscribe", state=DISABLED, command=self.unsubscribe)
        self.unsubscribe_button.grid(row=7, column=0, columnspan=5)

        for i in range(5, 8):
            root.grid_columnconfigure(i, weight=1, uniform="messages")
            root.grid_rowconfigure(i, weight=1, uniform="message_row")

        message_label = Label(root, text="Messages")
        message_label.grid(row=1, column=5, columnspan=3)

        self.message_list = Listbox(root)
        self.message_list.grid(row=2, column=5, columnspan=3, rowspan=6, sticky=W+E+N+S, padx=5, pady=5)

        self.frame.mainloop()

    def connect(self):
        if self.username_entry.get() != "" and self.password_entry.get() != "":
            self.client.username_pw_set(self.username_entry.get(), self.password_entry.get())
            self.username_entry.config(state=DISABLED)
            self.password_entry.config(state=DISABLED)
        url = self.connecting_entry.get()
        if self.last_connection == url:
            self.client.reconnect()
            self.connection_text.set("Connecting...")
            self.connecting_entry.config(state=DISABLED)
            self.connection_button.config(state=DISABLED)
        else:
            if url != "":
                self.client.loop_start()
                self.client.connect(url, 1883, 60)
                self.connection_text.set("Connecting...")
                self.connecting_entry.config(state=DISABLED)
                self.connection_button.config(state=DISABLED)

    def disconnect(self):
        self.client.disconnect()

    def subscribe(self):
        new_sub = True
        for item in self.subscription_list.get(0, END):
            if item == self.topic_entry.get():
                new_sub = False
        if new_sub:
            self.client.subscribe(self.topic_entry.get())
            self.topic_button.config(state=DISABLED)

    def on_connect(self, client, userdata, flags, rc):
        self.connection_text.set("Connected!")
        self.last_connection = self.connecting_entry.get()
        self.topic_button.config(state=NORMAL)
        self.topic_entry.config(state=NORMAL)
        self.connection_button.config(state=NORMAL, text="Disconnect", command=self.disconnect)

    def on_log(self, client, userdata, level, buf):
        print(str(buf))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        if granted_qos[0] != 128:
            self.subscription_list.insert(0, self.topic_entry.get())
            self.topic_entry.config(text="")
        self.topic_button.config(state=NORMAL)
        if self.subscription_list.size() > 0:
            self.unsubscribe_button.config(state=NORMAL)

    def on_message(self, client, userdata, msg):
        self.message_list.insert(0, msg.payload)

    def on_disconnect(self, client, userdata, rc):
        self.frame.destroy()
        self.frame.quit()

    def unsubscribe(self):
        if self.subscription_list.get(ANCHOR) != "":
            self.client.unsubscribe(self.subscription_list.get(ANCHOR))
            self.subscription_list.delete(ANCHOR)
            if self.subscription_list.size() == 0:
                self.unsubscribe_button.config(state=DISABLED)

root = Tk()

app = App(root)
