from AssistantClass import Assistant

name = ["madbone", 'bone', 'mad', 'boom', 'doc', 'doctor']
sensibilidad = 4000
mb = Assistant(name, sensibilidad, manual = False)

mb.runMadbone()