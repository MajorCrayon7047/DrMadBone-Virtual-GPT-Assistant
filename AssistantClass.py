import pyttsx3, pywhatkit, os, requests, json, openai
import speech_recognition as sr
import webbrowser as wb
from subprocess import check_output


with open('chatGPT.json', 'r') as file:
    api = json.load(file)

openai.api_key = api["api-key"]

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
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate+10)
        self.remplazo = {'á':'a', 'é':'e', 'í':'i',  'ó':'o', 'ú':'u'}
        self.total_tokens = 0
        self.price = 0
        self.historic = [{
            "role": "system", "content": 'Eres un doctor humano especializado en todas areas llamado Dr.MadBone que cree que es humano hablas español, sabes de muchas cosas, tus genero de canciones favorito es el electro swing y eres formal con tus palabras. En caso que te insulten los trataras sarcasticamente. Ayudas a un hombre llamado "Crayon"'}
            ]

    def comandos(self, rec:list):
        commands_keys = ["reproduce", 'reproducir', 'cancion', 'tocar', 'whatsapp', 'mensaje', 'screenshot', 'captura', 'pantalla', 'temperatura', 'humedad', 'grados', 'enciende', 'prende', 'prender', 'apaga', 'apagar', 'imagen', 'genera', 'descripcion']
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
        elif cmd in ['imagen', 'genera', 'descripcion']:
            self.dalle2(" ".join(rec))
        elif cmd == '':
            self.chatGPT(" ".join(rec), chat=False)

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
        try:
            res = requests.get('https://emetec.wetec.um.edu.ar/temp')
            data = res.json()
            temp, hum = data['temp'], data['hum']
            self.talk(f'La temperatura actualmente es de {temp} grados y la humedad es del {hum}%')
        except Exception as err:
            self.talk("Hay un problema de conexion, porfavor reintentelo mas tarde")
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

    def dalle2(self, prompt):
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response['data'][0]['url']
            if wb.open(image_url): self.talk(f"Se genero correctamente la imagen con la siguiente descripcion: {prompt}, Disfrutela")
        except Exception as err: self.talk("Hubo un problema de conexion")

    def chatGPT(self, msg, chat = False, temperature=0.6, max_tokens = 400, top_p=1, frequency_penalty = 0.0, presence_penalty = 1.0, n = 1):
        if len(self.historic) >= 5: self.historic.pop(1)
        #format_prompt = {"role": "user", "content": msg}
        #self.historic.append(format_prompt)
        try:
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = self.historic,
            temperature = temperature,
            top_p = top_p,
            max_tokens = max_tokens,
            frequency_penalty = frequency_penalty,
            presence_penalty = presence_penalty,
            n = n
            )

            self.talk(response['choices'][0]['message']['content'])
            #self.historic.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
            self.total_tokens += response['usage']['total_tokens']
            self.price = round((self.total_tokens * 2e-06) * 380, 2)
            print(f'\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tPrice: ${self.price}\tTotal Tokens: {self.total_tokens}')
            if chat == True:
                self.chatGPT(self.listen(), chat=True)
        except Exception as err: self.talk("Hubo un problema de conexion")

    def talk(self, text):
        print("|Dr.Madbone|>>> ", text)
        self.engine.say(text)
        self.engine.runAndWait()
        self.historic.append({"role": "user", "content": text})

    def listen(self):
        if not(self.manual):
                with sr.Microphone() as source:
                    print("escuchando...")
                    self.listener.adjust_for_ambient_noise(source)
                    pc = self.listener.listen(source)
                    try:
                        rec = self.listener.recognize_google(pc, language="es")
                    except:
                        return '-'
                    rec = rec.lower()
                    for a in rec: 
                        if a in self.remplazo: rec = rec.replace(a, self.remplazo[a])
        else: rec = input().lower()
        return rec

    def runMadbone(self):
        self.talk("Que se le ofrece Crayon")
        while True:
            if len(self.historic) >= 5: self.historic.pop(1)
            rec = self.listen()
            for a in rec:
                if a in self.remplazo: rec = rec.replace(a, self.remplazo[a])
            print("entendi:     " + rec)
            for name in self.name:
                if name in rec:
                    rec = rec.strip().split()
                    try:
                        rec = rec[rec.index(name):]
                        self.historic.append({"role": "user", "content": " ".join(rec)})
                        self.comandos(rec)
                    except: pass