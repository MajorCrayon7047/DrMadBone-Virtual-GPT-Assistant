import pyttsx3, pywhatkit, os, requests
import speech_recognition as sr
from subprocess import check_output

class Assistant:
    def __init__(self, name:list, sensibilidad:int, manual=False):
        self.name = name
        self.manual = manual
        self.listener = sr.Recognizer()
        self.listener.energy_threshold = sensibilidad
        self.listener.dynamic_energy_threshold = False
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.remplazo = {'á':'a', 'é':'e', 'í':'i',  'ó':'o', 'ú':'u'}

    def comandos(self, rec:list):
        commands_keys = ["reproduce", 'reproducir', 'cancion', 'tocar', 'whatsapp', 'mensaje', 'screenshot', 'captura', 'pantalla', 'temperatura', 'humedad', 'grados', 'enciende', 'prende', 'prender', 'apaga', 'apagar']
        cmd = ""
        for a in commands_keys:
            if a in rec:
                pos = rec.index(a)+1
                cmd = a
                rec = rec[pos:]
        
        if cmd in ['reproduce', 'reproducir', 'cancion', 'tocar']:
            self.reproduce(" ".join(rec))
        elif cmd in ['whatsapp', 'mensaje']:
            self.whatsapp()
        elif cmd in ['screenshot', 'captura', 'pantalla']:
            self.captura()
        elif cmd in ['temperatura', 'humedad', 'grados']:
            self.meteorologia()
        elif cmd in ['enciende', 'prende', 'prender', 'apaga', 'apagar']:
            self.domotica(cmd, rec)
        elif cmd == '': self.talk('Lo siento no entendi que es lo que habias dicho')

    def reproduce(self, rec):
        print(f"Reproduciendo {rec}")
        self.talk(f"Reproduciendo {rec}")
        pywhatkit.playonyt(rec)
    
    def whatsapp(self, msg='', quien=''):
        if msg == '' and quien == '':
            if pywhatkit.open_web(): self.talk("Whatsapp web abierto")

    def captura(self):
        pywhatkit.take_screenshot("MB_screenshot", show=False)
        self.talk('Captura de pantalla tomada con exito... quiere ver la captura?')
        rec = self.listen()
        if 'si' in rec: check_output(os.getcwd()+f'/MB_screenshot.png', shell=True)
        else: pass

    def meteorologia(self):
        res = requests.get('https://emetec.wetec.um.edu.ar/temp')
        data = res.json()
        temp, hum = data['temp'], data['hum']
        self.talk(f'La temperatura actualmente es de {temp} grados y la humedad es del {hum}%')

    def domotica(self, cmd, rec:list):
        if cmd in ['enciende', 'prende', 'prender']: estado = 'ON'
        else: estado = 'OFF'

        if 'circuito' in rec and not('goteo' in rec):   #PONE UN EXPECT CONECTION ERROR
            num = 0
            for a in rec[rec.index('circuito')+1:]:
                if a.isdigit():
                    if int(a)>3: 
                        self.talk('actualmente solo hay 3 circuitos disponibles, porfavor repita el comando con un numero valido')
                        return
                    num = a
            print(f'http://192.168.54.200/?c{num}="{estado}"')
            if estado == 'ON': self.talk(f'Encendiendo el circuito {num} de riego')
            else: self.talk(f'Apagando el circuito {num} de riego')
            requests.get(f'http://192.168.54.200/?c{num}="{estado}"')
        if 'goteo' in rec:
            print(f'http://192.168.54.200/?g="{estado}"')
            if estado == 'ON': self.talk('Encendiendo el sistema de goteo.')
            else: self.talk('Apagando el sistema de goteo.')
            requests.get(f'http://192.168.54.200/?g="{estado}"')
        if 'rutina' in rec:
            print(f'http://192.168.54.200/?rutine={estado}')
            if estado == 'ON': self.talk('Encendiendo la rutina del sistema de riego.')
            else: self.talk('Apagando la rutina del sistema de riego.')
            requests.get(f'http://192.168.54.200/?rutine="{estado}"')

    def talk(self, text):
        print(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        if not(self.manual):
            try:
                with sr.Microphone() as source:
                    print("escuchando...")
                    self.listener.adjust_for_ambient_noise(source)
                    pc = self.listener.listen(source)
                    rec = self.listener.recognize_google(pc, language="es")
                    rec = rec.lower()
                    for a in rec: 
                        if a in self.remplazo: rec = rec.replace(a, self.remplazo[a])
            except:
                pass
        else: rec = input()
        return rec

    def runMadbone(self):
        self.talk("Despertado y listo para ayudar.")
        while True:
            rec = self.listen()
            for a in rec:
                if a in self.remplazo: rec = rec.replace(a, self.remplazo[a])
            print("entendi:     " + rec)
            for n in self.name:
                if n in rec:
                    rec = rec.strip().split()
                    rec = rec[(rec.index(n)+1):]
                    self.comandos(rec)