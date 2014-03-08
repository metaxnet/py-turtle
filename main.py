#! /usr/bin/python
import Tkinter as TK
import turtle

COMMANDS = [
            ("forward",    turtle.forward,      "qd", "qdime"),\
            ("backward",   turtle.backward,     "ah", "ahvre"),\
            ("right",      turtle.right,        "im", "imine"),\
            ("left",       turtle.left,         "wm", "wmale"),\
            ("goto",       turtle.goto,         "lnqvde"),\
            ("setx",       turtle.setx,         "lrvhb"),\
            ("sety",       turtle.sety,         "lavrK"),\
            ("setheading", turtle.setheading,   "lkivvN"),\
            ("home",       turtle.home,         "ebite"),\
            ("circle",     turtle.circle,       "oigvl"),\
            ("dot",        turtle.dot,          "nqvde"),\
            ("stamp",      turtle.stamp,        "hvtmt"),\
            ("clearstamp", turtle.clearstamp,   "nqe`hvtmt"),\
            ("clearstamps",turtle.clearstamps,  "nqe`hvtmvt"),\
            ("undo",       turtle.undo,         "bul"),\
            ("speed",      turtle.speed,        "meirvt"),\
            ("position",   turtle.position,     "miqvM"),\
            ("towards",    turtle.towards,      "zvvit"),\
            ("xcor",       turtle.xcor,         "rvhb"),\
            ("ycor",       turtle.ycor,         "avrK"),\
            ("heading",    turtle.heading,      "kivvN"),\
            ("distance",   turtle.distance,     "mrhq")]

HEBREW_LATIN = "abgdevzhuiKklMmNnsoFfXxqrwt"

class HebrewHandler:
    def __init__(self, hebrew_latin=HEBREW_LATIN):
        self.dic = self.create_dic(hebrew_latin)

    def create_dic(self, hebrew_latin):
        dic = {}
        for i in range(len(hebrew_latin)):
            dic[hebrew_latin[i]] = unichr(0x5d0+i)
        return dic

    def to_hebrew(self, text):
        out = []
        for c in text:
            if c in self.dic:
                out.append(self.dic[c])
            else:
                out.append(c)
        print [u"".join(out)], text
        return u"".join(out)

class Commander:
    def __init__(self):
        self.HH = HebrewHandler()
        self.movement_commands = {}
        self.commands = {}
        for w in COMMANDS:
           command = w[0]
           function = w[1]
           hebrew = w[2:]
           for h in hebrew:
                hebrew_command = self.HH.to_hebrew(h)
                self.commands[hebrew_command] = (command, function)
           
    def handle_command(self, event):
        text = event.widget.get()
        print type(text)
        words = text.split(u" ")
        print words
        if words[0] in self.commands:
            print self.commands[words[0]][0]
        else:
            print self.commands.keys()

class App:
    def __init__(self):
        self.C = Commander()
        self.root = TK.Tk()
        self.canvas = TK.Canvas(self.root)
        self.canvas.pack()
        self.screen = turtle.TurtleScreen(self.canvas)
        self.text = TK.Text(self.root, height=10)
        self.text.insert("end", "Hello")
        self.text.pack()
        self.entry = TK.Entry(self.root) 
        self.entry.bind("<Key>", self.handle_key)
        self.entry.bind("<Return>", self.C.handle_command) 
        self.entry.pack()
        self.command_string = TK.StringVar() 
        self.command_label = TK.Label(self.root, textvariable=self.command_string)
        self.command_label.pack()
        self.root.mainloop()
    
    def handle_key(self, event):
        text = event.widget.get()
        self.command_string.set(text)
        
a = App()

