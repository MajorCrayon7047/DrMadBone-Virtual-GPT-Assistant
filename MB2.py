from AssistantClass import Assistant

name = ["madbone", 'bone', 'mad', 'boom']
sensibilidad = 4000
mb = Assistant(name, sensibilidad, manual=True)

mb.runMadbone()