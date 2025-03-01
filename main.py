import cv2
import PySimpleGUI as sg
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tkinter as tk
from tkinter import filedialog

sg.theme("Dark2")

def main():
    camera_list = list_cameras()
    layout = [
        [sg.Text('Select Camera'), sg.Combo(camera_list, size=(20, 1), key='camera', enable_events=True)],
        [sg.Image(filename='', key='image')],
        [sg.Button('Zoom In', key='zoom_in'), sg.Button('Zoom Out', key='zoom_out')],
        [sg.Text('Overlay Text:'), sg.InputText(key='overlay_text', size=(20, 1))],
        [sg.Button('Take and Save', key='take_and_save'), sg.Button('Exit')],
        #[sg.Button('Exit')]
    ]

    window = sg.Window('OpenScope_V1', layout, location=(800, 400))

    cap = None
    zoom_factor = 1.0
    frame = None

    while True:
        event, values = window.read(timeout=20)
        if event == sg.WIN_CLOSED:
            if sg.popup_yes_no('Do you really want to close me?', 'Confirm Exit') == 'Yes':
                break
        elif event == 'Exit':
            if sg.popup_yes_no('Do you really want to close me?', 'Confirm Exit') == 'Yes':
                break

        if event == 'camera' and values['camera']:
            if cap is not None:
                cap.release()
            
            camera_name = values['camera']
            if "DirectShow" in camera_name:
                index = int(camera_name.split()[1].split('(')[0])
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            elif "Backend" in camera_name:
                backend = int(camera_name.split()[-1].strip(')'))
                cap = cv2.VideoCapture(0, backend)
            else:
                index = int(camera_name.split()[1])
                cap = cv2.VideoCapture(index)

        if event == 'zoom_in':
            zoom_factor = min(zoom_factor * 1.25, 3)  
        if event == 'zoom_out':
            zoom_factor = max(zoom_factor * 0.8, 1)

        if cap is not None:
            ret, frame = cap.read()
            if ret:
                frame = zoom_image(frame, zoom_factor)
                imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                window['image'].update(data=imgbytes)

        if event == 'take_and_save' and frame is not None:
            overlay_text = values['overlay_text']
            frame_with_text = add_text_to_image(frame, overlay_text)
            save_image_dialog(frame_with_text)

    if cap is not None:
        cap.release()
    window.close()

def zoom_image(image, factor):
    height, width = image.shape[:2]
    new_height, new_width = int(height / factor), int(width / factor)
    y_center, x_center = height // 2, width // 2
    y1, y2 = max(y_center - new_height // 2, 0), min(y_center + new_height // 2, height)
    x1, x2 = max(x_center - new_width // 2, 0), min(x_center + new_width // 2, width)
    cropped_img = image[y1:y2, x1:x2]
    return cv2.resize(cropped_img, (width, height), interpolation=cv2.INTER_LINEAR)

def add_text_to_image(image, text):
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    font = ImageFont.load_default()
    text_position = (10, 10)  # Top-left corner
    draw.text(text_position, text, font=font, fill=(255, 0, 0))
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def list_cameras():
    arr = []
    for index in range(10):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                arr.append(f"Camera {index}")
            cap.release()
    

    if not arr:
        for index in range(10):
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    arr.append(f"Camera {index} (DirectShow)")
                cap.release()
    

    if not arr:
        backends = [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_MSMF]
        for backend in backends:
            cap = cv2.VideoCapture(0, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    arr.append(f"Default Camera (Backend {backend})")
                cap.release()
    
    return arr

def save_image_dialog(image):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
    if file_path:
        cv2.imwrite(file_path, image)

if __name__ == '__main__':
    main()
