import py5
import math
from processing.sound import SoundFile, Waveform, Amplitude, FFT
#Documentation
#MichalKapaczA00035927
#Selection menu and rhytmn game
#This project shows a menu selection for different songs that i like to play a song you will need to click on the album cover
#Once a song starts playing a game depedning on the songs amp readings begans where you need to hover over the sqaures to destroy them
#im really proud of my circular waveform and the cubes spawning depending on the amps
#if the sqaures hit the middle image dr house house three times then the game stops.
#Controls
#Mouse left click on album cover to select song
# Space = pause and unpause
# B = back to the main menu
# Mouse hover to destroy cubes
#Requirtment breakdown
#1 Variables : I used variables to store x and y values for different objects, speed, aswell as  score and live value of the player
#2 Drawing with code : the cubes that spawn in from the different angles are spawned in using py5.rect with the value depedningso n the amp and  sqaure sizew varaible
#3 loops : used to draw menu covers, titles
#4 If statements : used to for spawning cubes from the directions depending on the amp of the song
#5 Lists : used for song dictionaries that include their titles, cover and background image, color, and amp range
#6 Interactivity : the code reacts to the users inputs of the space bar aswell as b which pause or unpause the music and go back to the selection menu.
#7 Sound : i created a waveform that reacts to the songs bass(FFT)
#testing : during the creation of my code i tested alot of different amp readings base of what i was getting from print(amp) until i was happy with the  the spawning of the cubes. i also tested a few different songs but some of them had amps that were similair for a good bit of the song which made it really boring when spawning the cubes.

#songdictionary
songs = [
    {"title": "Pierce the Veil - Circles", "file": "Circles.mp3", "cover": "Circles.png", "back": "pierceback.jpeg","amp_ranges": [0.21, 0.245, 0.275], "color": [255, 0, 0]},
    {"title": "Origami Angels - 666 flags", "file": "666.mp3", "cover": "city.png", "back": "origamiback.jpg","amp_ranges": [0.22, 0.25, 0.28], "color": [255, 100, 0]},
    {"title": "Title Fight - Numb but i still feel it", "file": "Numb.mp3", "cover": "floralg.png", "back": "TTback.jpg","amp_ranges": [0.2, 0.23, 0.26], "color": [0, 100, 0]},
    {"title": "Hatsune Miky and Kasane Teto - Mesmirizer", "file": "tetomiku.mp3", "cover": "mesmirize.jpg", "back": "mtback.jpg","amp_ranges": [0.2, 0.25, 0.28], "color": [128, 0, 128]},

]
#soundstuff
current_index = -1
soundfile = None
waveform = None
amplitude = None
fft = None
paused = False

#Menu+musicplayerbackgroundimg
cover_size = 150
hover_size = 175
spacing = 50
scroll_offset = 0
album_covers = []
background_img = []

#Cubeandplayerstats [] -- {]
spawn_interval = 60
square_size = 40
speed = 7.5
hit_radius = 25
score = 0
notes = []
lives = 3

#loadsthealbumcovers
def setup():
    global album_covers, background_img, base
    py5.size(900, 900)
    py5.rect_mode(py5.CENTER)
    py5.text_align(py5.LEFT, py5.CENTER)
    base = py5.load_image("Base.png")
    for song in songs:
        try:
            img = py5.load_image(song['cover'])
            album_covers.append(img)
        except:
            album_covers.append(None)
        try:
            bg = py5.load_image(song['back'])
            background_img.append(bg)
        except:
            background_img.append(None)

#drawsmenuorsongpayerdependingontheindex
def draw():
    py5.background(0)
    if current_index == -1:
        draw_menu()
    else:
        draw_player()

def in_destroy_zone(x, y, size):
    cx = 450
    cy = 450
    half = size / 2

    return (
        x > cx - half and
        x < cx + half and
        y > cy - half and
        y < cy + half
    )

#Textsizeandaligning
def set_text_style(size=16, align_x=py5.LEFT, align_y=py5.CENTER):
    py5.text_size(size)
    py5.text_align(align_x, align_y)

#Menuforalbums
def draw_menu():
    set_text_style()
    py5.fill(255)

    y_pos = spacing - scroll_offset + cover_size / 2
    x_pos = spacing + cover_size / 2

    for i, song in enumerate(songs):
        img = album_covers[i]
        img_size = cover_size

        #albumsbecomebiggerwhenhoveredover
        if img and (x_pos - hover_size/2 <= py5.mouse_x <= x_pos + hover_size/2 and
                    y_pos - hover_size/2 <= py5.mouse_y <= y_pos + hover_size/2):
            img_size = hover_size

        if i == current_index:
            py5.stroke(200, 200, 255)
            py5.stroke_weight(3)
            py5.rect(x_pos, y_pos, img_size+10, img_size+10)
            py5.no_stroke()

        if img:
            py5.image(img, x_pos - img_size/2, y_pos - img_size/2, img_size, img_size)

        py5.text(song['title'], x_pos + img_size/2 + 20, y_pos)
        y_pos += cover_size + spacing
        py5.text("DO NOT LET THE CUBES REACH DR.HOUSE HOUSE", 500, 100)
        py5.text("OR YOU WILL LOSE", 500, 150)
#clicktoplay
def mouse_pressed():
    global current_index, paused
    if current_index == -1:
        y_pos = spacing - scroll_offset + cover_size / 2
        for i, img in enumerate(album_covers):
            if img and (y_pos - hover_size/2 <= py5.mouse_y <= y_pos + hover_size/2):
                current_index = i
                paused = False
                load_song(current_index)
                break
            y_pos += cover_size + spacing

#keysthatpress
def key_pressed():
    global current_index, paused, lives, score
    if current_index != -1 and soundfile:
        #pause
        if py5.key == ' ':
            paused = not paused
            soundfile.amp(0 if paused else 0.3)
        #gobacktomenu
        elif py5.key.lower() == 'b':
            soundfile.stop()
            current_index = -1
            paused = False
            lives= 3
            score = 0
            notes.clear()

#loadnadplaysongs
def load_song(index):
    global soundfile, amplitude, waveform, paused, FFT
    if soundfile:
        soundfile.stop()
    paused = False
    file_path = songs[index]['file']
    soundfile = SoundFile(py5.get_current_sketch(), file_path)
    soundfile.play()
    soundfile.amp(0.3)

    amplitude = Amplitude(py5.get_current_sketch())
    amplitude.input(soundfile)
    waveform = Waveform(py5.get_current_sketch(), 512)
    waveform.input(soundfile)
    fft = FFT(py5.get_current_sketch(), 512)
    fft.input(soundfile)
#playnextsong
def next_song():
    global current_index
    current_index = (current_index + 1) % len(songs)
    load_song(current_index)

#playprevioussong
def previous_song():
    global current_index
    current_index = (current_index - 1) % len(songs)
    load_song(current_index)


def spawn_note():
        global current_index
        if paused or current_index == -1:  #dontspawnifpaused
            return
        
        amp = amplitude.analyze()
        t1, t2, t3 = songs[current_index]["amp_ranges"]
        #spawnbasedonamplituderanges
        x, y = 0, 0
        if  0.17 < amp < t1:
            x = 0
            y = 0
        elif t1 <= amp < t2:
            x = 900
            y = 0
        
        elif t2 <= amp < t3:
            x = 0
            y = 900

        elif amp > t3:
            x = 900
            y = 900

        #aimatthecentreofthecanvas
        dx = 450 - x
        dy = 450 - y
        d = math.hypot(dx, dy)
        if d == 0:
            d = 0.01

        vx = (dx / d) * speed
        vy = (dy / d) * speed

        notes.append({"x": x, "y": y, "vx": vx, "vy": vy, "hit": False})
def update_notes():
        global score, lives, current_index, paused  
        mx, my = py5.mouse_x, py5.mouse_y
        for note in notes:
            if note["hit"]:
                continue

            note["x"] += note["vx"]
            note["y"] += note["vy"]

            if "angle" not in note:
                note["angle"] = 0
            note["angle"] += 0.1
            #drawthesquares
            py5.push_matrix()
            py5.translate(note["x"], note["y"])
            py5.rotate(note["angle"])
            cube_color = songs[current_index]["color"]
            py5.fill(*cube_color)
            py5.rect(0, 0, square_size, square_size)
            py5.pop_matrix()
            #hovertohit
            if (abs(note["x"] - mx) < hit_radius and
                abs(note["y"] - my) < hit_radius):
                note["hit"] = True
                score += 100

        #removecubesthathavebeenhit
        notes[:] = [n for n in notes if not n["hit"]]
        for note in notes[:]:
            note["x"] += note["vx"]
            note["y"] += note["vy"]

        #destroycubewheninthedestroyzoneandtakeaway1lifepoint
            if in_destroy_zone(note["x"], note["y"], square_size):
                notes.remove(note)
                lives -= 1
        if lives == 0:
            soundfile.stop()
            current_index = -1
            paused = False
            lives= 3
            score = 0
            notes.clear()
def draw_player():
    global current_index, base
    py5.background(0)

    if current_index != -1 and background_img[current_index]:
        py5.image(background_img[current_index], 0, 0, py5.width, py5.height)

    #songtitle
    set_text_style(24, py5.CENTER, py5.CENTER)
    c1, c2, c3 = songs[current_index]["color"]
    py5.fill(c1, c2, c3)
    py5.stroke(0)
    py5.text(songs[current_index]['title'], py5.width/2, 60)
    py5.image(base, (900 - 100) / 2, (900 - 100) / 2)
    #waveform
    if waveform and amplitude and soundfile:
    #color
        cube_color = songs[current_index]["color"]
        py5.stroke(*cube_color)
        py5.stroke_weight(2)
    
    #centerandradius
        cx, cy = py5.width / 2, py5.height / 2
        base_radius = 150       # base circle size
        scale = 100             # how far the circle reacts to sound
    
    #updateampandwaveform
        fft.analyze()
        if not paused:
            waveform.analyze()
    
        num_points = len(waveform.data)
    
    #drawthecircularwaveform
        for i, val in enumerate(waveform.data):
            angle = py5.remap(i, 0, num_points, 0, 2 * math.pi)  # distribute around circle
            r = base_radius + val * scale                          # radius affected by waveform
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            py5.point(x, y)


    
    #notesfunctioncalled
    if py5.frame_count % 30 == 0:   #spawnrate
        spawn_note()

    update_notes()

    #textforscoreandlives
    c1, c2, c3 = songs[current_index]["color"]
    py5.fill(c1, c2, c3)
    py5.text(f"Score: {score}", 750, 100)
    py5.text(f"Lives: {lives}", 750, 150)

    #textforcontrols
    set_text_style(16, py5.CENTER, py5.CENTER)
    py5.text("SPACE = Play/Pause |  B = Menu",
             py5.width/2, py5.height - 40)
py5.run_sketch()