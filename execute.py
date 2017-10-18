import StringIO
import os.path
import pycurl
import os
import difflib
import linecache
import RPi.GPIO as GPIO
import time
from PIL import Image,ImageDraw

index = "00"
name = "no name"
room_no = "000"
floor_no="0"
wing = "0"
more_rooms = "0"
prof_name1 = ""
(x12,x11,x10,x13) = (605,553,400,450)
(y12,y11,y10,y13) = (802,805,778,145)
(y22,y21,y20,y23) = (802,805,778,145)
(y32,y31,y30) = (491,494,638)
(y42,y41,y40) = (394,400,472)
(y52,y51,y50) = (394,400,472)
(y62,y61,y60) = (491,494,316)
(y72,y71,y70) = (70,80,125)
(y82,y81,y80) = (70,80,125)
((a12,b12),(a11,b11),(a10,b10),(a13,b13)) = ((533,491),(483,494),(400,778),(390,20))
GPIO.setmode(GPIO.BCM)
GPIO.setup(14,GPIO.IN,pull_up_down =GPIO.PUD_UP)
GPIO.setup(15,GPIO.IN,pull_up_down =GPIO.PUD_UP)
button14 = GPIO.input(14)
button15 = GPIO.input(15)



# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
GPIO.setwarnings(False)

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False	

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def main(s1,s2):
  # Main program block

  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7


  # Initialise display
  lcd_init()
	

    # Send some test
  lcd_string(s1,LCD_LINE_1)
  lcd_string(s2,LCD_LINE_2)

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0F,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
def speech_to_text():
	os.system("arecord -D plughw:0,0 -f cd -t wav -d 4 -q -r 16000 | flac - -s -f --best --sample-rate 16000 -o daveconroy.flac")
	print "Recording Audio .. press Ctrl+C to exit"
	#variables
	filename = 'daveconroy.flac'
	key = '' #Subsitute Google API key
	url = 'https://www.google.com/speech-api/v2/recognize?output=json&lang=en-in&key=' + key

	#send the file to google speech api
	c = pycurl.Curl()
	c.setopt(pycurl.VERBOSE, 0)
	c.setopt(pycurl.URL, url)
	fout = StringIO.StringIO()
	c.setopt(pycurl.WRITEFUNCTION, fout.write)

	c.setopt(pycurl.POST, 1)
	c.setopt(pycurl.HTTPHEADER, ['Content-Type: audio/x-flac; rate=16000'])

	filesize = os.path.getsize(filename)
	c.setopt(pycurl.POSTFIELDSIZE, filesize)
	fin = open(filename, 'rb')
	c.setopt(pycurl.READFUNCTION, fin.read)
	c.perform()

	response_code = c.getinfo(pycurl.RESPONSE_CODE)
	response_data = fout.getvalue()

	#since google replies with mutliple json strings, the built in python json decoders dont work well
	#print response_data
	start_loc = response_data.find("transcript")
	tempstr = response_data[start_loc+13:]
	end_loc = tempstr.find("\"")
	final_result = tempstr[:end_loc]
	c.close()
	print final_result
	return final_result

def bt_detect():
	bt_str1 = "obexftp --nopath --noconn --uuid none --bluetooth "
	bt_str2 = " --channel 12 -p "
	filename = "/home/pi/Desktop/Final/Direction.png"
	optemp2 = []
	nametemp = []
	outp = os.popen('hcitool scan').read()
	optemp1 = outp.split()
	optemp1 = optemp1[2:]
	for p in optemp1:
		if(len(p) > 6):
			if(p[2] == ':' and p[5] == ':'):
				optemp2.append(p)
			else:
				nametemp.append(p)
		else:
			nametemp.append(p)
	nametemp = nametemp[2:]
	print nametemp
	for k in range(len(optemp2)):
		os.system(bt_str1 + optemp2[k] + bt_str2 + filename)

def fetch_data():
	f1 = open("room_number.txt",'r')
	proflist = f1.readlines()
	for i in range(len(proflist)-1):
		proflist[i] = proflist[i][:-1]
	
	tosearch = speech_to_text()
	
	print "To Search"
	print tosearch
	if(len(difflib.get_close_matches(tosearch,proflist,1,cutoff = 0.3)) == 0):
		vars1 = "Didn't Get that , try again. A room number works better!"
		vars1 = vars1.replace(" ","%20")
		os.system("omxplayer -noconsolecontrols \"http://translate.google.com/translate_tts?tl=en&q=" + vars1 + "\"")
		return ""
	matched_prof = difflib.get_close_matches(tosearch,proflist,1,cutoff = 0.3)[0]
	print "Matched Prof"
	print matched_prof
	index = matched_prof[0:3]
	print "index"
	print index
	prof_name = matched_prof[4:]
	#print prof_name
	if(index[1] == '0' and index[0] == '0'):
		index = index[-1]
	elif(index[0] == '0'):
		index = index[1:]
	print "indices"
	print index
	print eval(index)
	line = linecache.getline('Room&ProfData.txt',eval(index)+1)
	line = line[:-1]
	prof_name1 = line[14:]
	print "data from file"
	print prof_name1
	print "Final Line"
	print line
	return line
#fetch_data()

def speak_out():
#Going Up
	floor_com_str1 = "Go straight and climb up first the stairs to "
	if(floor_num == 1) :floor_str = "first floor"
	elif(floor_num == 2) :floor_str = "second floor"
	elif(floor_num == 3) :
		floor_com_str2 = "Go straight and climb up the second stairs to Mezzanine floor "
#Choosing wing

	if(floor_num == 1 or floor_num == 2):	
		if(wing_num == 1):
			wing_str = "Turn right and walk till last corridor then take left"
		elif(wing_num == 2):	
			wing_str = "Turn right and walk till last corridor then take right"
		elif(wing_num == 3):
			wing_str = "Turn right"
		elif(wing_num == 4):
			wing_str = "Turn left and walk till first corridor on the right"
		elif(wing_num == 5):
			wing_str = "Turn left and walk till first corridor on the left"
		elif(wing_num == 6):
			wing_str = "Turn left and walk till next stairs"
		elif(wing_num == 7):
			wing_str = "Turn left and walk till end of corridor and turn right"
		elif(wing_num == 8):
			wing_str = "Turn left and walk till end of corridor and turn left"
	elif(floor_num == 0):
		floor_str = ""
		if(wing_num == 1):
			wing_str = "Turn right"
		elif(wing_num == 2):
			wing_str = "Turn left"
		elif(wing_num == 3):
			wing_str = "Go straight"
		elif(wing_num == 4):
			wing_str = "Go straight and turn left to the first corridor"
		elif(wing_num == 5):
			wing_str = "Go straight till the stairs on the left"
		elif(wing_num == 6):
			wing_str = "Go straight till the end of corridor and then turn right"
		elif(wing_num == 7):
			wing_str = "Go straight till the end of corridor and then turn left"
	elif(floor_num == 3):
		floor_str = ""
		if(wing_num == 1):
			wing_str = "Turn right and take left corridor"
		elif(wing_num == 2):
			wing_str = "Turn right and take right corridor"
#Choosing room in a wing
	room_com_str1 = "Its "
	room_com_str2 = "room "
	if(room_num == 1):
		room_str = "first"
	elif(room_num == 2):
		room_str = "second"
	elif(room_num == 3):
		room_str = "third"
	elif(room_num == 4):
		room_str = "fourth"
	elif(room_num == 5):
		room_str = "fifth"
	elif(room_num == 6):
		room_str = "sixth"
	elif(room_num == 7):
		room_str = "seventh"
	elif(room_num == 8):
		room_str = "eighth"
	elif(room_num == -3):
		room_str = "third last"
	elif(room_num == -2):
		room_str = "second last"
	elif(room_num == -1 or room_num ==0):
		room_str = "last"
#Choosing L/R
	if(l_or_r == 'L') : l_or_r_str = "to your left"
	elif(l_or_r == 'R'): l_or_r_str = "to your right"
	elif(l_or_r == 'Z') :l_or_r_str = "straight ahead"

	if(floor_num == 3):
		vars1 = floor_com_str2
	elif(floor_num == 0):
		vars1 = ""
	else:
		vars1 = floor_com_str1 + floor_str
	vars = vars1 + ". "+ wing_str +". "+ room_com_str1 + room_str + room_com_str2 + l_or_r_str
	vars1 = vars1.replace(' ',"%20")
	vars2 = wing_str.replace(' ',"%20")
	vars3 = room_com_str1 + room_str + room_com_str2 + l_or_r_str
	vars3 = vars3.replace(' ',"%20")
	os.system("omxplayer -noconsolecontrols \"http://translate.google.com/translate_tts?tl=en&q=" + vars1 + "\"")
	os.system("omxplayer -noconsolecontrols \"http://translate.google.com/translate_tts?tl=en&q=" + vars2 + "\"")
	os.system("omxplayer -noconsolecontrols \"http://translate.google.com/translate_tts?tl=en&q=" + vars3 + "\"")
	a = open("Direction.txt",'w')
	a.close()
	print "File Saved!!"
GPIO.setup(14,GPIO.IN,pull_up_down =GPIO.PUD_UP)
k = 1

def ImageGenerator(data):
	if(floor_num == 0):
		im = Image.open('ground.png')
	elif(floor_num == 1):
		im = Image.open('floor1.png')
	elif(floor_num == 2):
		im = Image.open('floor3.png')
	elif(floor_num == 3):
		im = Image.open('mezzanine.png')
	draw = ImageDraw.Draw(im)
	rx = data.split()[-2]
	ry = data.split()[-1]
	roomx = eval(rx)
	roomy = eval(ry)
	if(floor_num == 1):
		(x1,y1,y2,y3,y4,y5,y6,y7,y8,a1,b1) = (x11,y11,y21,y31,y41,y51,y61,y71,y81,a11,b11)
	elif(floor_num == 2):
		(x1,y1,y2,y3,y4,y5,y6,y7,y8,a1,b1) = (x12,y12,y22,y32,y42,y52,y62,y72,y82,a12,b12)
	elif(floor_num == 0):
		(x1,y1,y2,y3,y4,y5,y6,y7,y8,a1,b1) = (x10,y10,y20,y30,y40,y50,y60,y70,y80,a10,b10)
	elif(floor_num == 3):
		(x1,y1,y2,a1,b1) = (x13,y13,y23,a13,b13)
	draw.line((a1,b1,x1,b1),fill = (0,0,255),width=10)
	if(wing_num==1): 
		draw.line((x1,b1,x1,y1),fill = (0,0,255),width=10)
		draw.line((x1,y1,roomx,y1),fill = (0,0,255),width=10)
		draw.line((roomx,y1,roomx,roomy),fill = (0,0,255),width=10)
	elif(wing_num==2): 
		draw.line((x1,b1,x1,y2),fill = (0,0,255),width=10)
		draw.line((x1,y2,roomx,y2),fill = (0,0,255),width=10)
		draw.line((roomx,y2,roomx,roomy),fill = (0,0,255),width=10)
	elif(wing_num==3): 
		draw.line((x1,b1,x1,roomy),fill = (0,0,255),width=10)
		draw.line((x1,roomy,roomx,roomy),fill = (0,0,255),width=10)
	elif(wing_num==4): 
		draw.line((x1,b1,x1,y4),fill = (0,0,255),width=10)
		draw.line((x1,y4,roomx,y4),fill = (0,0,255),width=10)
		draw.line((roomx,y4,roomx,roomy),fill = (0,0,255),width=10)
	elif(wing_num==5): 
		draw.line((x1,b1,x1,y5),fill = (0,0,255),width=10)
		draw.line((x1,y5,roomx,y5),fill = (0,0,255),width=10)
		draw.line((roomx,y5,roomx,roomy),fill = (0,0,255),width=10)
	elif(wing_num==6): 
		draw.line((x1,b1,x1,roomy),fill = (0,0,255),width=10)
		draw.line((x1,roomy,roomx,roomy),fill = (0,0,255),width=10)
	elif(wing_num==7): 
		draw.line((x1,b1,x1,y7),fill = (0,0,255),width=10)
		draw.line((x1,y7,roomx,y7),fill = (0,0,255),width=10)
		draw.line((roomx,y7,roomx,roomy),fill = (0,0,255),width=10)
	elif(wing_num==8): 
		draw.line((x1,b1,x1,y8),fill = (0,0,255),width=10)
		draw.line((x1,y8,roomx,y8),fill = (0,0,255),width=10)
		draw.line((roomx,y8,roomx,roomy),fill = (0,0,255),width=10)
	im.save('Direction.png')


while True:
	input_state = GPIO.input(14)
	present = time.gmtime().tm_sec + time.gmtime().tm_min*60
	if(input_state == button14):
		a = 2
		print "in false"
	if (input_state != (button14)):
		k = 2
		start = time.gmtime().tm_sec + time.gmtime().tm_min*60
		print "in state 2"
		main("Welcome To Elec.","Engineering Dept")
		os.system("omxplayer -noconsolecontrols \"http://translate.google.com/translate_tts?tl=en&q=Welcome+to+Department+of+Electrical+Engineering%2ESpeakout+a+Professor's+Name+or+Room+number\"")
		print "in last"
		k = 3
		data = fetch_data()
		if(data != ""):
			linetemp = data[4:12]
			prof_name1 = data[13:]
			lcd_byte(0x01,LCD_CMD)
			if(prof_name1[5] == ' '):
				lcd_byte(0x01,LCD_CMD)
				lcd_string(prof_name1[:6],LCD_LINE_1)
				lcd_string(prof_name1[6:],LCD_LINE_2)
			else:
				lcd_byte(0x01,LCD_CMD)
				lcd_string(prof_name1[:4],LCD_LINE_1)
				lcd_string(prof_name1[4:],LCD_LINE_2)
			cord = linetemp.split()
			floor_num = eval(cord[0])
			wing_num = eval(cord[1])
			l_or_r = cord[2]
			room_num = eval(cord[3])
			print room_num
			ImageGenerator(data)
			speak_out()
			message = "Do you want me to send the instructions through Bluetooth ?"
			message = message.replace(" ","%20")
			os.system("omxplayer -noconsolecontrols \"http://translate.google.com/translate_tts?tl=en&q=" + message + "\"")
			while True:
				input_state1 = GPIO.input(14)
				input_state2 = GPIO.input(15)
				if(input_state1 == button14):
					bt_detect()
					break
				elif(input_state2 != button15):
					break	
		button14 = GPIO.input(14)
		button15 = GPIO.input(15)