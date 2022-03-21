import re
import musicalbeeps
import time

# variables generales
newlist = []
tokens = []
position = 0

while True:
    try:
        filename = input("Introduce el nombre del archivo (no se te olvide agregar el .txt): ")
        textfile = open(filename, 'r')
        break
    except FileNotFoundError:
        print("Not an existing file, try again")

lines = textfile.readlines()

# Se eliminan lineas que comienzan con "#"
newlist = [x for x in lines if not x.startswith("#")]

# Se sustituye el valor de cambio de línea por el símbolo "$" 
final = []
for y in newlist:
    new = y.replace("\n", ' $')
    final.append(new)

textfile.close()

# Asignación de expresiones regulares
VOICE = "([_a-zA-z][_a-zA-z0-9]){1,31}"
NEWLINE = "(\$)"
NOTE = "(((A|B|C|D|E|F|G)|((A|B|C|D|E|F|G)(#*|b*))(-2|-1|0|1|2|3|4|5|6|7|8))|(R))(((w|h|q|e|s|t|f)((t|3|5|7|9)|(\.)*)))(\s)*"
EXPDR = "\|"

# Función para tocar notas a apartir de musicalbeeps
def playMusic():
    textfile = open(filename, 'r')
    filetext = textfile.read()
    textfile.close()

    player = musicalbeeps.Player(volume = 0.3, mute_output = False)

    title = '(?:\#TITLE [^\n]*)'
    songName = re.findall(title, filetext)
    if(songName):
        piece = songName[0].split('#TITLE')[1]
        print("Music Piece Title: " + piece)
        print("\n")


    mnote = "((((A|B|C|D|E|F|G)(#*|b*))(-2|-1|0|1|2|3|4|5|6|7|8))|(R))(((w|h|q|e|s|t|f)((t|3|5|7|9)|(\.)*)))"
    notes = re.findall(mnote, filetext)


    for i in notes:
        letter = i[3]
        octave = i[5]
        accidental = i[4]

        if(i[9]== "w"):
            tvalue = 4
        elif(i[9] == "h"):  
            tvalue = 2
        elif(i[9] == "q"):
            tvalue = 1
        elif(i[9] == "e"):
            tvalue = 0.5
        elif(i[9] == "s"):
            tvalue = 0.25
        elif(i[9] == "t"):
            tvalue = 3
        elif(i[9] == "f"):
            tvalue = 0.75

        timeModifier = 1
        if(i[11] == "t"):
            timeModifier = 0.6
        elif(i[11] == "5"):
            timeModifier = 0.8
        elif(i[11] == "7"):
            timeModifier = 0.85
        elif(i[11] == "9"):
            timeModifier = 0.88
        elif(i[12].startswith(".")):
            timeModifier = 1.5


        if(i[0] == "R"):
            letter = "pause"

        final = letter + octave + accidental
        print(final, tvalue, timeModifier)
        player.play_note(final, tvalue * timeModifier)
        
    bar = '(?:\#BAR)'
    end = re.findall(bar, filetext)
    if(bar):
        print("A measure ends here, bye!")
        exit()

# Asignación de tokens 
# <----- Comienza método de descenso recursivo ----->

note_token = 11
voice_token = 10
pipe_token = 12
newLine_token = 33
unknown_token = 13

for i in final:
    for j in i.split():
        if(re.match(NOTE, j)):
            tokens.append(note_token)
        elif(re.match(VOICE, j)):
            tokens.append(voice_token)
        elif(re.fullmatch(EXPDR, j)):
            tokens.append(pipe_token)
        elif(re.match(NEWLINE, j)):
            tokens.append(newLine_token)
        else:
            tokens.append(unknown_token)

# Inicio de secuencia de descenso recursivo
def data():
    global position

    if(tokens[position] == voice_token):
        match(voice_token)
        noteline()
    else:
        print("Las líneas de datos deben de comenzar con un identificador VOICE")
        exit()

def noteline():
    global position

    if(tokens[position] == note_token):
        match(note_token)
        note1()
    else:
        print("Se esperaba una NOTE")
        return

def pipe():
    global position
    if(tokens[position] == pipe_token):
        print("Se esperaba una NOTE o NEWLINE")
        exit()
    else:
        return

def note1():
    global position

    if(tokens[position] == note_token):
        match(note_token)
        note1()
    elif(tokens[position] == pipe_token):
        match(pipe_token)
        pipe()
        note1()
    elif(tokens[position] == newLine_token):
        match(newLine_token)
        data()
    else:
        if(tokens[position] == unknown_token):
            print("Lexema desconocido, se esperaba una NOTE o '|' ")
        elif(tokens[position] == voice_token):
            print("Se detectó un identificador de voz, se esperaba una NOTE o '|' ")
        else:
            print("Se esperaba una NOTE o '|' ")
            
        return


def match(t):
    global position
    if(tokens[position] == t):
        if(t == 11):
            lexema = "NOTE"
            print("Lexema aceptado: ", lexema, " ", t)
        elif(t == 12):
            lexema = "PIPE"
            print("Lexema aceptado: ", lexema, " ", t)
        elif(t == 10):
            lexema = "VOICE identifier"
            print("Lexema aceptado: ", lexema, " ", t)
        elif(t == 33):
            lexema = "New Line ---"
            print("Lexema aceptado: ", lexema, " ", t)
        time.sleep(0.2)
        position += 1
        return
    
try:    
    data()
except IndexError:
    pass

if(tokens[position-1] == 33):
    print("Sintaxis correcta")
    playMusic()
else:
    print("Linea mal construida")
