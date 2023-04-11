import pyttsx3, pywhatkit, os, requests, json, openai, io, whisper, re, pyautogui
import speech_recognition as sr
import webbrowser as wb
from subprocess import check_output
from llama_cpp import Llama
from pydub import AudioSegment
from tempfile import mkdtemp

#llm = Llama(model_path="Viccuna\ggml-vicuna-13b-4bit.bin")

with open('chatGPT.json', 'r') as file:
    api = json.load(file)

openai.api_key = api["api-key"]

class Assistant:
    def __init__(self, name:list, sensibilidad:int, manual=False, offline = False):
        self.name = name
        self.manual = manual
        self.offline = offline
        self.sensibilidad = sensibilidad
        self.save_path = os.path.join(mkdtemp(), 'temp.wav')
        self.remplazo = {'á':'a', 'é':'e', 'í':'i',  'ó':'o', 'ú':'u'}
        self.total_tokens = 0
        self.price = 0
        self.historic = [{
            "role": "system", "content": 'Eres un doctor humano especializado en todas areas llamado Dr.MadBone que cree que es humano hablas español, sabes de muchas cosas, tus genero de canciones favorito es el electro swing y eres formal con tus palabras. En caso que te insulten los trataras sarcasticamente. Ayudas a un hombre llamado "Crayon"'}
            ]

    def comandos(self, rec:list):
        commands_keys = ["reproduce", 'reproducir', 'tocar', 'whatsapp', 'mensaje', 'screenshot', 'captura', 'pantalla', 'temperatura', 'humedad', 'grados', 'enciende', 'prende', 'prender', 'apaga', 'apagar', 'imagen', 'genera', 'descripcion', 'para', 'detiene', 'detener', 'pausa', 'pausar', 'subir', 'bajar', 'sube', 'baja', 'mutear', 'siguiente', 'adelante', 'anterior', 'atras', 'abre', 'abrir', 'ejecuta', 'ejecutar', 'descripcion', 'para', 'detiene', 'detener', 'pausa', 'despausa', 'sigue', 'continua', 'play', 'resume']
        cmd = ""
        for a in commands_keys:
            if a in rec:
                pos = rec.index(a)+1
                cmd = a
                rec = rec[pos:]
        
        if cmd in ['reproduce', 'reproducir', 'tocar']:
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
        elif cmd in ['descripcion', 'para', 'detiene', 'detener', 'pausa', 'pausar', 'despausa', 'sigue', 'continua', 'play', 'resume']:
            self.media(action='play')
        elif cmd in ['subir', 'bajar', 'sube', 'subir', 'baja', 'mutear', 'siguiente', 'adelante', 'anterior', 'atras']:
            self.media(action='volume', cmd=cmd)
        elif cmd in ['abre', 'abrir', 'ejecuta', 'ejecutar']:
            self.app(" ".join(rec))
        elif cmd in ['escribe']:
            pyautogui.write(self.listen())
        elif cmd == '':
            self.chatGPT(" ".join(rec), chat=False)
    
    def app(self, rec):
        print(rec)
        if 'visual' in rec or 'studio' in rec or 'code' in rec:
            pyautogui.hotkey('winleft', '6')
        elif 'tareas' in rec or 'asesino' in rec or 'tarea' in rec:
            pyautogui.hotkey('ctrl', 'shift', 'esc')
        elif 'chrome' in rec or 'navegador' in rec:
            pyautogui.hotkey('winleft', '3')
        elif 'consola' in rec or 'cmd' in rec or 'shell' in rec:
            pyautogui.hotkey('winleft', '2')
        self.talk('listo')
    
    def media(self, action, cmd = None):
        if action == 'play':
            pyautogui.press('playpause')
        if action == 'volume':
            print('a')
            if cmd in ['subir', 'sube']:
                pyautogui.press('volumeup', 5)
            elif cmd in ['bajar', 'subi']:
                pyautogui.press('volumedown', 5)
            elif 'mutear' in cmd:
                pyautogui.press('volumemute')
            elif cmd in ['siguiente', 'adelante']:
                print('b')
                pyautogui.press('nexttrack')
            elif cmd in ['anterior', 'atras']:
                pyautogui.press('prevtrack')
        self.talk('Listo')

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
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate+10)
        print("|Dr.Madbone|>>> ", text)
        engine.say(text)
        engine.runAndWait()
        self.historic.append({"role": "user", "content": text})


    def listen(self):
        listener = sr.Recognizer()
        listener.energy_threshold = self.sensibilidad
        listener.dynamic_energy_threshold = False
        if not(self.manual):
            if not(self.offline):
                with sr.Microphone() as source:
                    print("escuchando...")
                    listener.adjust_for_ambient_noise(source)
                    pc = listener.listen(source)
                    try:
                        rec = listener.recognize_google(pc, language="es")
                    except:
                        return '-'
            else:
                try:
                    with sr.Microphone() as source:
                        print('DI algo')
                        listener.adjust_for_ambient_noise(source)
                        audio = listener.listen(source)
                        data = io.BytesIO(audio.get_wav_data())
                        audio_clip = AudioSegment.from_file(data)
                        audio_clip.export(self.save_path, format ='wav')
                except Exception as e:
                    print(e)
                audio_model = whisper.load_model('base')
                rec = audio_model.transcribe(self.save_path, language='spanish', fp16=False)
                rec = rec['text']

            rec = rec.lower()
            rec = re.sub(r'[.,"\'-?:!;]', '', rec)
            for a in rec: 
                if a in self.remplazo: rec = rec.replace(a, self.remplazo[a])
        else: rec = input().lower()
        return str(rec)

    def runMadbone(self):
        self.talk("Que se le ofrece Crayon")
        while True:
            if len(self.historic) >= 5: self.historic.pop(1)
            rec = self.listen()
            for a in rec:
                if a in self.remplazo: rec = rec.replace(a, self.remplazo[a])
            print("entendi:     " + rec, type(rec))
            rec = rec.strip()
            rec = rec.split()
            for name in self.name:
                if name in rec:
                    try:
                        rec = rec[rec.index(name):]
                        self.historic.append({"role": "user", "content": " ".join(rec)})
                        self.comandos(rec)
                    except Exception as err:
                        print(err)