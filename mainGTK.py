#!/usr/bin/env python2.7

import turtle
import math, random, copy
import pygtk
pygtk.require('2.0')
import gtk

MODE_WRAP = "WRAP"
MODE_WINDOW = "WINDOW"
MODE_FENCE = "FENCE"

MODE_PRINT = 0
MODE_TYPE = 1
MODE_SHOW = 2

PEN_DOWN = "DOWN"
PEN_UP = "UP"

PEN_PAINT = "PAINT"
PEN_ERASE = "ERASE"
PEN_REVERSE = "REVERSE"

TURTLE_SHOW = True
TURTLE_HIDE = False

HEBREW_LATIN = "abgdevzhuiKklMmNnsoFfXxqrwt"
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

TRUE = "\"TRUE"
FALSE = "\"FALSE"

NUM = 0
WRD = 1
LST = 2
ARR = 3
TNG = 4
TRU = 5 #A "tf" input must be the word TRUE, the word FALSE, or a list.  If it's a list, then it must be a Logo expression, which will be evaluated to produce a value that must be TRUE or FALSE.  The comparisons with TRUE and FALSE are always case-insensitive.
CHR = 6

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
        COMMANDS = [
            #TURTLE AND WINDOW CONTROL missing FILL,LABEL,TEXTSCREEN,FULLSCREEN,SPLITSCREEN,SETSCRUNCH,REFRESH,NOREFRESH
            (["showturtle", "st"],   ["erae.xb","erx"],         [],            self.set_turtle_view,    TURTLE_SHOW),\
            (["hideturtle", "ht"],   ["estr.xb","esx"],         [],            self.set_turtle_view,    TURTLE_HIDE),\
            (["clean"],              ["nqe"],                   [],            self.clean,              None),\
            (["clearscreen", "cs"],  ["nqe.msK"],               [],            self.clear_screen,       None),\
            (["wrap"],               ["mxb.kdvr"],              [],            self.set_draw_mode,      MODE_WRAP),\
            (["window"],             ["mxb.hlvn"],              [],            self.set_draw_mode,      MODE_WINDOW),\
            (["fence"],              ["mxb.gdr"],               [],            self.set_draw_mode,      MODE_FENCE),\
            #PEN AND BACKGROUND CONTROL missing: SETPENCOLOR,SETPALETTE,
            (["pendown", "pd"],      ["evrd.ou","evrdou"],      [],            self.set_pen_position,   PEN_DOWN),\
            (["penup", "pu"],        ["erM.ou","erMou"],        [],            self.set_pen_position,   PEN_UP),\
            (["penpaint", "ppt"],    ["ou.xvbo","oux"],         [],            self.set_pen_mode,       PEN_PAINT),\
            (["penerase", "pe"],     ["ou.mvhq","oum"],         [],            self.set_pen_mode,       PEN_ERASE),\
            (["penreverse", "px"],   ["ou.evfK","oue"],         [],            self.set_pen_mode,       PEN_REVERSE),\
            #TURTLE MOTION missing: ARC
            (["forward", "fd"],      ["qd", "qdime"],           [NUM],         self.forward,            None),\
            (["backward", "bk"],     ["ah", "ahvre"],           [NUM],         self.backward,           None),\
            (["left", "lt"],         ["wm", "wmale"],           [NUM],         self.left,               None),\
            (["right", "rt"],        ["im", "imine"],           [NUM],         self.right,              None),\
            (["goto", "setpos"],     ["qbo.miqvM"],             [LST],         self.go_to,              None),\
            (["setxy"],              ["lxvmt"],                 [NUM,NUM],     self.set_xy,             None),\
            (["setx"],               ["lrvhb"],                 [NUM],         self.set_x,              None),\
            (["sety"],               ["lavrK"],                 [NUM],         self.set_y,              None),\
            (["setheading", "seth"], ["lkivvN"],                [NUM],         self.set_heading,        None),\
            (["setpensize"],         ["qbo.gvdl.ou"],           [LST],         self.set_pen_size,       None),\
            (["home"],               ["ebite"],                 [],            self.home,               None),\
            #TRANSMITTERS
            (["print", "pr"],        ["edfs", "ed"],            [TNG],         self.print_output,       None),\
            (["type"],               ["edfs.xmvd"],             [TNG],         self.type_output,        None),\
            (["show"],               ["edfs.gvlmi"],            [TNG],         self.show_output,       None),\
            (["random"],             ["egrl"],                  [NUM],         self.handle_math,        "random"),\
            (["sin"],                ["sinvs"],                 [NUM],         self.handle_math,        "sin"),\
            (["cos"],                ["qvsinvs"],               [NUM],         self.handle_math,        "cos"),\
            (["arctan"],             ["ungns"],                 [NUM],         self.handle_math,        "arctan"),\
            (["int"],                ["wlM"],                   [NUM],         self.handle_math,        "int"),\
            (["minus"],              ["minvs"],                 [NUM],         self.handle_math,        "minus"),\
            (["sqrt"],               ["wvrw"],                  [NUM],         self.handle_math,        "sqrt"),\
            (["remainder"],          ["warit"],                 [NUM,NUM],     self.handle_math,        "remainder"),\
            (["power"],              ["hzqe"],                  [NUM,NUM],     self.handle_math,        "power"),\
            (["first"],              ["rawvN"],                 [TNG],         self.first_and_last,       0),\
            (["firsts"],             ["rawvniM"],               [LST],         self.handle_firsts,        None),\
            (["butfirsts"],          ["la.rawvniM"],            [LST],         self.handle_butfirsts,     None),\
            (["butfirst"],           ["la.rawvN"],              [TNG],         self.butfirst_and_butlast, (1,None)),\
            (["last"],               ["ahrvN"],                 [TNG],         self.first_and_last,       -1),\
            (["lasts"],              ["ahrvniM"],               [LST],         self.handle_lasts,         None),\
            (["butlasts"],           ["la.ahrvniM"],            [LST],         self.handle_butlasts,      None),\
            (["item"],               ["aibr"],                  [NUM, TNG],    self.handle_item,          None),\
            (["remove"],             ["slq"],                   [TNG, LST],    self.handle_remove,        None),\
            (["remdup"],             ["slq.kfvliM"],            [LST],         self.handle_remdup,        None),\
            (["butlast"],            ["la.ahrvN"],              [TNG],         self.butfirst_and_butlast, (0,-1)),\
            (["quoted"],             ["kmile"],                 [TNG],         self.handle_quoted,        None),\
            #TURTLE MOTION QUERIES missing: SCRUNCH
            (["pos", "position"],    ["miqvM"],                 [],            self.handle_turtle_query,  "pos"),\
            (["xcor"],               ["rvhb"],                  [],            self.handle_turtle_query,  "xcor"),\
            (["ycor"],               ["avrK"],                  [],            self.handle_turtle_query,  "ycor"),\
            (["heading"],            ["kivvN"],                 [],            self.handle_turtle_query,  "heading"),\
            (["towards"],            ["zvvit"],                 [TNG],         self.towards,              None),\
            #
            (["repeat"],             ["hzvr"],                  [NUM,TNG],     self.repeat_loop,          None),\
            (["word"],               ["mile"],                  [WRD,WRD],     self.construct_word,       None),\
            (["list"],               ["rwime"],                 [TNG,TNG],     self.construct_list,       None),\
            (["sentence"],           ["mwfu"],                  [TNG,TNG],     self.construct_sentence,   None),\
            (["fput"],               ["wiM.braw"],              [TNG,LST],     self.handle_fput,          None),\
            (["pick"],               ["wlvF"],                  [TNG],         self.handle_pick,          None),\
            (["for"],                ["lkl"],                   [TNG,TNG],     self.for_loop,             None),\
            (["lput"],               ["wiM.bsvF"],              [TNG,LST],     self.handle_lput,          None),\
            (["if"],                 ["aM"],                    [TNG,LST],     self.handle_if,            None),\
            #QUERIES
            (["count"],              ["avrK"],                  [TNG],         self.handle_count,         None),\
            (["ascii"],              ["msfr.tv"],               [CHR],         self.handle_ascii,         None),\
            (["rawascii"],           ["msfr.tv.gvlmi"],         [CHR],         self.handle_rawascii,      None),\
            (["char"],               ["tv.msfr"],               [NUM],         self.handle_char,          None),\
            (["member"],             ["btvK"],                  [TNG,TNG],     self.handle_member,        None),\
            (["lowercase"],          ["avtivt.qunvt"],          [WRD],         self.handle_lowercase,     None),\
            (["uppercase"],          ["avtivt.gdvlvt"],         [WRD],         self.handle_uppercase,     None),\
            #PREDICATES
            (["wordp", "word?"],     ["mile?"],                 [TNG],         self.is_word,              None),\
            (["listp", "list?"],     ["rwime?"],                [TNG],         self.is_list,              None),\
            (["arrayp", "array?"],   ["morK?"],                 [TNG],         self.is_array,             None),\
            (["emptyp", "empty?"],   ["riq?"],                  [TNG],         self.is_empty,             None),\
            (["equalp", "equal?"],   ["wve?"],                  [TNG,TNG],     self.is_equal,             None),\
            (["notequalp", "notequal?"], ["la.wve?"],           [TNG,TNG],     self.is_not_equal,         None),\
            (["beforep", "before?"], ["lfni"],                  [WRD,WRD],     self.is_before,            None),\
            (["substringp", "substring?"], ["mile.btvK"],       [TNG,TNG],     self.is_substring,         None),\
            (["numberp", "number?"], ["msfr?"],                 [TNG],         self.is_number,            None),\
            (["backslashedp", "backslashed?"], ["tv.buvh?"],    [CHR],         self.is_backslashed,       None),\
            (["make"],               ["qbo"],                   [],            None,                      None),\
            (["end"],                ["svF"],                   [],            None,                      None),\
            (["to"],                 ["lmd"],                   [],            None,                      None),\
            (["load"],               ["uoN"],                   [],            None,                      None),\
            (["stop"],               ["oxvr"],                  [],            None,                      None),\
            (["help"],               ["ozre"],                  [],            self.handle_help,          None)\
            ]
            #(["circle"],             ["oigvl"]),\
            #(["dot"],                ["nqvde"]),\
            #(["stamp"],              ["hvtmt"]),\
            #(["clearstamp"],         ["nqe`hvtmt"]),\
            #(["clearstamps"],        ["nqe`hvtmvt"]),\
            #(["distance"],           ["mrhq"]),\

        ERRORS = [["too many %s", "ivtr mdi %s"],\
                  ["too few %s", "fhvt mdi %s"]\
                ]

        self.COMMANDS = COMMANDS
        self.HH = HebrewHandler()
        self.movement_commands = {}
        self.commands = {}
        self.namespace = {}
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.turtle_home_position = [SCREEN_WIDTH/2 + 0.0, SCREEN_HEIGHT/2 + 0.0]
        self.turtle_position = [0, 0]
        self.home()
        self.turtle_heading = 0
        
        self.refresh_turtle_flag = False
        self.show_turtle_flag = True
        self.pen_position = PEN_DOWN
        self.pen_mode = PEN_PAINT
        self.draw_mode = MODE_WINDOW
        self.temp_image = None
        self.command_loop_level = 0
        self.current_proc_name = False
        self.incomplete_line = ""

        for w in COMMANDS:
           logo = w[0]
           hebrew = w[1]
           inputs = w[2]
           function = w[3]
           default_input = w[4]
           for command in logo:
                self.commands[command] = (logo[0],inputs,function,default_input)
           for hcommand in hebrew:
                hebrew_command = self.HH.to_hebrew(hcommand)
                self.commands[hebrew_command] = (logo[0],inputs,function,default_input)
        
        self.test()
    
    def set_drawing_area(self, area):
        self.area = area
        self.style = self.area.get_style()
        self.gc = self.area.window.new_gc(foreground=None, background=None, font=None, function=-1,\
                                          fill=-1, tile=None, stipple=None, clip_mask=None, subwindow_mode=-1\
                                          ,ts_x_origin=-1, ts_y_origin=-1, clip_x_origin=-1,clip_y_origin=-1,\
                                          graphics_exposures=-1,line_width=-1, line_style=-1, cap_style=-1,\
                                          join_style=-1)

    def set_output_label(self, label):
        self.output_label = label
        
    def tokenize(self, text, debug=False):
        if debug: 
            print "Tokenizing", text
        text = self.incomplete_line + " " +text
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
                else:
                    token = token + text[i]
            
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
            #error = self.HH.to_hebrew("ivtr mdi " + brackets_type[0])
            error = 0 #OPEN_BRACKETS_ERROR
            self.incomplete_line = text
        else:
            self.incomplete_line = ""

        if brackets_level < 0:
            #error = self.HH.to_hebrew("ivtr mdi " + brackets_type[1])
            error = 1 #TOO_MANY_CLOSING_BRACKETS_ERROR

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
            inputs = self.commands[token][1]
            function = self.commands[token][2]
            default_input = self.commands[token][3]
            if len(inputs) == 0:
                if default_input != None:
                    value = function(default_input)
                else:
                    value = function()
                    
            elif len(inputs) == 1:
                parameter, words, error = self.process_expression(words, namespace, parameter_only=True)                    
                if default_input != None:
                    value = function(default_input, parameter)
                else:
                    value = function(parameter)
                
            elif len(inputs) == 2:
                parameter1, words, error = self.process_expression(words, namespace, parameter_only=True)
                parameter2, words, error = self.process_expression(words, namespace, parameter_only=True)                    
                if default_input != None:
                    value = function(default_input, parameter1, parameter2)
                else:
                    value = function(parameter1, parameter2)

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
            if debug:
                print "New_tokens=", new_tokens, "Error=", error
            value, dummy, error = self.process_expression(new_tokens, namespace)
        elif token[0] == "[" and token[-1] == "]":
            value = token
        else:
            value = float(token)           
            
        if words and words[0] in "+-/*%" and not parameter_only:
            operator = words[0]
            value2, words, error = self.process_expression(words[1:], namespace)

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
        
        if words and words[0] in ["<",">","=", ">=", "<=", "<>"] and not parameter_only:                
            operator = words[0]
            value2, words, error = self.process_expression(words[1:], namespace)
            if operator == "<":
                cond = (value < value2)
            elif operator == ">":
                cond = (value > value2)
            elif operator == "=":
                cond = (value == value2)
            elif operator == ">=":
                cond = (value >= value2)
            elif operator == "<=":
                cond = (value <= value2)
            elif operator == "<>":
                cond = (value != value2)
            if cond:
                value = TRUE
            else:
                value = FALSE
        
        if debug:
            print "Expression Value=", value, "Words=", words, "Error=", error
        return value, words, error
        
        
    def handle_text(self, text, namespace={}):
        # missing end brackets/parentheses should cause continuation line
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
                
    def handle_command(self, text, namespace={}, debug=False):
        all_ok = True
        if not text:
            return all_ok
        if not namespace:
            namespace = self.namespace
        # The two-character sequence #! at the beginning of a line also starts a comment.
        # A semicolon begins a comment in an instruction line.  Logo ignores characters from the semicolon to the end of the line.  A tilde as the last character still indicates a continuation line, but not a continuation of the comment.
        if text[-1] == "~": #A line (an instruction line or one read by READLIST or READWORD) can be continued onto the following line if its last character is a tilde (~).
            print "Line not completed!"
        self.command_loop_level = self.command_loop_level + 1
        startx, starty = self._get_turtle_position()

        if self.temp_image:
            self.area.window.draw_image(self.gc, self.temp_image, 0, 0, int(startx - 9.0), int(starty- 9.0), 20, 20)
            self.temp_image = None
        unitext = text.decode("utf-8")
        words, error = self.tokenize(unitext)
        if error == 0:
           return True

        while words:
            if debug: 
                print "WWWords=", words, error
            while not words[0]:
                words = words[1:]
            if self.current_proc_name:
                namespace = self.handle_to(words, namespace)
                words = []
            elif words[0] in namespace:
                if debug: 
                    print "Handling proc:", namespace[words[0]]
                command = words[0]
                words = words[1:]
                local_namespace = copy.deepcopy(namespace)
                for variable in namespace[command][0]:
                    parameter, words, error = self.process_expression(words, local_namespace)
                    local_namespace[variable[1:]] = parameter
                if debug: 
                    print local_namespace
                all_ok = True
                for line in namespace[command][1]:
                    if all_ok:
                        all_ok = self.handle_command(line, local_namespace)
                    else:
                        break
                all_ok = True
                        
            elif words[0] in self.commands:
                if debug: 
                    print "Process command:", words[0]
                command = words[0]
                token = self.commands[command][0]
                inputs = self.commands[token][1]
                function = self.commands[token][2]
                default_input = self.commands[token][3]
                
                if token == "for":
                    self.for_loop(words[1], words[2], namespace)
                    words = words[3:]

                elif token == "stop":
                    words = []
                    return_value = False
                    return False
                    
                elif token == "load":
                    filename, words, error =  self.process_expression(words[1:], namespace)
                    f = open(filename[1:], "rb")
                    # REPLACE THIS WITH HANDLE_TEXT and treat open brackets as indication of line continuation
                    lines = [l.replace("\r", "") for l in f.readlines()]
                    for line in lines:
                        all_ok = self.handle_command(line[:-1])

                elif token == "repeat":
                    times, words, error = self.process_expression(words[1:], namespace)
                    loop_body = words[0][1:-1]
                    self.repeat_loop(int(times), loop_body, namespace)
                    words = words[1:]

                elif token == "to":
                    namespace = self.handle_to(words[1:], namespace)
                    words = []
                    
                elif token == "make":
                    name, words, error = self.process_expression(words[1:], namespace)
                    value, words, error = self.process_expression(words[:], namespace)                    
                    namespace["\""+name] = value
                    words = []                

                elif len(inputs) == 0:
                    if default_input != None:
                        all_ok = function(default_input)
                    else:
                        all_ok = function()
                    words = words[1:]
                    
                elif len(inputs) == 1:
                    parameter, words, error = self.process_expression(words[1:], namespace)                    
                    if default_input != None:
                        all_ok = function(default_input, parameter)
                    else:
                        all_ok = function(parameter)
                
                elif len(inputs) == 2:
                    parameter1, words, error = self.process_expression(words[1:], namespace)
                    parameter2, words, error = self.process_expression(words[:], namespace)                    
                    if default_input != None:
                        all_ok = function(default_input, parameter1, parameter2)
                    else:
                        all_ok = function(parameter1, parameter2)
                
                else:
                    if debug: 
                        print command, "not implemented yet"
            else:
                if debug: 
                    print "No command found in {%s}" % (words[0])
                words = []
            if debug: 
                print "ALL_OK=", all_ok

        self.command_loop_level = self.command_loop_level - 1

        if self.command_loop_level == 0:
            if self.show_turtle_flag:
                self.draw_turtle()
        while gtk.events_pending():
            gtk.main_iteration(False)
            
        return all_ok

    def handle_math(self, token, parameter):
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
        elif token == "remainder":
             value = parameter[0] % parameter[1]
        elif token == "power":
             value = parameter[0] ** parameter[1]
        return value

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
        
    def handle_if(self, condition, block):
        all_ok = True
        if condition == "\"TRUE":
            all_ok = self.handle_command(block[1:-1])
        return all_ok
        
    def handle_lowercase(self, word):
        return str(word).lower()

    def handle_uppercase(self, word):
        return str(word).upper()
        
    def handle_ascii(self, parameter):
        return ord(parameter)

    def handle_rawascii(self, parameter):
        return ord(parameter)

    def handle_char(self, parameter):
        return chr(parameter)

    def handle_quoted(self, parameter):
        return "\"" + parameter

    def is_word(self, thing):
        if not thing:
           return FALSE
        elif thing[0] == "[" and thing[-1]=="]":
           return False
        return TRUE

    def is_list(self, thing):
        if not thing:
           return FALSE
        elif thing[0] != "[" or thing[-1] != "]":
           return FALSE
        return TRUE

    def is_array(self, thing):
        if not thing:
           return FALSE
        elif thing[0] != "{" or thing[-1] != "}":
           return FALSE
        return TRUE

    def is_empty(self, thing):
        if not thing or thing == "[]":
           return FALSE
        return TRUE

    def is_backslashed(self, thing):
        if thing and thing[0] == "\"":
           return TRUE
        return FALSE

    def is_substring(self, thing1, thing2):
        if thing1 in thing2:
            return TRUE
        return FALSE

    def is_before(self, thing1, thing2):
        if thing1 < thing2:
           return TRUE
        return FALSE

    def is_equal(self, thing1, thing2):
        if thing1 == thing2:
            return TRUE
        return FALSE

    def is_not_equal(self, thing1, thing2):
        if not self.is_equal(thing1, thing2):
            return TRUE
        return FALSE

    def is_number(self, thing):
        try:
            i = int(thing)
            return TRUE
        except:
            return FALSE
        
    def handle_count(self, parameter):
        if parameter[0] == "\"":
            chars, error = self._split_word(parameter)
            return len(chars)
        elif parameter[0] == "[":
            words, error = self._split_list(parameter)
            return len(words)
        else:
            return None, "can't split "+str(parameter)

    def handle_member(self, member, l):
        if parameter[0] == "\"":
            chars, error = self._split_word(parameter)
            if member in chars:
                return TRUE
            else:
                return FALSE
        elif parameter[0] == "[":
            words, error = self._split_list(parameter)
            if member in words:
                return TRUE
            else:
                return FALSE
        else:
            return None, "can't split "+str(parameter)
            
    def handle_item(self, index, thing):
        return first_and_last(index, thing)

    def handle_remove(self, thing, l):
        words, error = self._split_list(l)
        out = []
        for w in words:
            if self.is_equal(thing, w):
                continue
            else:
                out.append(w)
        return self.construct_list(out)

    def handle_remdup(self, l):
        words, error = self._split_list(l)
        out = []
        for w in words:
            if w in out:
                continue
            else:
                out.append(w)
        return self.construct_list(out)

    def _handle_firsts_etc(self, func):
        lists, error = self._split_list(l)
        out = []
        for sub_l in lists:
            out.append(func(sub_l))
        return self.construct_list(out)

    def handle_firsts(self, l):
        return self._handle_firsts_etc(self.handle_first)

    def handle_butfirsts(self, l):
        return self._handle_firsts_etc(self.handle_butfirst)

    def handle_lasts(self, l):
        return self._handle_firsts_etc(self.handle_last)

    def handle_butlasts(self, l):
        return self._handle_firsts_etc(self.handle_butlast)

    def handle_first(self, t):
        return self.first_and_last(0, t)

    def handle_butfirst(self, t):
        return self.butfirst_and_butlast([1,None], t)

    def handle_last(self, t):
        return self.first_and_last(-1, t)

    def handle_butlast(self, t):
        return self.butfirst_and_butlast([0,-1], t)
        
    def first_and_last(self, place, thing):
        if thing[0] == "\"":
            chars, error = self._split_word(thing)
            return "\"" + chars[place]
        elif thing[0] == "[":
            words, error = self._split_list(thing)
            return words[place]
        else:
            return None, "can't split "+str(thing)

    def butfirst_and_butlast(self, places, thing):
        splace, eplace = places
        if thing[0] == "\"":
            chars, error = self._split_word(thing)
            return "\"" + "".join(chars[splace:eplace])
        elif thing[0] == "[":
            words, error = self._split_list(thing)
            return "["+ " ".join(words[splace:eplace]) + "]"
        else:
            return None, "can't split "+str(thing)

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
            namespace[self.current_proc_name][1].append(" ".join(words))
        return namespace

    #def random(self, number):
    #    import random
    #    return int(random.random(number))

    def handle_fput(self, tng, lst):
        if tng[0] == "\"":
            item = tng[1:]
        else:
            item = tng
        return "[" + tng + " " + lst[1:] + "]"

    def handle_lput(self, tng, lst):
        if tng[0] == "\"":
            item = tng[1:]
        else:
            item = tng
        return "[" +  lst[:-1] + " " + tng +"]"
    
    def construct_word(self, parameter1, parameter2):
        parameters = [parameter1, parameter2]
        return "\"" + ("".join([p[1:] for p in parameters]))

    def construct_list(self, parameter1, parameter2 = None):
        if parameter2 == None:
            l = parameter1
        else:
            parameters = [parameter1, parameter2]
            l = []
            for p in parameters:
                if p[0] == "\"":
                    l.append(p[1:])
                elif p[0] == "[" and p[-1] == "]":
                    l.append(p)
        return "[" + " ".join(l) + "]"
        
    def construct_sentence(self, parameter1, parameter2):
        parameters = [parameter1, parameter2]
        l = []
        for p in parameters:
            if p[0] == "\"":
                l.append(p[1:])
            elif p[0] == "[" and p[-1] == "]":
                l.append(p[1:-1])
        return "[" + " ".join(l) + "]"        
            
    def clear_screen(self):
        self.area.window.clear()
        self.home()
        self.refresh_turtle_flag = True

    def clean(self):
        self.area.window.clear()
        self.refresh_turtle_flag = True

    def test(self):
        return
        print "1. 100.0, 100.0, 300.0, 300.0", self._calculate_visible_segment(100,100,300,300)
        print "2. -100.0, -100.0, 400.0, 400.0", self._calculate_visible_segment(-100,-100,400,400)
        print "2y. 400.0, 400.0, -100.0, -100.0", self._calculate_visible_segment(400,400,-100,-100)
        print "2z. -100.0, 400.0, 400.0, -100.0", self._calculate_visible_segment(-100,400,400,-100)
        print "2a. -110.0, -100.0, 290.0, 300.0", self._calculate_visible_segment(-110,-100,290,300)
        print "2b. -100.0, -90.0, 300.0, 310.0", self._calculate_visible_segment(-100,-90,300,310)
        print "2c. -100.0, 310.0, 300.0, -90.0", self._calculate_visible_segment(-100,310,300,-90)
        print "3. -100.0, -100.0, -100.0, -300.0", self._calculate_visible_segment(-100,-100,-100,-300)        
        print "4. -1000.0, -1000.0, 3000.0, 3000.0", self._calculate_visible_segment(-1000,-1000,3000,3000)
        print "5. -1000.0, 0.0, 3000.0, 0.0", self._calculate_visible_segment(-1000,0,3000,0)
        print "6. 0.0, -1000.0, 0.0, 3000.0", self._calculate_visible_segment(0,-1000,0,3000)
        print "7. -200.0, -1000.0, 300.0, 1000.0", self._calculate_visible_segment(-200,-1000,300,1000)
        print "8. -50, 50, 600, 50", self._calculate_visible_segment(-50,50,600,50)
        print "8. 50, 600, 50, -50", self._calculate_visible_segment(50,600,50,-50)
        
    def _is_visible(self, point):
        if point[0] >=0 and point[0] <= self.screen_width \
           and point[1] >= 0 and point[1] <= self.screen_height:
                return True
        return False
        
    def _calculate_a_and_b(self, sx, sy, ex, ey):
        deltax = ex - sx + 0.0
        deltay = ey - sy + 0.0

        if deltay == 0:
            a = 0.0
            b = sy
        elif deltax== 0:
            a = None
            b = None
        else:
            a = deltay / deltax
            b = sy - (a * sx)
        return a, b
        
    def _calculate_line_and_frame_instersections(self, sx, sy, ex, ey):
        #print "calculate_line_and_frame_instersections", sx, sy, ex, ey, H, W, a, b
        a , b = self._calculate_a_and_b(sx, sy, ex, ey)

        W = self.screen_width + 0.0
        H = self.screen_height + 0.0

        points = []

        if a == None and b == None:
           if self._is_visible((sx , 0)):
               points = [(sx, 0), (sx, self.screen_height)]
        elif a == 0:
            if self._is_visible((0, b)):
                points =  [(0, sy), (self.screen_width, sy)]
        else:
            y_for_0 = self._fix_float(b)
            y_for_W = self._fix_float(a * W + b)
            if a:
                x_for_0 = self._fix_float((0.0 - b) / a)
                x_for_H = self._fix_float((H - b) / a)
            else:
                x_for_0 = -1
                x_for_H = -1
        
            points = [p for p in [(0.0, y_for_0), (x_for_0, 0.0), (W, y_for_W), (x_for_H, H)] if self._is_visible(p)]

        return points
        
    def _fix_float(self, n):
        if int(n + 1) - n < 0.000000000001: # Should check for negative and positive numbers!
            n = int(n + 1) + 0.0
        elif int(n+1) - n > 0.999999999999:
            n = int(n) + 0.0
        return n       
        
    def _calculate_distance(self, sx, sy, ex, ey):
        return math.sqrt((sx - ex) ** 2 + (sy - ey) ** 2)
    
    def _find_closest_point(self, x, y, points):
        distance = self._calculate_distance(x, y, points[0][0], points[0][1])
        closest = points[0]
        for i in range(len(points)):
            temp_distance = self._calculate_distance(x, y, points[i][0], points[i][1])
            if temp_distance < distance:
                closest = points[i]
                distance = temp_distance
        return closest
        
    def _calculate_visible_segment(self, sx, sy, ex, ey):
        if sx == ex and sy == ey:
            return None
        sx = self._fix_float(sx)
        sy = self._fix_float(sy)
        ex = self._fix_float(ex)
        ey = self._fix_float(ey)

        points = self._calculate_line_and_frame_instersections(sx, sy, ex, ey)
        
        if self._is_visible((sx, sy)):
            line_sx = sx
            line_sy = sy
        elif not points:
            return None
        else:
            closest = self._find_closest_point(sx, sy, points)
            line_sx = closest[0]
            line_sy = closest[1]

        if self._is_visible((ex, ey)):
            line_ex = ex
            line_ey = ey
        elif not points:
            return None
        else:
            closest = self._find_closest_point(ex, ey, points)
            line_ex = closest[0]
            line_ey = closest[1]

        return line_sx, line_sy, line_ex, line_ey
            
    def _move_to_position(self, endx, endy):
        startx, starty = self._get_turtle_position()
        w = self.screen_width + 0.0
        h = self.screen_height + 0.0
        #
        if self.draw_mode == MODE_WRAP and self.pen_position == PEN_UP:
            endx = (endx % w) + 0.0
            endy = (endy % h) + 0.0
        elif self.draw_mode == MODE_WRAP and self.pen_position == PEN_DOWN:
            sx = startx
            sy = starty
            deltax = endx - startx
            deltay = endy - starty
            segment = self._calculate_visible_segment(sx, sy, endx, endy)
            all_ok = True
            while all_ok:
                line_startx, line_starty, line_endx, line_endy = segment
                self._draw(line_startx, line_starty, line_endx, line_endy)
                if line_endx == endx and line_endy == endy:
                    all_ok = False
                else:
                    dx = line_endx - line_startx + 0.0
                    dy = line_endy - line_starty + 0.0
                    sy = line_endy
                    sx = line_endx
                
                    if line_endx == 0:
                        sx = w
                    elif line_endx == w:
                        sx = 0
                   
                    if line_endy == 0:
                        sy = h
                    elif line_endy == h:
                        sy = 0

                    deltax = deltax - dx
                    deltay = deltay - dy
                    endx = sx + deltax
                    endy = sy + deltay

                    if sx == endx and sy == endy:
                        all_ok = False
                    else:                  
                        segment = self._calculate_visible_segment(sx, sy, endx, endy)
                        if segment and segment[0] == segment[2] and segment[1] == segment[3]:
                            all_ok = False
                
        elif self.draw_mode == MODE_FENCE:
            all_ok = True
            if endx < 0:
                endx = 0.0
                all_ok = False
            elif endx > w - 1:
                endx = w - 1.0
                all_ok = False
            if endy < 0:
                endy = 0.0
                all_ok = False
            elif endy > h - 1:
                all_ok = False
                endy = h -1.0
            
            if self.pen_position == PEN_DOWN and all_ok:
                self._draw(startx, starty, endx, endy)        
                
        elif self.draw_mode == MODE_WINDOW:
            if self.pen_position == PEN_DOWN:
                segment = self._calculate_visible_segment(startx, starty, endx, endy)
                if segment:
                    line_startx, line_starty, line_endx, line_endy = segment
                    self._draw(line_startx, line_starty, line_endx, line_endy)
        #
        self._set_turtle_position(endx, endy)
        self.refresh_turtle_flag = True
        return True

    def _draw(self, sx, sy, ex, ey):
        self.area.window.draw_line(self.gc, int(round(sx)), int(round(sy)), int(round(ex)), int(round(ey)))

    def forward(self, distance):
        return self._move_distance(distance, -1)
        
    def backward(self, distance):
        return self._move_distance(distance, 1)
            
    def _move_distance(self, distance, direction):
        startx, starty = self._get_turtle_position()
        if self.turtle_heading == 180:
            dirx = 0
        else:
            dirx = math.sin(math.radians(self.turtle_heading))
        diry = math.cos(math.radians(self.turtle_heading))
        direction = direction + 0.0
        endx = startx + direction * dirx * (distance + 0.0)
        endy = starty + direction * diry * (distance + 0.0)
        return self._move_to_position(endx, endy)

    def right(self, degrees):
        self.turtle_heading = (self.turtle_heading - degrees) % 360
        self.refresh_turtle_flag = True
        return True

    def left(self, degrees):
        self.turtle_heading = (self.turtle_heading + degrees) % 360
        self.refresh_turtle_flag = True
        return True
        
    def home(self):
        self._set_turtle_position(self.turtle_home_position[0], self.turtle_home_position[1])
        self.refresh_turtle_flag = True
        return True

    def set_turtle_view(self, flag):
        self.show_turtle_flag = flag
        self.refresh_turtle_flag = True
        return True
        
    def handle_turtle_query(self, query):
        tx , ty = self._get_turtle_position()
        x = tx - self.turtle_home_position[0]
        if x == int(x):
            x = int(x)
        
        y = ty - self.turtle_home_position[1]
        if y == int(y):
            y = int(y)
                
        if query == "xpos":
            return x
        elif query == "ypos":
            return y
        elif query == "pos":
            return "["+str(x)+" "\
                      +str(y)+"]"
        elif query == "heading":
            return self.turtle_heading

    def towards(self, pos, namespace={}):
        tokens, error = self.tokenize(pos[1:-1])
        x, tokens, error = self.process_expression(tokens[:], namespace)
        y, tokens, error = self.process_expression(tokens[:], namespace)
        return self.handle_math("arctan", x/y)

    def set_pen_position(self, position):
        self.pen_position = position
        return True
        
    def set_pen_mode(self, mode):
        self.pen_position = PEN_DOWN
        self.pen_mode = mode
        if mode == PEN_ERASE:
            self.gc.function = gtk.gdk.CLEAR
        elif mode == PEN_REVERSE:
            self.gc.function = gtk.gdk.INVERT
        else:
            self.gc.function = gtk.gdk.SET
        return True

    def set_draw_mode(self, mode):
        self.draw_mode = mode
        if mode == MODE_WINDOW:
            x = self._get_turtle_position()[0] % self.screen_width
            y = self._get_turtle_position()[1] % self.screen_height
            self.turtle_position = [x, y]
        return True

    def set_heading(self, angle):
        self.turtle_heading = (angle) % 360
        return True

    def set_x(self, x):
        return self._move_to_position(x + self.turtle_home_position[0], self._get_turtle_position()[1])

    def set_y(self, y):
        return self._move_to_position(self._get_turtle_position()[0], y + self.turtle_home_position[1])

    def set_xy(self, x, y):
        return self._move_to_position(x + self.turtle_home_position[0], y + self.turtle_home_position[1])
        
    def go_to(self, position):
        words, error = self.tokenize(position[1:-1])
        if not error:
            x, words, error = self.process_expression(words[1:], namespace)
            y, words, error = self.process_expression(words, namespace)
        return self.set_xy(x, y)        

    def set_pen_size(self, size):
        self.gc.line_width = size
        return

    def repeat_loop(self, times, loop_body, namespace):
        for i in xrange(times):
            namespace['repcount'] = i + 1
            all_ok = self.handle_command(loop_body, namespace)
        return all_ok
        
    def for_loop(self, loop_header, loop_body, namespace={}):
        words, error = self.tokenize(loop_header[1:-1])
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

            namespace[variable] = start
            if end > start:
                while namespace[variable] <= end:
                    if step == None:
                        current_step, dummy, error = self.process_expression(words, namespace)
                    else:
                        current_step = step
                    all_ok = self.handle_command(loop_body[1:-1], namespace)
                    namespace[variable] = namespace[variable] + current_step
            else:
                while namespace[variable] >= end:
                    if step == None:
                        current_step, dummy, error = self.process_expression(words, namespace)
                    else:
                        current_step = step
                    all_ok = self.handle_command(loop_body[1:-1], namespace)
                    namespace[variable] = namespace[variable] + current_step
        else:
            print "Error:", error
            return False
        return True
        
    def _calc_dirx_and_diry(self, angle):
        if angle == 180:
            dirx = 0.0
        else:
            dirx = math.sin(math.radians(angle))
        diry = math.cos(math.radians(angle))
        return dirx, diry

    def hide_turtle(self):
        startx, starty = self._get_turtle_position()
        if self.temp_image:
            self.area.window.draw_image(self.gc, self.temp_image, 0, 0, int(startx - 9.0), int(starty- 9.0), 20, 20)
            self.temp_image = None
        else:
            print "Can't hide turtle"
            
    def draw_turtle(self):
        startx, starty = self._get_turtle_position()
        angle = self.turtle_heading
        head_dirx, head_diry = self._calc_dirx_and_diry(angle)
        toe1_dirx, toe1_diry = self._calc_dirx_and_diry(angle+120)
        toe2_dirx, toe2_diry = self._calc_dirx_and_diry(angle+240)
        head = (int(startx - head_dirx * 6.0), int(starty - head_diry * 6.0))
        toe1 = (int(startx - toe1_dirx * 6.0), int(starty - toe1_diry * 6.0))
        toe2 = (int(startx - toe2_dirx * 6.0), int(starty - toe2_diry * 6.0))
        if self._is_visible((startx, starty)):
            self.temp_image = self.area.window.get_image(int(startx - 10.0), int(starty- 10.0), 20, 20) 
        else:
            self.temp_image = None
        self.area.window.draw_polygon(self.gc, True, (head, toe1, toe2))
        
    def _get_turtle_position(self):
        #print "TP", self.turtle_xposition, self.turtle_yposition
        return self.turtle_xposition, self.turtle_yposition
        
    def _set_turtle_position(self, x, y):
        #print "TP", x, y
        self.turtle_xposition = x
        self.turtle_yposition = y
        
    def show_output(self, output):
        #Prints the input or inputs like PRINT, except that if an input is a list it is printed inside square brackets
        return self.print_output(output, mode = MODE_SHOW)

    def type_output(self, output):
        #Prints the input or inputs like PRINT, except that no newline character is printed at the end and multiple inputs are not separated by spaces.
        return self.print_output(output, mode = MODE_TYPE)
        
    def print_output(self, output, mode=MODE_PRINT):
        print "OUTPUT=", output
        if type(output) == type(0) or type(output) == type(0.0):
            output = str(output)
            if output and output[-2:] == ".0":
                output = output[:-2]
        elif output and output[0] == "\"":
            output = output[1:]
        elif output and output[0] == "[" and output[-1] == "]" and (mode != MODE_SHOW):
            output = output[1:-1]
        self.output_label.set_text(str(output))
        if mode == MODE_TYPE:
            print output,
        return True
        
    def handle_help(self):
        for w in self.COMMANDS:
           logo = w[0]
           hebrew = w[1]
           inputs = w[2]
           function = w[3]
           default_input = w[4]
           for command in logo:
                print command,
           for hcommand in hebrew:
                print self.HH.to_hebrew(hcommand),
           print
        

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
            #print self.history_index, len(self.history)
            widget.set_text(self.history[self.history_index])
            return True
        elif event.keyval == 65364: #down
            self.history_mode = True
            self.history_index = self.history_index + 1
            #print self.history_index, len(self.history)
            if self.history_index == len(self.history):
                self.history_index = self.history_index - 1
            else:
                widget.set_text(self.history[self.history_index])
            return True
        else:
            self.history_mode = False

        
    def handle_command(self, widget=None, event=None):
        text = widget.get_text()
        all_ok = self.commander.handle_command(text)
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

if __name__ == "__main__":
    app = App()
    app.main()
