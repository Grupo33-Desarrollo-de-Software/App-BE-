from background_task import background

@background(schedule=5)
def taskNotificaciones():
    print("hola mundo")
