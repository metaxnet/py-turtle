#!/usr/bin/env python2.7

import turtle
import math, random, copy
import pygtk
pygtk.require('2.0')
import gtk

COMMANDS = [
            (["home"],               ["ebite"]),\
            (["wrap"],               ["mxb`kdvr"]),\
            (["window"],             ["mxb`hlvn"]),\
            (["fence"],              ["mxb`jdr"]),\
            (["clearscreen", "cs"],  ["nqe`msK"]),\
            (["clean"],              ["nqe"]),\
            (["penup", "pu"],        ["erM`ou","erMou"]),\
            (["pendown", "pd"],      ["ewrd`ou","ewrdou"]),\
            (["penreverse", "px"],   ["efwK`ou","efwKou"]),\
            (["showturtle", "st"],   ["exg`xb","exgxb"]),\
            (["hideturtle", "ht"],   ["estr`xb","estrxb"]),\
            (["forward", "fd"],      ["qd", "qdime"]),\
            (["backward", "bk"],     ["ah", "ahvre"]),\
            (["right", "rt"],        ["im", "imine"]),\
            (["left", "lt"],         ["wm", "wmale"]),\
            (["setpensize"],         ["qbo`gvdl`ou"]),\
            (["print", "pr"],        ["edfs", "ed"]),\
            (["random"],             ["egrl"]),\
            (["first"],              ["rawvn"]),\
            (["butfirst"],           ["la`rawvn"]),\
            (["last"],               ["ahrvn"]),\
            (["butlast"],            ["la`ahrvn"]),\
            (["pick"],               ["wlvF"]),\
            (["sin"],                ["sinvs"]),\
            (["cos"],                ["qvsinvs"]),\
            (["arctan"],             ["ungns"]),\
            (["int"],                ["wlM"]),\
            (["minus"],              ["minvs"]),\
            (["remainder"],          ["warit"]),\
            (["power"],              ["hzqe"]),\
            (["sqrt"],               ["wvrw"]),\
            (["for"],                ["lkl"]),\
            (["goto"],               ["lnqvde"]),\
            (["setx"],               ["lrvhb"]),\
            (["sety"],               ["lavrK"]),\
            (["setxy"],              ["lnqvde"]),\
            (["setheading", "seth"], ["lkivvN"]),\
            (["circle"],             ["oigvl"]),\
            (["dot"],                ["nqvde"]),\
            (["stamp"],              ["hvtmt"]),\
            (["clearstamp"],         ["nqe`hvtmt"]),\
            (["clearstamps"],        ["nqe`hvtmvt"]),\
            (["undo"],               ["bul"]),\
            (["speed"],              ["meirvt"]),\
            (["position"],           ["miqvM"]),\
            (["towards"],            ["zvvit"]),\
            (["xcor"],               ["rvhb"]),\
            (["ycor"],               ["avrK"]),\
            (["pos"],                ["miqvM"]),\
            (["heading"],            ["kivvN"]),\
            (["distance"],           ["mrhq"]),\
            (["repeat"],             ["hzvr"]),\
            (["end"],                ["svF"]),\
            (["to"],                 ["lmd"]) ]
            
PEN_UP = 0
PEN_DOWN = 1
PEN_ERASE = 2
PEN_REVERSE = 3

HEBREW_LATIN = "abgdevzhuiKklMmNnsoFfXxqrwt"
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

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
        return u"".join(out)

class Commander:
    def __init__(self):
        self.HH = HebrewHandler()
        self.movement_commands = {}
        self.commands = {}
        self.namespace = {}
        self.turtle_home_position = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]
        self.home()
        self.turtle_direction = 0
        
        self.refresh_turtle_flag = False
        self.show_turtle_flag = True
        self.pen_mode = PEN_DOWN
        self.temp_image = None
        self.command_loop_level = 0
        self.current_proc_name = False

        for w in COMMANDS:
           logo = w[0]
           hebrew = w[1]
           for command in logo:
                self.commands[command] = (logo[0],None)
           for hcommand in hebrew:
                hebrew_command = self.HH.to_hebrew(hcommand)
                self.commands[hebrew_command] = (logo[0], None)
    
    def set_drawing_area(self, area):
        self.area = area
        self.style = self.area.get_style()
        self.gc = self.area.window.new_gc(foreground=None, background=None, font=None, function=-1, fill=-1, tile=None, stipple=None, clip_mask=None, subwindow_mode=-1,ts_x_origin=-1, ts_y_origin=-1, clip_x_origin=-1,
clip_y_origin=-1, graphics_exposures=-1,line_width=-1, line_style=-1, cap_style=-1,join_style=-1)

    def set_output_label(self, label):
        self.output_label = label
        
    def tokenize(self, text, debug=False):
        if debug: 
            print "Tokenizing", text
        i = 0
        tokens = []
        token = ""
        error = ""
        all_ok = True
        brackets_level = 0
        quotation_flag = False
        backslash_flag = False
        vertical_bars_flag = False
        comment_flag = False
        # An alternative notation to include otherwise delimiting characters in words is to enclose a group of characters in vertical bars.  All characters between vertical bars are treated as if they were letters.  In data read with READWORD the vertical bars are preserved in the resulting word.  In data read with READLIST (or resulting from a PARSE or RUNPARSE of a word) the vertical bars do not appear explicitly; all potentially delimiting characters (including spaces, brackets, parentheses, and infix operators) appear as though entered with a backslash.  Within vertical bars, backslash may still be used; the only characters that must be backslashed in this context are backslash and vertical bar themselves.         
        # To include an otherwise delimiting character (including semicolon or tilde) in a word, precede it with backslash (\).         
        while i < len(text):
            if brackets_level:
                if text[i] == brackets_type[0]:
                    brackets_level = brackets_level + 1
                    
                elif text[i] == brackets_type[1]:
                    brackets_level = brackets_level - 1
                token = token + text[i]
            elif backslash_flag:
                token = token + text[i]
                backslash_flag = False
            elif vertical_bars_flag:
                token = token + text[i]
                if text[i] == "|":
                    vertical_bars_flag = False
            elif text[i] == "\\":
                token = token + text[i]
                backslash_flag = True
            elif text[i] == "|":
                token = token + text[i]                
                vertical_bars_flag = True
            elif text[i] == "[": 
                quotation_flag = False #After a quotation mark outside square brackets, a word is delimited by a space, a square bracket, or a parenthesis.
                brackets_level = 1
                brackets_type = "[]"
                if token:
                    tokens.append(token)                
                token = brackets_type[0]
            elif text[i] == "(": 
                quotation_flag = False #After a quotation mark outside square brackets, a word is delimited by a space, a square bracket, or a parenthesis.
                brackets_level = 1
                brackets_type = "()"
                if token:
                    tokens.append(token)
                token = brackets_type[0]
            elif text[i] == "\"": 
                quotation_flag = True # After a quotation mark outside square brackets, a word is delimited by a space, a square bracket, or a parenthesis.
                token = token + text[i]
            elif text[i] in "+-*/<>=": #A word not after a quotation mark or inside square brackets is delimited by a space, a bracket, a parenthesis, or an infix operator +-*/=<>. 
                if not quotation_flag:
                    if token:
                        tokens.append(token)
                    else:
                        if text[i] in "<>=" and tokens[-1] in "<>=": #Each infix operator character is a word in itself, except the two-character sequences <= >= and <> 
                            tokens[-1] = tokens[-1] + text[i]
                        else:
                            tokens.append(text[i])
                    token=""
            elif text[i] == " ":
                quotation_flag = False # After a quotation mark outside square brackets, a word is delimited by a space, a square bracket, or a parenthesis.
                tokens.append(token)
                token = ""
            else:
                token = token + text[i]
            i = i + 1
        if token:
            tokens.append(token)
        if debug:
            print tokens, token, brackets_level

        if brackets_level > 0:
            error = self.HH.to_hebrew("ivtr mdi " + brackets_type[0])
        elif brackets_level < 0:
            error = self.HH.to_hebrew("ivtr mdi " + brackets_type[1])
        tokens = [x for x in tokens if x]
        if debug:
            print "TOKENS=", tokens
        return tokens, error        
        
    def process_expression(self, words, namespace={}, parameter_only=False, debug=False):
        if debug:
            print "Process expression: Words=", words
        token = words[0]
        words = words[1:]
        error = ""
        value = None
        if debug:
            print "Processing expression: Token", token, "Namespace", namespace
        if token in self.commands: 
            token = self.commands[token][0]
            if token in ["xcor", "ycor", "pos", "heading", "scrunch"]:
                if token == "xcor":
                    value = self.turtle_position[0]
                elif token == "ycor":
                    value = self.turtle_position[1]
                    
            elif token in ["first", "butfirst", "last", "butlast", "pick", "redup"]:
                parameter, words, error = self.process_expression(words, namespace, parameter_only=True)
                print "Words=", words, "Param=", parameter, "Error=", error
                if token == "first":
                    value = self.handle_first_and_last(0, parameter)
                elif token == "butfirst":
                    value = self.handle_butfirst_and_butlast(1, None, parameter)
                elif token == "last":
                    value = self.handle_first_and_last(-1, parameter)
                elif token == "butlast":
                    value = self.handle_butfirst_and_butlast(0, -1, parameter)
                elif token == "pick":
                    value = self.handle_pick(parameter)
                elif token == "redup":
                    value = self.handle_redup(parameter)
                
            elif token in ["random", "sin", "cos","tan","arctan","int","minus","sqrt", "towards"]:
                parameter, words, error = self.process_expression(words, namespace, parameter_only=True)
                print "Words=", words, "Param=", parameter, "Error=", error
                if token == "sin":
                    value = math.sin(math.radians(parameter))
                elif token == "cos":
                    value = math.cos(math.radians(parameter))
                elif token == "tan":
                    value = math.atan(math.radians(parameter))
                elif token == "arctan":
                    value = math.degrees(math.atan(parameter))
                elif token == "random":
                    value = int(random.random() * int(parameter))
                elif token == "int":
                    value = int(parameter)
                elif token == "minus":
                    value = parameter * -1
                elif token == "sqrt":
                    value = math.sqrt(parameter)

            elif token in ["remainder", "power"]:
                parameter1, words, error = self.process_expression(words, namespace, parameter_only=True)
                parameter2, words, error = self.process_expression(words, namespace, parameter_only=True)
                if token == "remainder":
                    value = parameter1 % parameter2
                elif token == "power":
                    value = parameter1 ** parameter2

        elif token == "repcount" and "repcount" in namespace:
            value = namespace['repcount']

        elif token[0] == ":":
            if token[1:] in namespace:
                value = namespace[token[1:]]
            else:
                error = self.HH.to_hebrew("ani la ivdo me ze ")+token

        elif token[0] == "\"":
            value = token

        elif token[0] == "(" and token[-1] == ")":
            new_tokens, error = self.tokenize(token[1:-1])
            print "New_tokens=", new_tokens, "Error=", error
            value, dummy, error = self.process_expression(new_tokens, namespace)
        elif token[0] == "[" and token[-1] == "]":
            value = token
        else:
            value = float(token)
            #words = words[1:]
        #print "Now words=", words
        if words and words[0] in "+-/*%" and not parameter_only:
            #print "OPFound operator", words[0], "! value=", value
            operator = words[0]
            #print "OPNow words=", words
            value2, words, error = self.process_expression(words[1:], namespace)
            #print "Value2=", value2
            #print "OPNow words=", words

            if operator == "+":
                value = value + value2
            elif operator == "-":
                value = value - value2
            elif operator == "*":
                value = value * value2
            elif operator == "/":
                value = value / value2
            elif operator == "%":
                value = value % value2
        print "Expression Value=", value, "Words=", words, "Error=", error
        return value, words, error
        
        
    def handle_text(self, text, namespace={}):
        lines = text.split("\n")
        i = 0
        wait_for_complete_line_flag = False
        command = ""
        while i < len(lines):
            if not lines[i]:
                i = i + 1
            else:
                if lines[i][:2] == "#!":
                    i = i + 1
                if lines[i][-1] == "~":
                    wait_for_complete_line_flag = True
                else:
                    wait_for_complete_line_flag = False                   
                
                if ";" in lines[i]:
                    line = line[i][:lines[i].index(";")]
                else:
                    line = lines[i]
                i = i + 1
                command = command + line
                if not wait_for_complete_line_flag:
                    self.handle_command(command, namespace)
                
    def handle_command(self, text, namespace={}):
        if not namespace:
            namespace = self.namespace
        # The two-character sequence #! at the beginning of a line also starts a comment.
        # A semicolon begins a comment in an instruction line.  Logo ignores characters from the semicolon to the end of the line.  A tilde as the last character still indicates a continuation line, but not a continuation of the comment.
        if text[-1] == "~": #A line (an instruction line or one read by READLIST or READWORD) can be continued onto the following line if its last character is a tilde (~).
            print "Line not completed!"
        self.command_loop_level = self.command_loop_level + 1
        startx, starty = self.turtle_position
        #print self.gc.function, self.gc.function == gtk.gdk.SET
        if self.temp_image:
            self.area.window.draw_image(self.gc, self.temp_image, 0, 0, int(startx - 9.0), int(starty- 9.0), 20, 20)
            self.temp_image = None
        unitext = text.decode("utf-8")
        words, error = self.tokenize(unitext)
        while words:
            print "WWWords=", words, error
            while not words[0]:
                words = words[1:]
            if self.current_proc_name:
                namespace = self.handle_to(words, namespace)
                words = []
            elif words[0] in namespace:
                print "Handling proc:", namespace[words[0]]
                command = words[0]
                words = words[1:]
                local_namespace = copy.deepcopy(namespace)
                #local_namespace = {}
                #for k in namespace:
                #    local_namespace[k] = namespace[k]
                for variable in namespace[command][0]:
                    parameter, words, error = self.process_expression(words, local_namespace)
                    local_namespace[variable[1:]] = parameter
                print local_namespace
                for line in namespace[command][1]:
                    self.handle_command(line, local_namespace)
            elif words[0] in self.commands:
                print "Process command:", words[0]
                command = words[0]
                if self.commands[command][0] in ['home', "hideturtle", "showturtle",\
                    "penup", "pendown", "penreverse", "penerase", "clearscreen", "clean",\
                    "wrap", "window", "fence"]:
                    if self.commands[command][0] == "home":
                        self.home()
                    elif self.commands[command][0] == "wrap":
                        self.wrap()
                    elif self.commands[command][0] == "window":
                        self.window()
                    elif self.commands[command][0] == "fence":
                        self.fence()
                    elif self.commands[command][0] == "clearscreen":
                        self.clear_screen()
                    elif self.commands[command][0] == "clean":
                        self.clean()
                    elif self.commands[command][0] == "hideturtle":
                        self.hide_turtle()
                    elif self.commands[command][0] == "showturtle":
                        self.show_turtle()
                    elif self.commands[command][0] == "penup":
                        self.pen_up()
                    elif self.commands[command][0] == "pendown":
                        self.pen_down()
                    elif self.commands[command][0] == "penerase":
                        self.pen_erase()
                    elif self.commands[command][0] == "penreverse":
                        self.pen_reverse()
                    words = words[1:]
                elif self.commands[command][0] in ["forward", "backward", "right", "left",\
                    "setpensize", "setheading", "setx", "sety", "print"]:
                    parameter, words, error = self.process_expression(words[1:], namespace)
                    if self.commands[command][0] == "forward":
                        self.forward(parameter)
                    elif self.commands[command][0] == "backward":
                        self.backward(parameter)
                    elif self.commands[command][0] == "right":
                        self.right(parameter)
                    elif self.commands[command][0] == "left":
                        self.left(parameter)
                    elif self.commands[command][0] == "setpensize":
                        self.set_pen_size(int(parameter))
                    elif self.commands[command][0] == "setheading":
                        self.set_heading(parameter)
                    elif self.commands[command][0] == "setx":
                        self.set_x(parameter)
                    elif self.commands[command][0] == "sety":
                        self.set_y(parameter)                    
                    elif self.commands[command][0] == "print":
                        self.print_output(parameter)
                        #print "PRINTING", parameter
                    #words = words[2:]
                elif self.commands[command][0] in ["setxy"]:
                    parameter1, words, error = self.process_expression(words[1:], namespace)
                    print parameter1, words, error
                    parameter2, words, error = self.process_expression(words[:], namespace)
                    print parameter2, words, error
                    if self.commands[command][0] == "setxy":
                        self.set_xy(parameter1, parameter2)
                elif self.commands[command][0] == "for":
                    self.for_loop(words[1], words[2], namespace)
                    words = words[3:]
                elif self.commands[command][0] == "repeat":
                    times, words, error = self.process_expression(words[1:], namespace)
                    #print words
                    loop_body = words[0][1:-1]
                    self.repeat_loop(int(times), loop_body, namespace)
                    words = words[1:]
                elif self.commands[command][0] == "to":
                    namespace = self.handle_to(words[1:], namespace)
                    words = []
                else:
                    print command, "not implemented yet"
            else:
                print "No command found in {%s}" % (words[0])
                words = []
        #else:
        #    print self.commands.keys()

        self.command_loop_level = self.command_loop_level - 1

        if self.command_loop_level == 0:
            if self.show_turtle_flag:
                self.draw_turtle()
        while gtk.events_pending():
            gtk.main_iteration(False)

    def _split_word(self, parameter):
        if parameter[0] !="\"":
            return None, parameter + "is not a word"
        chars = []
        i = 1
        while i < len(parameter):
            if chars and chars[-1] == "\\":
                chars[-1] = chars[-1] + parameter[i]
            else:
                chars.append(parameter[i])
            i = i + 1
        return chars, ""

    def _split_list(self, parameter):
        words, error = self.tokenize(parameter[1:-1])
        return words, error 
        
    def handle_first_and_last(self, place, parameter):
        print parameter
        if parameter[0] == "\"":
            chars, error = self._split_word(parameter)
            return "\"" + chars[place]
        elif parameter[0] == "[":
            words, error = self._split_list(parameter)
            print words
            return words[place]
        else:
            return None, "can't split "+str(parameter)

    def handle_butfirst_and_butlast(self, splace, eplace, parameter):
        if parameter[0] == "\"":
            chars, error = self._split_word(parameter)
            print chars[splace:eplace]
            return "\"" + "".join(chars[splace:eplace])
        elif parameter[0] == "[":
            words, error = self._split_list(parameter)
            return "["+ " ".join(words[splace:eplace]) + "]"
        else:
            return None, "can't split "+str(parameter)

    def handle_pick(self, parameter):
        if parameter[0] == "\"":
            chars, error = self._split_word(parameter)
            return "\"" + random.choice(chars), ""
        elif parameter[0] == "[":
            words, error = self._split_list(parameter)
            return random.choice(words), ""
        else:
            return None, "can't split "+str(parameter)

    def handle_to(self, words, namespace):
        if not self.current_proc_name:
            self.current_proc_name = words[0]
            namespace[words[0]] = [words[1:]] + [[]]
        elif words == ["end"] or words == [self.HH.to_hebrew("svF")]:
            self.current_proc_name = ""
        else:
            print namespace
            namespace[self.current_proc_name][1].append(" ".join(words))
        return namespace

    def random(self, number):
        import random
        return int(random.random(number))
            
    def clear_screen(self):
        self.area.window.clear()
        self.home()
        self.refresh_turtle_flag = True

    def clean(self):
        self.area.window.clear()
        self.refresh_turtle_flag = True
            
    def _move_to_position(self, endx, endy):
        startx, starty = self.turtle_position
        if self.pen_mode in [PEN_DOWN, PEN_ERASE, PEN_REVERSE]:
             self.area.window.draw_line(self.gc, int(startx), int(starty), int(endx), int(endy))
        self.turtle_position = [endx, endy]
        self.refresh_turtle_flag = True

    def forward(self, distance):
        self._move_distance(distance, -1)
        
    def backward(self, distance):
        self._move_distance(distance, 1)
            
    def _move_distance(self, distance, direction):
        startx, starty = self.turtle_position
        if self.turtle_direction == 180:
            dirx = 0
        else:
            dirx = math.sin(math.radians(self.turtle_direction))
        diry = math.cos(math.radians(self.turtle_direction))
        direction = direction + 0.0
        #print startx, starty, direction, dirx, diry, distance
        endx = startx + direction * dirx * (distance + 0.0)
        endy = starty + direction * diry * (distance + 0.0)
        #print "Moving", (startx, starty, endx, endy)
        if self.pen_mode in [PEN_DOWN, PEN_ERASE, PEN_REVERSE]:
             self.area.window.draw_line(self.gc, int(startx), int(starty), int(endx), int(endy))
        self.turtle_position = [endx, endy]
        self.refresh_turtle_flag = True

    def right(self, degrees):
        self.turtle_direction = (self.turtle_direction - degrees) % 360
        self.refresh_turtle_flag = True

    def left(self, degrees):
        self.turtle_direction = (self.turtle_direction + degrees) % 360
        self.refresh_turtle_flag = True
        
    def home(self):
        self.turtle_position = self.turtle_home_position[:]
        self.refresh_turtle_flag = True

    def show_turtle(self):        
        self.show_turtle_flag = True

    def hide_turtle(self):        
        self.show_turtle_flag = False
        
    def pen_up(self):
        self.pen_mode = PEN_UP

    def pen_down(self):
        self.pen_mode = PEN_DOWN
        
    def pen_erase(self):
        self.pen_mode = PEN_ERASE
        self.gc.function = gtk.gdk.CLEAR

    def pen_reverse(self):
        self.pen_mode = PEN_REVERSE
        self.gc.function = gtk.gdk.INVERT
        
    def set_heading(self, angle):
        self.turtle_direction = (angle) % 360

    def set_x(self, x):
        self._move_to_position(x + self.turtle_home_position[0], self.turtle_position[1])

    def set_y(self, y):
        self._move_to_position(self.turtle_position[0], y + self.turtle_home_position[1])

    def set_xy(self, x, y):
        self._move_to_position(x + self.turtle_home_position[0], y + + self.turtle_home_position[1])

    def set_pen_size(self, size):
        self.gc.line_width = size

    def repeat_loop(self, times, loop_body, namespace):
        for i in xrange(times):
            namespace['repcount'] = i + 1
            print "Loop body=", loop_body, i
            self.handle_command(loop_body, namespace)
        
    def for_loop(self, loop_header, loop_body, namespace={}):
        words, error = self.tokenize(loop_header[1:-1])
        #print "Words =", words, "error=", error
        if not error:
            variable = words[0]
            start, words, error = self.process_expression(words[1:], namespace)
            end, words, error = self.process_expression(words, namespace)
            if words:
                step = None
            else:
                if end > start:
                    step = 1
                else:
                    step = -1
            #print (start, end, step), words
            #values = xrange(int(start), int(end), int(step))
            ##print values, variable
            #for value in values:
            #    namespace[variable] = value
            #    self.handle_command(loop_body[1:-1], namespace)
            namespace[variable] = start
            if end > start:
                while namespace[variable] <= end:
                    if step == None:
                        current_step, dummy, error = self.process_expression(words, namespace)
                    else:
                        current_step = step
                    #print (start, end, step, current_step), words
                    self.handle_command(loop_body[1:-1], namespace)
                    namespace[variable] = namespace[variable] + current_step
            else:
                while namespace[variable] >= end:
                    if step == None:
                        current_step, dummy, error = self.process_expression(words, namespace)
                    else:
                        current_step = step
                    #print (start, end, step, current_step), words
                    self.handle_command(loop_body[1:-1], namespace)
                    namespace[variable] = namespace[variable] + current_step
        else:
            print "Error:", error
        
    def _calc_dirx_and_diry(self, angle):
        if angle == 180:
            dirx = 0.0
        else:
            dirx = math.sin(math.radians(angle))
        diry = math.cos(math.radians(angle))
        return dirx, diry
            
    def draw_turtle(self):
        startx, starty = self.turtle_position
        angle = self.turtle_direction
        head_dirx, head_diry = self._calc_dirx_and_diry(angle)
        toe1_dirx, toe1_diry = self._calc_dirx_and_diry(angle+120)
        toe2_dirx, toe2_diry = self._calc_dirx_and_diry(angle+240)
        head = (int(startx - head_dirx * 6.0), int(starty - head_diry * 6.0))
        toe1 = (int(startx - toe1_dirx * 6.0), int(starty - toe1_diry * 6.0))
        toe2 = (int(startx - toe2_dirx * 6.0), int(starty - toe2_diry * 6.0))
        #print "Cut on", int(startx - 10.0), int(starty- 10.0)
        self.temp_image = self.area.window.get_image(int(startx - 10.0), int(starty- 10.0), 20, 20) 
        self.area.window.draw_polygon(self.gc, True, (head, toe1, toe2))
        
    def print_output(self, output):
        if output and output[0] == "\"":
            output = output[1:]
        elif output and output[0] == "[" and output[-1] == "]":
            output = output[1:-1]
        self.output_label.set_text(str(output))
        print "PRINT", output
        

class App:
    def __init__(self):
        self.commander = Commander()
        self.window = gtk.Window()
        self.window.connect("destroy", self.destroy)
        vbox = gtk.VBox()
        self.area = gtk.DrawingArea()
        self.area.set_size_request(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.pangolayout = self.area.create_pango_layout("")
        self.scrolled = gtk.ScrolledWindow()
        self.scrolled.set_size_request(500, 500)
        self.scrolled.add_with_viewport(self.area)
        self.textbuffer = gtk.TextBuffer()
        self.textview = gtk.TextView()
        self.textview.set_buffer(self.textbuffer)
        self.textview.set_editable(False)
        self.label = gtk.Label()
        self.entry = gtk.Entry()
        self.entry.connect("activate", self.handle_command)
        self.entry.connect("key-press-event", self.handle_keypress)
        vbox.pack_start(self.scrolled, 0,0,False)
        vbox.pack_start(self.textview, 0,0,False)
        vbox.pack_start(self.label, 0,0,False)
        vbox.pack_start(self.entry, 0,0,False)
        self.window.add(vbox)
        self.window.show_all()
        self.commander.set_drawing_area(self.area)
        self.commander.set_output_label(self.label)
        self.history_index = 0
        self.history_mode = False
        self.history = []

    def handle_keypress(self, widget=None, event=None):
        if event.keyval == 65362: #up
            self.history_mode = True
            if self.history_index > 0:
                self.history_index = self.history_index - 1
            print self.history_index, len(self.history)
            widget.set_text(self.history[self.history_index])
            return True
        elif event.keyval == 65364: #down
            self.history_mode = True
            self.history_index = self.history_index + 1
            print self.history_index, len(self.history)
            if self.history_index == len(self.history):
                self.history_index = self.history_index - 1
            else:
                widget.set_text(self.history[self.history_index])
            return True
        else:
            self.history_mode = False

        
    def handle_command(self, widget=None, event=None):
        text = widget.get_text()
        self.commander.handle_command(text)
        widget.set_text("")
        if self.history_mode:
            pass
        else:
            self.history.append(text)
            self.history_index = len(self.history) - 1
        self.history_mode = False
        widget.grab_focus()
        
    def destroy(self, event=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

print __name__
if __name__ == "__main__":
    app = App()
    app.main()
