import os
import sys
import soundcard as sc
import soundfile as sf
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
import threading
from PIL import Image, ImageTk
import numpy as np
import time

class recorder():
    def __init__(self):
    
        self.root = tk.Tk()
        self.root.title("Recorder")
        self.root.iconbitmap(default=self.resourcePath("images/icon.ico"))
        self.root.resizable(width=False, height=False)        
        self.is_on = False
        self.is_saving = False
        
        on_img = Image.open(self.resourcePath("images/switch_on.png"))                                                
        on_img = on_img.resize((int(on_img.width*(180/on_img.height)), int(on_img.height*(180/on_img.height))))        
        self.on = ImageTk.PhotoImage(on_img)
        
        off_img = Image.open(self.resourcePath("images/switch_off.png"))                                             
        off_img = off_img.resize((int(off_img.width*(180/off_img.height)), int(off_img.height*(180/off_img.height))))        
        self.off = ImageTk.PhotoImage(off_img)    
        
        self.speaker_name = sc.default_speaker().name
        self.mic_name = sc.default_microphone().name

        self.radio_val=tk.IntVar() 

        frame1 = ttk.Frame(self.root)
        frame1.grid(row = 0, column = 0, columnspan=2, sticky=(tk.N,tk.W,tk.E,tk.S))
        frame2 = ttk.Frame(self.root)
        frame2.grid(row = 1, column = 0, columnspan=2, sticky=(tk.N,tk.W,tk.E,tk.S))
        frame3 = ttk.Frame(self.root)
        frame3.grid(row = 2, column = 0, columnspan=2)

        
        self.r_button_speaker = tk.Radiobutton(frame1,value=0,variable=self.radio_val,text="Speaker", command=self.set_combo_device)
        self.r_button_mic = tk.Radiobutton(frame1,value=1,variable=self.radio_val,text="Mic", command=self.set_combo_device)
        
        devices = self.get_devices()
        
        self.combo = ttk.Combobox(frame2,values=devices, postcommand=self.set_combo_device)
        self.combo.bind("<<ComboboxSelected>>",self.combo_selected)
        self.combo.set(self.speaker_name)
        
        self.button = tk.Button(frame3, image=self.off, bd = 0, command=self.click)
       
        self.r_button_speaker.grid(row=0,column=0)
        self.r_button_mic.grid(row=0,column=1)    
        self.combo.grid()
        
        self.button.grid()
        
        self.set_combo_device()
        
        self.root.protocol("WM_DELETE_WINDOW", self.close_main)
        self.root.mainloop()

    def get_devices(self):
        if self.radio_val.get() == 0:
            return sc.all_speakers()
        else:
            return sc.all_microphones()

    def set_combo_device(self):
        devices = self.get_devices()
        
        devices_name = [d.name for d in devices]
        devices_id = [d.id for d in devices]
        self.combo.configure(values=devices_name)
        
        if self.radio_val.get() == 0:
            self.combo.set(self.speaker_name)
            
        else:
            self.combo.set(self.mic_name)
            
        index = self.combo.current()
        
        if index == -1:
            self.set_default_device()
            
            if self.radio_val.get() == 0:
                self.combo.set(self.speaker_name)
                
            else:
                self.combo.set(self.mic_name)            

        self.id = devices_id[index]
    
    def set_default_device(self):
        if self.radio_val.get() == 0:        
            self.speaker_name = sc.default_speaker().name
        else:
            self.mic_name = sc.default_microphone().name

    def combo_selected(self,event):
    
        if self.radio_val.get() == 0:
            self.speaker_name = self.combo.get()
        else:
            self.mic_name = self.combo.get()
        
        self.set_combo_device()
    
    def get_id_and_name(self):
        if self.radio_val.get() == 0:
            device = sc.get_speaker(id=self.speaker_name)
        else:
            device = sc.get_microphone(id=self.mic_name)
            
        return device.id, device.name

    def click(self):
        if self.is_on:
            self.button.config(image = self.off)
            self.rec_stop()
            self.is_on = False
            
        else:
            self.button.config(image = self.on)
            self.rec_thread = threading.Thread(target=self.rec_start, daemon=True)
            self.rec_thread.start()
            self.is_on = True
                  
    def rec_start(self):
        self.data = np.empty(0)
        self.is_recording = True

        def get_recorded_data(self):
            blocks = []
            
            try:
                with sc.get_microphone(id=self.id, include_loopback=True).recorder(samplerate=48000) as r:
                    
                    while self.is_recording and self.id == id:
                        block = r._record_chunk()
                        
                        if block is None:
                            time.sleep(1)
                            
                            break
                        else:
                            blocks.append(block)
   
            except:
                pass
            
            if blocks != []:
                data = np.reshape(np.concatenate(blocks), [-1, len(set(r.channelmap))])
                self.data = np.r_[self.data,data[:, 0]]

        while self.is_recording:
            self.set_combo_device()
            id, name = self.get_id_and_name()
            get_recorded_data(self)
        
    def rec_stop(self):
        self.is_recording = False
        self.is_saving = True
        self.rec_thread.join()
        self.ask_filename()
        try:
            sf.write(file=self.filename, data=self.data, samplerate=48000)
            tk.messagebox.showinfo("Complete",f"Save as {self.filename}")
        except:
            pass
        self.r_button_mic.configure(state="normal")
        self.r_button_speaker.configure(state="normal")
        
        del self.data
        
        self.is_saving = False
            
    def ask_filename(self):
        work_path = os.path.dirname(sys.executable)
        self.filename = filedialog.asksaveasfilename(
            title = "Save as",
            filetypes = [("wav", ".wav")],
            initialdir = work_path+"\\", 
            defaultextension = "wav"
            )
    
    def close_main(self): 
        if self.is_saving:
            tk.messagebox.showerror("Error","Now saving")
        else:
            self.root.destroy()

    def resourcePath(self,filename):
      if hasattr(sys, "_MEIPASS"):
          return os.path.join(sys._MEIPASS, filename)
      return os.path.join(filename)

if __name__=="__main__":
    recorder()
    