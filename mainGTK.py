#!/usr/bin/env python2.7

#import turtle
import math, random, copy
import pygtk
pygtk.require('2.0')
import gtk

import pango

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

WS = "Workspace"

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

class Workspace:
    def __init__(self, outer_workspace=None):
        self.primitives = {}
        self.procedures = {}
        self.names = {}
        self.plists = {}
        self.buried = []
        self.traced = []
        self.stepped = []
        self.outer_workspace = outer_workspace

    def set_primitives(self, primitives):
        self.primitives = primitives
        
    def set_outer_workspace(self, workspace):
        self.outer_workspace = workspace
        
    def _as_list(self, l):
        return "["+" ".join(l)+"]"
        
    def _is_in(self, item, dic_name):
        l = self.__dict__[dic_name].keys()
        lower_l = [x.lower() for x in l]
        if item.lower() in lower_l:
            return l[lower_l.index(item.lower())]
        else:
            return None

    def handle_proc_input(self, varname, value):
        self.names[varname] = value
        return True
        
    def handle_make(self, varname, value):
        if varname[0] == "\"":
            varname = varname[1:]
        fixed = self._is_in(varname, "names")
        if fixed is not None:
            self.names[fixed] = value
            all_ok = True
        elif self.outer_workspace is not None:
            all_ok = self.outer_workspace.handle_make(varname, value)
        else:
            self.names[varname] = value
            all_ok = True
        return all_ok

    def handle_name(self, value, varname):
        if varname[0] == "\"":
            varname = varname[1:]
        fixed = self._is_in(varname, "names")
        if fixed is not None:
            self.names[fixed] = value
            all_ok = True
        elif self.outer_workspace is not None:
            all_ok = self.outer_workspace.handle_name(value, varname)
        else:
            self.names[varname] = value
            all_ok = True
        return all_ok
        
    def handle_thing(self, varname):
        fixed = self._is_in(varname, "names")
        if fixed is not None:
            return self.names[fixed]
        elif self.outer_workspace is not None:
            return self.outer_workspace.handle_thing(varname)
        else:
            return None
            
    def get_procedure(self, procname):
        fixed = self._is_in(procname, "procedures")
        if fixed is not None:
            return self.procedures[fixed]
        elif self.outer_workspace is not None:
            return self.outer_workspace.get_procedure(procname)
        else:
            return None

    def get_primitive(self, name):
        fixed = self._is_in(name, "primitives")
        if fixed == None and self.outer_workspace is not None:
            return self.outer_workspace.get_primitive(name)
        elif fixed is not None:
            return self.primitives[fixed]
        else:
            return None
        #if procname in self.procedures:
        #    return self.procedures[procname]
        #elif self.outer_workspace is not None:
        #    return self.outer_workspace.get_procedure(procname)
        #else:
        #    return None
        
    def handle_global(self, varname):
        if self.outer_workspace is not None:
            return self.handle_global(varname)
        else:
            if self._is_in(varname, "names") is not None:
                pass
            else:
                self.names[varname] = None
            return True
        
    def _find_in_recursive(self, name, dic_name):
        if self._is_in(name, dic_name) is not None:
            return TRUE
        elif self.outer_workspace is not None:
            return self.outer_workspace._find_in_recursive(name, dic_name)
        return FALSE
        
    def handle_procedurep(self, name):
        if self.handle_primitivep(name) == TRUE:
            return TRUE
        elif self.handle_definedp(name) == TRUE:
            return TRUE
        else:
            return FALSE
        #if (name in self.procedures()) or (name in self.primitives()):
        #    return TRUE
        #elif self.outer_workspace is not None:
        #    return self.outer_workspace.handle_procedurep(name)
        #return FALSE

    def handle_primitivep(self, name):
        return self._find_in_recursive(name, "primitives")
        #if name in self.primitives():
        #    return TRUE
        #elif self.outer_workspace is not None:
        #    return self.outer_workspace.handle_primitivep(name)
        #return FALSE

    def handle_definedp(self, name):
        return self._find_in_recursive(name, "procedures")
        #if name in self.procedures():
        #    return TRUE
        #elif self.outer_workspace is not None:
        #    return self.outer_workspace.handle_definedp(name)
        #return FALSE

    def handle_namep(self, name):
        return self._find_in_recursive(name, "names")
        #if name in self.names():
        #    return TRUE
        #elif self.outer_workspace is not None:
        #    return self.outer_workspace.handle_namep(name)#
        #
        #return FALSE

    def handle_plistp(self, name):
        return self._find_in_recursive(name, "plists")
        #if name in self.plists():
        #    return TRUE
        #elif self.outer_workspace is not None:
        #    return self.outer_workspace.handle_plistp(name)
        #return FALSE
        
    def handle_local(self, name):
        fixed = self._is_in(name, "names")
        if fixed is None:
            self.names[name] = None
        return True

    def handle_contents(self):
        procs = self.handle_procedures()
        names = self.handle_names()
        plists = self.handle_plists()
        return self._as_list([procs, names,plists])

    def handle_buried(self):
        return self._as_list(self.buried)

    def handle_traced(self):
        return self._as_list(self.traced)
        
    def handle_stepped(self):
        return self._as_list(self.stepped)
        
    def handle_procedures(self):
        l = self._get_procedures()
        return self._as_list(l)

    def _get_names(self):
        if self.outer_workspace is not None:
            l = self.outer_workspace._get_names()
            l.extend([name for name in self.names if name not in self.buried])
        else:
            l = [name for name in self.names if name not in self.buried]
        return l

    def _get_procedures(self):
        if self.outer_workspace is not None:
            l = self.outer_workspace._get_procedures()
            l.extend([name for name in self.procedures if name not in self.buried])
        else:
            l = [name for name in self.procedures if name not in self.buried]
        return l

    def handle_primitives(self):
        l = [name for name in self.primitives]
        return self._as_list(l)
            
    def handle_names(self):
        l = self._get_names()
        names = self._as_list(l)
        return self._as_list([procs, names])

    def handle_plists(self):
        procs = "[]"
        names = "[]"
        l = [name for name in self.plists if name not in self.buried]
        #SHOULD FILTER AND SHOW ONLY NON-EMPTY PLISTS
        names = self._as_list(l)
        return self._as_list([procs, names])

    def handle_namelist(self, name_or_list):
        pass
    def handle_pllist(self, name_or_list):
        pass
    def handle_arity(self, proc_name):
        pass
    def handle_nodes(self):
        pass

class Commander:
    def __init__(self, app):
        self.app = app
        COMMANDS = [
            #CONSTRUCTORS missing: MDARRAY, COMBINE, REVERSE, GENSYM
            (["word"],               ["mile"],                  [WRD,WRD],     self.construct_word,       None),\
            (["list"],               ["rwime"],                 [TNG,TNG],     self.construct_list,       None),\
            (["sentence", "se"],     ["mwfu"],                  [TNG,TNG],     self.construct_sentence,   None),\
            (["fput"],               ["wiM.braw"],              [TNG,LST],     self.handle_fput,          None),\
            (["lput"],               ["wiM.bsvF"],              [TNG,LST],     self.handle_lput,          None),\
            (["array"],              ["morK"],                  [NUM],         self.construct_array,      None),\
            (["listtoarray"],        ["rwime.lmorK"],           [LST],         self.list_to_array,        None),\
            (["arraytolist"],        ["morK.lrwime"],           [ARR],         self.array_to_list,        None),\
            #SELECTORS missing: MDITEM
            (["first"],              ["rawvN"],                 [TNG],         self.first_and_last,       0),\
            (["firsts"],             ["rawvniM"],               [LST],         self.handle_firsts,        None),\
            (["last"],               ["ahrvN"],                 [TNG],         self.first_and_last,       -1),\
            (["lasts"],              ["ahrvniM"],               [LST],         self.handle_lasts,         None),\
            (["butfirst", "bf"],     ["la.rawvN"],              [TNG],         self.butfirst_and_butlast, (1,None)),\
            (["butfirsts", "bfs"],   ["la.rawvniM"],            [LST],         self.handle_butfirsts,     None),\
            (["butlast"],            ["la.ahrvN"],              [TNG],         self.butfirst_and_butlast, (0,-1)),\
            (["butlasts"],           ["la.ahrvniM"],            [LST],         self.handle_butlasts,      None),\
            (["item"],               ["aibr"],                  [NUM, TNG],    self.handle_item,          None),\
            (["remove"],             ["slq"],                   [TNG, LST],    self.handle_remove,        None),\
            (["remdup"],             ["slq.kfvliM"],            [LST],         self.handle_remdup,        None),\
            (["pick"],               ["wlvF"],                  [TNG],         self.handle_pick,          None),\
            (["quoted"],             ["kmile"],                 [TNG],         self.handle_quoted,        None),\
            #MUTATORS
            (["setitem"],            ["qbo.aibr"],              [NUM, ARR, TNG], None,    None),\
            #TURTLE AND WINDOW CONTROL missing FILL,LABEL,TEXTSCREEN,FULLSCREEN,SPLITSCREEN,SETSCRUNCH,REFRESH,NOREFRESH
            (["showturtle", "st"],   ["erae.xb","erx"],         [],            self.set_turtle_view,    TURTLE_SHOW),\
            (["hideturtle", "ht"],   ["estr.xb","esx"],         [],            self.set_turtle_view,    TURTLE_HIDE),\
            (["clean"],              ["nqe"],                   [],            self.clean,              None),\
            (["clearscreen", "cs"],  ["nqe.msK"],               [],            self.clear_screen,       None),\
            (["wrap"],               ["mxb.kdvr"],              [],            self.set_draw_mode,      MODE_WRAP),\
            (["window"],             ["mxb.hlvn"],              [],            self.set_draw_mode,      MODE_WINDOW),\
            (["fence"],              ["mxb.gdr"],               [],            self.set_draw_mode,      MODE_FENCE),\
            (["label"],              ["tvvit"],                 [TNG],         self.handle_label,       None),\
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
            (["circle"],             ["oigvl"],                 [NUM],         self.handle_circle,      None),\
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
            #TURTLE MOTION QUERIES missing: SCRUNCH
            (["pos", "position"],    ["miqvM"],                 [],            self.handle_turtle_query,  "pos"),\
            (["xcor"],               ["rvhb"],                  [],            self.handle_turtle_query,  "xcor"),\
            (["ycor"],               ["avrK"],                  [],            self.handle_turtle_query,  "ycor"),\
            (["heading"],            ["kivvN"],                 [],            self.handle_turtle_query,  "heading"),\
            (["towards"],            ["zvvit"],                 [TNG],         self.towards,              None),\
            #
            (["repeat"],             ["hzvr"],                  [NUM,TNG],     self.repeat_loop,          None),\
            (["for"],                ["lkl"],                   [TNG,TNG],     self.for_loop,             None),\
            (["if"],                 ["aM"],                    [TRU,LST],     self.handle_if,            None),\
            (["ifelse"],             ["aM.vahrt"],              [TRU,LST,LST], self.handle_if_else,       None),\
            (["do.while"],           ["owe.kl.ovd"],            [LST,TRU],     self.handle_do_while,      None),\
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
            (["memberp", "member?"], ["btvK?"],                 [TNG,TNG],     self.is_member,            None),\
            (["backslashedp", "backslashed?"], ["tv.buvh?"],    [CHR],         self.is_backslashed,       None),\
            (["setpencolor", "setpc"], ["qbo.xbo.ou"],          [TNG],         self.set_pen_color,        None),\
            (["setscreencolor", "setsc"], ["qbo.xbo.msK"],      [TNG],         self.set_screen_color,     None),\
            (["and", "AND"],         ["gM"],                    [TRU,TRU],     self.handle_logical,       "and"),\
            (["make"],               ["qbo.at"],                [WRD,TNG],     self.handle_workspace,     [WS,"make"]),\
            (["name"],               ["qra.l"],                 [TNG,WRD],     self.handle_workspace,     [WS,"name"]),\
            (["local"],              ["mqvmi"],                 [WRD],         self.handle_workspace,     [WS,"local"]),\
            (["global"],             ["ovlmi"],                 [WRD],         self.handle_workspace,     [WS,"global"]),\
            (["end"],                ["svF"],                   [],            None,                      None),\
            (["to"],                 ["lmd"],                   [],            None,                      None),\
            (["load"],               ["uoN"],                   [],            None,                      None),\
            (["stop"],               ["oxvr"],                  [],            None,                      None),\
            (["output"],             ["ehzr"],                  [TNG],         None,                      None),\
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
        #                black    blue     green     cyan    red     magenta  yellow  white
        self.BASIC_COLORS = [[0,0,0], [0,0,1], [0,1,0], [0,1,1],[1,0,0], [1,0,1], [1,1,0], [1,1,1]]
        #                brown     tan      forest      aqua     salmon       purple     orange     grey
        self.EXTRA_COLORS = [[0.5,0,0], [1,0.5,0.5], [0,0.5,0], [0,0,0.5],[1,0.5,0.5], [.5,0,.5], [1,0.5,0], [.5,.5,.5]]

        self.COMMANDS = COMMANDS
        self.HH = HebrewHandler()
        self.movement_commands = {}
        self.commands = {}
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.turtle_home_position = [SCREEN_WIDTH/2 + 0.0, SCREEN_HEIGHT/2 + 0.0]
        self.turtle_position = [0, 0]
        self.home()
        self.turtle_heading = 180
        
        self.refresh_turtle_flag = False
        self.show_turtle_flag = True
        self.pen_position = PEN_DOWN
        self.pen_mode = PEN_PAINT
        self.draw_mode = MODE_WRAP
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
        
        self.workspace = Workspace()
        self.workspace.set_primitives(self.commands)
        self.test()
    
    def set_output_label(self, label):
        self.output_label = label
        
    def tokenize(self, text, debug=False):
        text = self.incomplete_line + "\n" +str(text) #PROBLEM WITH COMMENTED LINES!
        if debug: 
            print "Tokenizing", text
            print "self.incomplete_line = ", self.incomplete_line
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
                
            elif text[i] == "{": 
                quotation_flag = False #After a quotation mark outside square brackets, a word is delimited by a space, a square bracket, or a parenthesis.
                brackets_level = 1
                brackets_type = "{}"
                if token:
                    tokens.append(token)
                token = brackets_type[0]
                
            elif text[i] == ";":
                tokens.append(token)
                token = ""
                if "\n" in text[i:]:
                    comment_end = text[i:].index("\n")
                    next = text[:i] + text[i + comment_end:]
                else:
                    text = text[:i]
            
            elif text[i] == "\"": 
                quotation_flag = True # After a quotation mark outside square brackets, a word is delimited by a space, a square bracket, or a parenthesis.
                token = token + text[i]
            
            elif text[i] in "+-*/<>=": #A word not after a quotation mark or inside square brackets is delimited by a space, a bracket, a parenthesis, or an infix operator +-*/=<>. 
                if quotation_flag or brackets_level:
                    token = token + text[i]                        
                else:
                    if token:
                        tokens.append(token)
                        tokens.append(text[i])
                    else:
                        if text[i] in "<>=" and tokens[-1] in "<>=": #Each infix operator character is a word in itself, except the two-character sequences <= >= and <> 
                            tokens[-1] = tokens[-1] + text[i]
                        else:
                            tokens.append(text[i])
                    token=""
            
            elif text[i] in (" ", "\n"):
                quotation_flag = False # After a quotation mark outside square brackets, a word is delimited by a space, a square bracket, or a parenthesis.
                tokens.append(token)
                token = ""
            
            else:
                token = token + text[i]

            i = i + 1

        if token:
            tokens.append(token)

        if brackets_level > 0:
            error = 0 #OPEN_BRACKETS_ERROR
            self.incomplete_line = text
        else:
            self.incomplete_line = ""

        if brackets_level < 0:
            error = 1 #TOO_MANY_CLOSING_BRACKETS_ERROR

        tokens = [x for x in tokens if x]
        if debug:
            print "TOKENS=", tokens
        return tokens, error        
        
    def process_expression(self, words, workspace={}, parameter_only=False, greedy = False, debug=False):
        if debug:
            print "Process expression: Words=", words
        if not workspace:
            workspace = self.workspace
        token = words[0]
        words = words[1:]
        error = ""
        value = None
        if debug:
            print "Processing expression: Token", token
            print token, "in self.commands?", workspace.handle_primitivep(token)
            print token, "in procedures?", workspace.handle_definedp(token)
            print token, "is a list?", self._is_list(token)
            print token, "is a word?", self._is_word(token)
            print token, "is an array?", self._is_array(token)
        
        if token == "repcount":
            value = self.current_repcount

        elif workspace.handle_definedp(token) == TRUE: #in workspace._get_procedures():
            if debug: 
                print "Handling proc:", token

            new_workspace = Workspace(workspace)
            for variable in workspace.get_procedure(token)[0]:
                parameter, words, error = self.process_expression(words, new_workspace)
                new_workspace.handle_proc_input(variable[1:], parameter)

            if debug: 
                print new_workspace.names
            all_ok = True

            for line in workspace.get_procedure(token)[1]:
                if all_ok is not None:
                    all_ok = self.handle_command_line(line, new_workspace)
                else:
                    break
            value = all_ok
            
        elif workspace.handle_primitivep(token) == TRUE: #token in self.commands: 
            #ixed = workspace._is_in(token, "primitives")
            #rint "Fixed=", fixed
            #f fixed is not None:
            data = workspace.get_primitive(token)
            token = data[0] #self.commands[fixed][0]
            inputs = data[1] #self.commands[token][1]
            function = data[2] #self.commands[token][2]
            default_input = data[3] #self.commands[token][3]

            if type (default_input) == type([]) and WS in default_input:
                default_input[default_input.index(WS)] = workspace

            if greedy:
                parameters = []
                while words:
                    parameter, words, error = self.process_expression(words, workspace, parameter_only=False)                    
                    parameters.append(parameter)
            else:
                parameters = []
                for i in range(len(inputs)):
                    parameter, words, error = self.process_expression(words, workspace, parameter_only=False)
                    parameters.append(parameter)

            if default_input != None:
                value = function(default_input, parameters) #, workspace)
            else:
                value = function(parameters) #, workspace)

        elif token[0] == ":":
            if workspace.handle_namep(token[1:]): #in workspace._get_names():
                value = workspace.handle_thing(token[1:])
            else:
                error = self.HH.to_hebrew("ani la ivdo me ze ")+token
                keys = workspace._get_names()
                keys.sort()
                print "I know only", keys

        elif token[0] == "\"":
            value = token

        elif token[0] == "(" and token[-1] == ")":
            new_tokens, error = self.tokenize(token[1:-1])
            if debug:
                print "New_tokens=", new_tokens, "Error=", error
            value, dummy, error = self.process_expression(new_tokens, workspace, greedy=True)
        
        elif self._is_list(token) == TRUE: # == "[" and token[-1] == "]":
            value = token
            
        elif self._is_array(token) == TRUE: #token[0] == "{" and token[-1] == "}":
            value = token

        else:
            try:
                value = float(token)           
            except:
                value = 0.0

        if words and words[0] in "+-/*%" and not parameter_only:
            operator = words[0]
            value2, words, error = self.process_expression(words[1:], workspace)
            if self.is_number([value]) == TRUE and self.is_number([value2]) == TRUE:
                value = float(value)
                value2 = float(value2)
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
            value2, words, error = self.process_expression(words[1:], workspace)
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
                
    def handle_text(self, text, workspace={}):
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
                    self.handle_command_line(command, workspace)
                
    def handle_command_line(self, text, workspace={}, debug=False):
        all_ok = True
        if not text:
            return all_ok
        if not workspace:
            workspace = self.workspace
        if debug:
            print "Handling", text

        # The two-character sequence #! at the beginning of a line also starts a comment.
        # A semicolon begins a comment in an instruction line.  Logo ignores characters from the semicolon to the end of the line.  A tilde as the last character still indicates a continuation line, but not a continuation of the comment.
        if text[-1] == "~": #A line (an instruction line or one read by READLIST or READWORD) can be continued onto the following line if its last character is a tilde (~).
            print "Line not completed!"
        self.command_loop_level = self.command_loop_level + 1
        startx, starty = self._get_turtle_position()

        if self.temp_image:
            self.app.paste_turtle(self.temp_image, startx, starty)
            #self.area.window.draw_image(self.gc, self.temp_image, 0, 0, int(startx - 9.0), int(starty- 9.0), 20, 20)
            self.temp_image = None
        #print "TEXT={"+text+"}"
        unitext = text.decode("utf-8")
        if self.current_proc_name:
            self.handle_to(unitext, workspace)
            words = []
        else:
            words, error = self.tokenize(unitext)
            if error == 0:
                all_ok = True
            else:
                all_ok = self.handle_command(words, workspace)

        self.command_loop_level = self.command_loop_level - 1

        if self.command_loop_level == 0:
            if self.show_turtle_flag:
                self.draw_turtle()
        while gtk.events_pending():
            gtk.main_iteration(False)
        return all_ok

    def handle_command(self, words, workspace=None, debug=False):
        all_ok = True
        if workspace is None:
            workspace = self.workspace
        while words:
            if debug: 
                print "Words=", words
            while not words[0]:
                words = words[1:]
            if debug:
                print words[0], "in self.commands?", workspace.handle_primitivep(words[0])
                print words[0], "in procedures?", workspace.handle_definedp(words[0])
                print words[0], "is a list?", self._is_list(words[0])
                print words[0], "is a word?", self._is_word(words[0])
                print words[0], "is an array?", self._is_array(words[0])
            if workspace.handle_definedp(words[0]) == TRUE: #words[0] in workspace._get_procedures():
                command = words[0]
                words = words[1:]
                new_workspace = Workspace(workspace)
                for variable in workspace.get_procedure(command)[0]:
                    parameter, words, error = self.process_expression(words, new_workspace)
                    new_workspace.handle_proc_input(variable[1:], parameter)
                if debug: 
                    print new_workspace.names
                all_ok = True
                for line in workspace.get_procedure(command)[1]:
                    if all_ok is not None:
                        all_ok = self.handle_command_line(line, new_workspace)
                    else:
                        break
                all_ok = True
                        
            elif workspace.handle_primitivep(words[0]) == TRUE: #words[0] in self.commands:
                if debug: 
                    print "Process command:", words[0]
                command = words[0]
                words = words[1:]
                data = workspace.get_primitive(command)
                #print "Primitive=", data
                token = data[0] #self.commands[fixed][0]
                inputs = data[1] #self.commands[token][1]
                function = data[2] #self.commands[token][2]
                default_input = data[3] #self.commands[token][3]
                #token = self.commands[command][0]
                #inputs = self.commands[token][1]
                #function = self.commands[token][2]
                #default_input = self.commands[token][3]
                if type (default_input) == type([]) and WS in default_input:
                    default_input[default_input.index(WS)] = workspace
                
                if token == "for":
                    self.for_loop([words[0], words[1]], workspace)
                    words = words[2:]
                    
                elif token == "output":
                    #print "Outputting: NOTHING DONE WITH OUTPUT YET!"
                    out, words, error =  self.process_expression(words, workspace)
                    return out

                elif token == "stop":
                    words = []
                    return_value = None
                    return None
                    
                elif token == "load":
                    filename, words, error =  self.process_expression(words, workspace)
                    f = open(filename[1:], "rb")
                    # REPLACE THIS WITH HANDLE_TEXT and treat open brackets as indication of line continuation
                    lines = [l.replace("\r", "") for l in f.readlines()]
                    for line in lines:
                        all_ok = self.handle_command_line(line[:-1])

                elif token == "do.while":
                    condition = words[1]
                    block = words[0]
                    self.handle_do_while([condition, block], workspace)
                    words = words[2:]

                elif token == "repeat":
                    times, words, error = self.process_expression(words, workspace)
                    loop_body = words[0][1:-1]
                    self.repeat_loop([int(times), loop_body], workspace)
                    words = words[1:]

                elif token == "to":
                    self.handle_to(words, workspace)
                    words = []
                    
                #elif token == "make":
                #    name, words, error = self.process_expression(words[:], workspace)
                #    value, words, error = self.process_expression(words[:], workspace) 
                #    workspace.handle_make(name[1:], value)
                #    words = []                

                #elif token == "name":
                #    value, words, error = self.process_expression(words[:], workspace)
                #    name, words, error = self.process_expression(words[:], workspace) 
                #    workspace.handle_name(value, name[1:])
                #    words = []                

                elif token == "setitem":
                    index, words, error = self.process_expression(words[:], workspace)
                    name = words[0]
                    array, words, error = self.process_expression(words[:], workspace) 
                    value, words, error = self.process_expression(words[:], workspace) 
                    workspace.handle_make(name[1:], self.handle_set_item([index, array, value]))

                else:
                    parameters = []
                    #print "Inputs=", inputs, words
                    for i in range(len(inputs)):
                        parameter, words, error = self.process_expression(words[:], workspace)                    
                        parameters.append(parameter)
                    #print "Parameters=", parameters
                        
                    if default_input != None:
                        all_ok = function(default_input, parameters)
                    else:
                        all_ok = function(parameters)
            else:
                print "No COMMAND found in {%s}" % words[0]
                all_ok = False
            if debug: 
                print "ALL_OK=", all_ok

        return all_ok
        
    def handle_workspace(self, workspace_and_command, parameters):
        workspace, command = workspace_and_command
        while parameters:
            if command == "make":
                all_ok = workspace.handle_make(parameters[0], parameters[1])
                parameters = parameters[2:]
            elif command == "name":
                all_ok = workspace.handle_name(parameters[0], parameters[1])
                parameters = parameters[2:]
            elif command == "local":
                all_ok = workspace.handle_local(parameters[0])
                parameters = parameters[1:]
            elif command == "global":
                all_ok = workspace.handle_global(parameters[0])
                parameters = parameters[1:]
        if all_ok is None:
            print "All ok is none after", command
        return all_ok

    def handle_logical(self, token, parameters, workspace={}):
        if token == "not":
            boolean = not (parameters[0] == TRUE)
        elif token == "and":
            boolean = (parameters[0] == TRUE) and (parameters[1] == TRUE)
        elif token == "or":
            boolean = (parameters[0] == TRUE) or (parameters[1] == TRUE)
            
        if boolean:
            return TRUE
        else:
            return FALSE

    def handle_math(self, token, parameters, workspace={}):
        if token == "sin":
             value = math.sin(math.radians(parameters[0]))
        elif token == "cos":
             value = math.cos(math.radians(parameters[0]))
        elif token == "tan":
             value = math.atan(math.radians(parameters[0]))
        elif token == "arctan":
             value = math.degrees(math.atan(parameters[0]))
        elif token == "random":
             value = int(random.random() * int(parameters[0]))
        elif token == "int":
             value = int(parameters[0])
        elif token == "minus":
             value = parameters[0] * -1
        elif token == "sqrt":
             value = math.sqrt(parameters[0])
        elif token == "remainder":
             value = parameters[0] % parameters[1]
        elif token == "power":
             value = parameters[0] ** parameters[1]
        return value

    def _split_word(self, parameter, workspace={}):
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

    def _split_list(self, text, workspace={}):
        #Within square brackets, words are delimited only by spaces and square brackets.
        #words, error = self.tokenize(parameter[1:-1])
        brackets = 0
        words = []
        i = 0
        word = ""
        error = ""
        if text[0] == "[" and text[-1] == "]":
            text = text[1:-1]
        
        while i < len(text):
            if brackets:
                word = word + text[i]
            elif text[i] == "[":
                brackets = brackets + 1
                words.append(word)
                word = text[i]
            elif text[i] == "]":
                brackets = brackets - 1
                words.append(word+text[i])
                word = []
            elif text[i] == " ":
                words.append(word)
                word = ""
            else:
                word = word + text[i]
            i = i + 1
        if word:
           words.append(word)
        return words, error 

    def _split_array(self, text, workspace={}):
        #Within square brackets, words are delimited only by spaces and square brackets.
        #words, error = self.tokenize(parameter[1:-1])
        brackets = 0
        words = []
        i = 0
        word = ""
        error = ""
        if text[0] == "{" and text[-1] == "}":
            text = text[1:-1]
            origin = 1
        elif text[0] == "{" and ("}@" in text):
            items = text[1:].split("}@")
            text = "}@".join(items[:-1])
            origin = items[-1]
        
        while i < len(text):
            if brackets and text[i] == "]":
                brackets = brackets - 1
                words.append(word+text[i])
                word = []
            elif brackets:
                word = word + text[i]
            elif text[i] == "[":
                brackets = brackets + 1
                words.append(word)
                word = text[i]
            elif text[i] == " ":
                words.append(word)
                word = ""
            else:
                word = word + text[i]
            i = i + 1
        words.append(word)
        words = [w for w in words if w]
        origin = int(origin)
        return words, origin, error 

    def handle_circle(self, parameters):
        x, y = self._get_turtle_position()
        diameter = parameters[0]
        self.app.draw_circle(x, y, diameter)
        
    def handle_if(self, parameters, workspace={}):
        condition, block = parameters
        all_ok = True
        if condition == TRUE:
            all_ok = self.handle_command_line(block[1:-1], workspace)
        return all_ok

    def handle_if_else(self, parameters, workspace={}):
        condition, block1, block2 = parameters
        all_ok = True
        if condition == TRUE:
            all_ok = self.handle_command_line(block1[1:-1], workspace)
        else:
            all_ok = self.handle_command_line(block2[1:-1], workspace)
        return all_ok

    def handle_do_while(self, parameters, workspace={}):
        condition, block = parameters
        words, error = self.tokenize(condition[1:-1])      
        result, dummy, error = self.process_expression(words[:], workspace)
        all_ok = True
        while result == TRUE:
            all_ok = self.handle_command_line(block[1:-1])
            result, dummy, error = self.process_expression(words[:], workspace)
        return all_ok
        
    def handle_lowercase(self, parameters, workspace={}):
        return str(parameters[0]).lower()

    def handle_uppercase(self, parameters, workspace={}):
        return str(parameters[0]).upper()
        
    def handle_ascii(self, parameters, workspace={}):
        return ord(parameters[0])

    def handle_rawascii(self, parameters, workspace={}):
        return ord(parameters[0])

    def handle_char(self, parameters, workspace={}):
        return chr(parameter[0])

    def handle_quoted(self, parameters, workspace={}):
        return "\"" + parameters[0]

    def is_word(self, parameters, workspace={}):
        thing = parameters[0]
        return self._is_word(thing)
            
    def _is_word(self, thing):
        if not thing:
           return FALSE
        elif str(thing)[0] == "[" and str(thing)[-1]=="]":
           return False
        elif str(thing)[0] == "{" and str(thing)[-1]=="}":
           return False        
        return TRUE

    def is_list(self, parameters, workspace={}):
        thing = parameters[0]
        return self._is_list(thing)
            
    def _is_list(self, thing):
        if thing and str(thing)[0] == "[" and str(thing)[-1] == "]":
           return TRUE
        return FALSE

    def is_array(self, thing, parameters, workspace={}):
        thing = parameters[0]
        return self._is_array(thing)
            
    def _is_array(self, thing, workspace={}):
        if thing[0] == "{" and ((thing[-1] == "}") or ("}@" in thing)):
           return TRUE
        return FALSE

    def is_empty(self, parameters, workspace={}):
        thing = parameters[0]
        if not thing or thing == "[]":
           return FALSE
        return TRUE

    def is_backslashed(self, parameters, workspace={}):
        thing = parameters[0]
        if thing and thing[0] == "\\":
           return TRUE
        return FALSE

    def is_substring(self, parameters, workspace={}):
        thing1, thing2 = parameters
        if thing1 in thing2:
            return TRUE
        return FALSE

    def is_before(self, parameters, workspace={}):
        thing1, thing2 = parameters
        if thing1 < thing2:
           return TRUE
        return FALSE

    def is_equal(self, parameters, workspace={}):
        thing1, thing2 = parameters
        if thing1 == thing2:
            return TRUE
        return FALSE

    def is_not_equal(self, parameters, workspace={}):
        if not self.is_equal(parameters, workspace):
            return TRUE
        return FALSE

    def is_number(self, parameters, workspace={}):
        thing = parameters[0]
        try:
            i = int(thing)
            return TRUE
        except:
            return FALSE

    def is_member(self, parameters, workspace={}):
        thing1, thing2 = parameters
        #if "thing2" is a list or an array, outputs TRUE if "thing1" is EQUALP 	to a member of "thing2", FALSE otherwise.  If "thing2" is 	a word, outputs TRUE if "thing1" is a one-character word EQUALP to a 	character of "thing2", FALSE otherwise.
        if self._is_list(thing2) == TRUE:
            items, error = self._split_list(thing2)
            if thing1 in items:
                return TRUE
        elif self._is_array(thing2) == TRUE:
            items, origin, error = self._split_array(thing2, workspace)
            if thing1 in items:
                return TRUE
        elif self._is_word(thing2) == TRUE and self._is_word(thing1) == TRUE:
            if len(thing1) == 2 and thing1[1:] in thing2:
                return TRUE
        return FALSE
                
    def handle_count(self, parameters, workspace={}):
        thing = parameters[0]
        if self._is_word(thing):
            chars, error = self._split_word(thing, workspace)
            return len(chars)
        elif self._is_list(thing):
            words, error = self._split_list(thing, workspace)
            return len(words)
        else:
            return None, "can't split "+str(thing)

    def handle_member(self, parameters, workspace={}):
        member, l = parameters
        if self._is_word(member):
            chars, error = self._split_word(member, workspace)
            if member in chars:
                return TRUE
            else:
                return FALSE
        elif self._is_list(member):
            words, error = self._split_list(member, workspace)
            if member in words:
                return TRUE
            else:
                return FALSE
        else:
            return None, "can't split "+str(parameter)
            
    def handle_item(self, parameters, workspace={}):
        index, thing = parameters
        return self.first_and_last(index-1, [thing], workspace)

    def handle_remove(self, parameters, workspace={}):
        thing, l = parameters
        words, error = self._split_list(l, workspace)
        out = []
        for w in words:
            if self.is_equal([thing, w], workspace):
                continue
            else:
                out.append(w)
        return self.construct_list(out, workspace)

    def handle_remdup(self, parameters, workspace={}):
        l = parameters[0]
        words, error = self._split_list(l, workspace)
        out = []
        for w in words:
            if w in out:
                continue
            else:
                out.append(w)
        return self.construct_list(out, workspace)

    def _handle_firsts_etc(self, func, parameters, workspace):
        l = parameters[0]
        if self._is_list(l):
            lists, error = self._split_list(l, workspace)
        else:
            lists = []
            print l, "is not a list!"
            
        out = []
        for sub_l in lists:
            out.append(func(sub_l))
        return self.construct_list(out, workspace)

    def handle_firsts(self, parameters, workspace):
        return self._handle_firsts_etc(self.handle_first, parameters, workspace)

    def handle_butfirsts(self, parameters, workspace):
        return self._handle_firsts_etc(self.handle_butfirst, parameters, workspace)

    def handle_lasts(self, parameters, workspace):
        return self._handle_firsts_etc(self.handle_last, parameters, workspace)

    def handle_butlasts(self, parameters, workspace):
        return self._handle_firsts_etc(self.handle_butlast, parameters, workspace)

    def handle_first(self, parameters, workspace):
        return self.first_and_last(0, parameters, workspace)

    def handle_butfirst(self, parameters, workspace):
        return self.butfirst_and_butlast([1,None], parameters, workspace)

    def handle_last(self, parameters, workspace):
        return self.first_and_last(-1, parameters, workspace)

    def handle_butlast(self, parameters, workspace):
        return self.butfirst_and_butlast([0,-1], parameters, workspace)
        
    def first_and_last(self, place, parameters, workspace):
        place = int(place)
        if self._is_word(parameters[0]):
            chars, error = self._split_word(parameters[0])
            return "\"" + chars[place]
        elif self._is_list(parameters[0]):
            words, error = self._split_list(parameters[0])
            return words[place]
        else:
            return None, "can't split "+str(parameters)

    def butfirst_and_butlast(self, places, parameters, workspace):
        splace, eplace = places
        splace = int(splace)
        eplace = int(eplace)
        if self.is_word(parameters, workspace):
            chars, error = self._split_word(parameters[0], workspace)
            return "\"" + "".join(chars[splace:eplace])
        elif self.is_list(parameters, workspace):
            words, error = self._split_list(parameters[0], workspace)
            return "["+ " ".join(words[splace:eplace]) + "]"
        else:
            return None, "can't split "+str(parameters)

    def handle_pick(self, parameters, workspace):
        if self.is_word(parameters, workspace):
            chars, error = self._split_word(parameters[0], workspace)
            return "\"" + random.choice(chars), ""
        elif self.is_list(parameters, workspace):
            words, error = self._split_list(parameters[0], workspace)
            return random.choice(words), ""
        else:
            return None, "can't split "+str(parameters)

    def handle_to(self, words_or_text, workspace, debug=False):
        if type(words_or_text) == type([]):
            words = words_or_text
        else:
            text = words_or_text
        if not self.current_proc_name:
            self.current_proc_name = words[0]
            self.workspace.procedures[words[0]] = [words[1:]] + [[]]
        elif text == "end" or text == self.HH.to_hebrew("svF"):
            if debug:
                print "Defined", self.current_proc_name
                print "Input=", self.workspace.procedures[self.current_proc_name][0]
                print "Body=\n", "\n".join(self.workspace.procedures[self.current_proc_name][1])
            self.current_proc_name = ""
        else:
            self.workspace.procedures[self.current_proc_name][1].append(text)
        return

    def handle_set_item(self, parameters):
        num, array, thing = parameters
        items, origin, error = self._split_array(array)
        items[int(num) - origin] = "[" + thing + "]"
        if origin == 1:
            new_array = "{" + " ".join(items) + "}"
        else:
            new_array = "{" + " ".join(items) + "}@"+str(origin)
        return new_array
        
    def _parse_word(self, word, workspace={}):
        w = str(word)
        if w and w[0] == "\"":
            return w[1:]
        elif w and w[-2:] == ".0":
            return w[:-2]
        else:
            return w

    def handle_fput(self, parameters, workspace={}):
        thing, l = parameters
        if self._is_word(thing):
            item = self._parse_word(thing, workspace)
        else:
            item = thing

        if self._is_word(l) and len(item) == 1:
             return self.construct_word([item, l], workspace)
        elif self.is_list(l, workspace):
            return "[" + item  + " " + l[1:-1] +"]"
        return "ERROR"

    def handle_lput(self, parameters, workspace={}):
        thing, l = parameters
        if self.is_word(thing, workspace):
            item = self._parse_word(thing, workspace)
        else:
            item = thing

        if self.is_word(l, workspace) and len(item) == 1:
             return self.construct_word([l, item], workspace)
        elif self.is_list(l, workspace):
            return "[" +  l[1:-1] + " " + item +"]"
        return "ERROR"
    
    def construct_word(self, parameters, workspace={}):
        return "\"" + ("".join([self._parse_word(p, workspace) for p in parameters]))

    def construct_list(self, parameters, workspace={}):
        l = []
        for p in parameters:
            if self._is_word(p):
                l.append(self._parse_word(p, workspace))
            elif self._is_list(p):
                l.append(p)
        return "[" + " ".join(l) + "]"
        
    def construct_sentence(self, parameters, workspace={}):
        l = []
        for p in parameters:
            if self._is_word(p):
                l.append(self._parse_word(p, workspace))
            elif self._is_list(p):
                l.append(p[1:-1])
        return "[" + " ".join(l) + "]"
        
    def construct_array(self, parameters, workspace={}):
        if len(parameters) == 2:
            size = int(parameters[0])
            origin = int(parameters[1])
        else:
            size = int(parameters[0])
            origin = 1
        if origin == 1:
            end_bracket = "}"
        else:
            end_bracket = "}@"+str(origin)
        return "{"+" ".join("[]" * size) + end_bracket
        
    def list_to_array(self, parameters, workspace={}):
        l = parameters[0]
        return "{"+l[1:-1]+"}"

    def array_to_list(self, parameters, workspace={}):
        a = parameters[0]
        if a[-1] == "}":
            end = -1
        else:
            items = a.split("}")
            temp = "}".join(items[-1])
            end = len(temp)
        return "["+a[1:end]+"]"
            
    def clear_screen(self, parameters=[], workspace={}):
        self.app.clear_screen()
        self.home()
        self.refresh_turtle_flag = True
        return True

    def clean(self, parameters=[], workspace={}):
        self.app.clear_screen()
        self.refresh_turtle_flag = True
        return True

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
            if not segment:
                self._set_turtle_position(endx, endy)
                self.refresh_turtle_flag = True
                return True
                
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
        self.app.draw_line(sx, sy, ex, ey)
        #self.area.window.draw_line(self.gc, int(round(sx)), int(round(sy)), int(round(ex)), int(round(ey)))

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

    def forward(self, parameters, workspace={}):
        distance = parameters[0]
        return self._move_distance(distance, -1)
        
    def backward(self, parameters, workspace={}):
        distance = parameters[0]
        return self._move_distance(distance, 1)
            
    def right(self, parameters, workspace={}):
        degrees = parameters[0]
        self.turtle_heading = (self.turtle_heading - degrees) % 360
        self.refresh_turtle_flag = True
        return True

    def left(self, parameters, workspace={}):
        degrees = parameters[0]
        self.turtle_heading = (self.turtle_heading + degrees) % 360
        self.refresh_turtle_flag = True
        return True
        
    def home(self, parameters=[], workspace={}):
        self._set_turtle_position(self.turtle_home_position[0], self.turtle_home_position[1])
        self.refresh_turtle_flag = True
        return True

    def set_turtle_view(self, flag, parameters={}, workspace={}):
        self.show_turtle_flag = flag
        self.refresh_turtle_flag = True
        return True
        
    def handle_turtle_query(self, parameters, workspace={}):
        query = parameters[0]
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
            return "["+str(x)+" "+str(y)+"]"
        elif query == "heading":
            return self.turtle_heading

    def towards(self, parameters, workspace={}):
        pos = parameters[0]
        tokens, error = self.tokenize(pos[1:-1])
        x, tokens, error = self.process_expression(tokens[:], workspace)
        y, tokens, error = self.process_expression(tokens[:], workspace)
        return self.handle_math("arctan", x/y)

    def set_pen_position(self, pos, parameters, workspace={}):
        self.pen_position = pos
        return True
        
    def set_pen_mode(self, mode, parameters=[], workspace={}):
        self.pen_position = PEN_DOWN
        self.pen_mode = mode
        self.app.set_pen_mode(mode)
        return True

    def set_draw_mode(self, parameters, workspace={}):
        mode = parameters[0]
        self.draw_mode = mode
        if mode == MODE_WINDOW:
            x = self._get_turtle_position()[0] % self.screen_width
            y = self._get_turtle_position()[1] % self.screen_height
            self.turtle_position = [x, y]
        return True

    def _parse_color(self, parameter, workspace={}):
        if self.is_list([parameter]) == TRUE:
            tokens, error = self.tokenize(parameter[1:-1])
            r, tokens, error = self.process_expression(tokens[:], workspace)
            g, tokens, error = self.process_expression(tokens[:], workspace)
            b, tokens, error = self.process_expression(tokens[:], workspace)
        else:
            rgb = self.BASIC_COLORS[int(parameter)]
            r = rgb[0] * 256.0
            g = rgb[1] * 256.0
            b = rgb[2] * 256.0
        return r,g,b

    def set_pen_color(self, parameters, workspace={}):
        color = parameters[0]
        r,g,b = self._parse_color(color, workspace)
        self.app.set_foreground_color(r, g, b)
        self.pen_color = color
        return True

    def set_screen_color(self, parameters, workspace={}):
        color = parameters[0]        
        r,g,b = self._parse_color(color, workspace)
        self.app.set_background_color(r, g, b)
        self.screen_color = color
        return True

    def set_heading(self, parameters, workspace={}):
        angle = parameters[0]
        self.turtle_heading = (angle + 180) % 360
        return True

    def set_x(self, parameters, workspace={}):
        x = parameters[0]
        return self._move_to_position(x + self.turtle_home_position[0], self._get_turtle_position()[1])

    def set_y(self, parameters, workspace={}):
        y = parameters[0]
        return self._move_to_position(self._get_turtle_position()[0], y + self.turtle_home_position[1])

    def set_xy(self, parameters, workspace={}):
        x, y = parameters
        return self._move_to_position(x + self.turtle_home_position[0], y + self.turtle_home_position[1])
        
    def go_to(self, parameters, workspace={}):
        pos = parameters[0]
        tokens, error = self._split_list(pos)
        x, words, error = self.process_expression(tokens[:], workspace)
        y, words, error = self.process_expression(words[:], workspace)
        return self.set_xy([int(x), int(y)], workspace)        

    def set_pen_size(self, parameters, workspace={}):
        width = self.handle_first(parameters, workspace)
        self.app.set_line_width(int(width))
        return True

    def repeat_loop(self, parameters, workspace={}):
        times, loop_body = parameters
        all_ok = True
        for i in xrange(times):
            self.current_repcount = i + 1
            all_ok = self.handle_command_line(loop_body, workspace={})
        return all_ok
        
    def for_loop(self, parameters, workspace={}):
        loop_header, loop_body = parameters
        words, error = self.tokenize(loop_header[1:-1])
        if not error:
            variable = words[0]
            start, words, error = self.process_expression(words[1:], workspace)
            end, words, error = self.process_expression(words, workspace)
            if words:
                step = None
            else:
                if end > start:
                    step = 1
                else:
                    step = -1

            workspace.names[variable] = start
            #workspace.handle_proc_input(variable, start)
            if end > start:
                while workspace.names[variable] <= end:
                    if step == None:
                        current_step, dummy, error = self.process_expression(words, workspace)
                    else:
                        current_step = step
                    all_ok = self.handle_command_line(loop_body[1:-1], workspace)
                    workspace.names[variable] = workspace.names[variable] + current_step
            else:
                while workspace.names[variable] >= end:
                    if step == None:
                        current_step, dummy, error = self.process_expression(words, workspace)
                    else:
                        current_step = step
                    all_ok = self.handle_command_line(loop_body[1:-1], workspace)
                    workspace.names[variable] = workspace.names[variable] + current_step
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
            self.app.hide_turtle(self.temp_image, startx, starty)
            self.temp_image = None
        else:
            print "Can't hide turtle"
        return True
            
    def draw_turtle(self):
        startx, starty = self._get_turtle_position()
        angle = self.turtle_heading
        head_dirx, head_diry = self._calc_dirx_and_diry(angle)
        toe1_dirx, toe1_diry = self._calc_dirx_and_diry(angle+120)
        toe2_dirx, toe2_diry = self._calc_dirx_and_diry(angle+240)
        head = [int(startx - head_dirx * 6.0), int(starty - head_diry * 6.0)]
        toe1 = [int(startx - toe1_dirx * 6.0), int(starty - toe1_diry * 6.0)]
        toe2 = [int(startx - toe2_dirx * 6.0), int(starty - toe2_diry * 6.0)]
        if self._is_visible((startx, starty)):
            self.temp_image = self.app.get_turtle_image(startx, starty)
        else:
            self.temp_image = None
        self.app.draw_turtle(head, toe1, toe2)
        return True
        
    def handle_label(self, parameters, workspace={}):
        text = parameters[0]
        startx, starty = self._get_turtle_position()
        if self._is_word(text):
           text = text[1:]
        elif self._is_list(text):
           text = text[1:-1]
        self.app.draw_label(text, startx, starty)
        return True
        
    def _get_turtle_position(self):
        return self.turtle_xposition, self.turtle_yposition
        
    def _set_turtle_position(self, x, y):
        self.turtle_xposition = x
        self.turtle_yposition = y
        
    def show_output(self, output, workspace={}):
        #Prints the input or inputs like PRINT, except that if an input is a list it is printed inside square brackets
        return self.print_output(output, mode = MODE_SHOW, workspace=workspace)

    def type_output(self, output, workspace={}):
        #Prints the input or inputs like PRINT, except that no newline character is printed at the end and multiple inputs are not separated by spaces.
        return self.print_output(output, mode = MODE_TYPE, workspace=workspace)
        
    def print_output(self, parameters, mode=MODE_PRINT, workspace={}):
        output = parameters[0]
        words, error = self.tokenize(output)
        out, words, error = self.process_expression(words[:], workspace)
        if self._is_word(out):
            out = self._parse_word(out)
        elif self._is_list(out) and (mode != MODE_SHOW):
            out = out[1:-1]
        self.output_label.set_text(str(out))
        if mode == MODE_TYPE:
            print out,
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
        self.commander = Commander(self)
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
        self.vpaned = gtk.VPaned()
        self.vpaned.add1(self.scrolled)
        self.vpaned.add2(self.textview)
        self.label = gtk.Label()
        self.entry = gtk.Entry()
        self.entry.connect("activate", self.handle_command)
        self.entry.connect("key-press-event", self.handle_keypress)
        vbox.pack_start(self.vpaned, 0,0,False)
        vbox.pack_start(self.label, 0,0,False)
        vbox.pack_start(self.entry, 0,0,False)
        self.window.add(vbox)
        self.window.show_all()
        self.set_drawing_area(self.area)
        self.commander.set_output_label(self.label)
        self.history_index = 0
        self.history_mode = False
        self.history = []
        
    def set_drawing_area(self, area):
        self.area = area
        self.style = self.area.get_style()
        self.gc = self.area.window.new_gc(foreground=None, background=None, font=None, function=-1,\
                                          fill=-1, tile=None, stipple=None, clip_mask=None, subwindow_mode=-1\
                                          ,ts_x_origin=-1, ts_y_origin=-1, clip_x_origin=-1,clip_y_origin=-1,\
                                          graphics_exposures=-1,line_width=1, line_style=-1, cap_style=-1,\
                                          join_style=-1)

    def handle_keypress(self, widget=None, event=None):
        if event.keyval == 65362: #up
            self.history_mode = True
            if self.history_index > 0:
                self.history_index = self.history_index - 1
            widget.set_text(self.history[self.history_index])
            return True
        elif event.keyval == 65364: #down
            self.history_mode = True
            self.history_index = self.history_index + 1
            if self.history_index == len(self.history):
                self.history_index = self.history_index - 1
            else:
                widget.set_text(self.history[self.history_index])
            return True
        else:
            self.history_mode = False

        
    def handle_command(self, widget=None, event=None):
        text = widget.get_text()
        all_ok = self.commander.handle_command_line(text)
        widget.set_text("")
        if self.history_mode:
            pass
        else:
            self.history.append(text)
            self.history_index = len(self.history) - 1
        self.history_mode = False
        widget.grab_focus()

    def clear_screen(self):
        self.area.window.clear()
        return True
        
    def draw_label(self, text, x, y):
        y = self._fix_y(y)
        context = self.area.get_pango_context()
        layout = pango.Layout(context)
        layout.set_text(text)
        self.area.window.draw_layout(self.gc, int(x), int(y), layout)        

    def _fix_y (self, y):
        return SCREEN_HEIGHT - y 

    def draw_turtle(self, head, toe1, toe2):
        head = (head[0], self._fix_y(head[1]))
        toe1 = (toe1[0], self._fix_y(toe1[1]))
        toe2 = (toe2[0], self._fix_y(toe2[1]))
        self.area.window.draw_polygon(self.gc, True, (head, toe1, toe2))

    def hide_turtle(self, image, startx, starty):
        starty = self._fix_y(starty)
        self.area.window.draw_image(self.gc, image, 0, 0, int(startx - 9.0), int(starty- 9.0), 20, 20)
        
    def paste_turtle(self, image, startx, starty):
        starty = self._fix_y(starty)
        self.area.window.draw_image(self.gc, image, 0, 0, int(startx - 9.0), int(starty- 9.0), 20, 20)
        
    def get_turtle_image(self, startx, starty):
        starty = self._fix_y(starty)
        return self.area.window.get_image(int(startx - 10.0), int(starty- 10.0), 20, 20) 
        
    def set_line_width(self, size):
        self.gc.line_width = size

    def set_foreground_color(self, r, g, b):
        color = gtk.gdk.Color(r, g, b)
        self.gc.set_rgb_fg_color(color) #self.gc.set_foreground(color)

    def set_background_color(self, r, g, b):
        color = gtk.gdk.Color(r, g, b)
        self.gc.set_rgb_bg_color(color) #self.gc.set_foreground(color)
        
    def set_pen_mode(self, mode):
        if mode == PEN_ERASE:
            self.gc.function = gtk.gdk.CLEAR
        elif mode == PEN_REVERSE:
            self.gc.function = gtk.gdk.INVERT
        else:
            self.gc.function = gtk.gdk.SET
        
    def draw_line(self, sx, sy, ex, ey):
        sy = self._fix_y(sy)
        ey = self._fix_y(ey)
        self.area.window.draw_line(self.gc, int(round(sx)), int(round(sy)), int(round(ex)), int(round(ey)))

    def draw_circle(self, x, y, diam):
        print "Drawing circle: x,y,diam=", x,y,diam
        print "Line width=", self.gc.line_width
        diam = int(diam)
        filled = False
        self.area.window.draw_arc(self.gc, filled, int(x - (diam/2)), int(y - (diam/2)), diam, diam, 0, 360 * 64)

    def destroy(self, event=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    app = App()
    app.main()
