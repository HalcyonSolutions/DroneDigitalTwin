import numpy as np
def calculate_distance(P1, P2):
    P1 = np.array(P1)
    P2 = np.array(P2)
    return np.sqrt(np.sum((P1 - P2)**2))
    


text="""
45.0, 17.0, -16.0; 36.0, 17.0, -16.0;34.0, 19.0, -18.0;32.0, 21.0, -20.0;30.0, 23.0, -22.0;28.0, 25.0, -24.0;25.0, 27.0, -24.0;22.0, 30.0, -24.0;19.0, 33.0, -24.0;16.0, 36.0, -24.0;13.0, 39.0, -24.0;10.0, 42.0, -24.0;7.0, 45.0, -24.0;4.0, 48.0, -24.0;1.0, 51.0, -24.0;-2.0, 54.0, -24.0;-5.0, 57.0, -24.0;-8.0, 60.0, -24.0;-11.0, 63.0, -24.0;-14.0, 66.0, -24.0;-17.0, 69.0, -24.0;-20.0, 71.0, -24.0;-23.0, 71.0, -24.0;-26.0, 72.0, -25.0;-29.0, 72.0, -25.0;-32.0, 72.0, -25.0;-35.0, 72.0, -25.0;-38.0, 72.0, -25.0;-41.0, 72.0, -25.0;-43.0, 74.0, -27.0;-46.0, 75.0, -28.0;-50.0, 76.0, -25.0
"""
text = text.strip().replace(" ","").split(";")

new_set = []
prev_x=0
prev_y=0
prev_z=0
distance = 20
for i, NED in enumerate(text):
    x, y, z = NED.split(",")
    x = float(x)
    y = float(y)
    z = float(z)
    
    if i != 0:
        P1 = [x,y,z]
        P2 = [prev_x, prev_y, prev_z]
        if calculate_distance(P1, P2) < distance:
            continue
        
    new_set.append(f"{x},{y},{z}")
    prev_x = x
    prev_y = y
    prev_z = z

new_text = ";".join(new_set)
print("The new text:")
print(new_text)
