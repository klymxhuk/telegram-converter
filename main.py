import json
import os
from kivy.config import Config
Config.set("graphics", "resizable", 1)
Config.set("graphics", "width", 800)
Config.set("graphics", "height", 600)
Config.write()
import re
import asyncio
from telethon import TelegramClient
if __name__ == '__main__':
    from kivy.properties import ObjectProperty
    from kivymd.uix.button import MDFlatButton
    from kivymd.uix.dialog import MDDialog
    from kivy.core.window import Window
    from kivy.lang import Builder
    from kivy.properties import StringProperty
    from kivymd.app import MDApp
    from kivymd.uix.filemanager import MDFileManager
    from kivymd.toast import toast
    from kivy.uix.boxlayout import BoxLayout
    from kivy.clock import Clock, _default_time as time
import subprocess
import multiprocessing

STATUS = ''
T_STATUS = 0

def mul(path,cs, compres, out_res):
    only_path = path.split('.')[0]
    if not os.path.exists(f"{only_path}.mp4"):
        if not out_res:
            s = subprocess.Popen(f'c:\\Converter\\bin\\ffmpeg.exe -i  {path}',
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in iter(s.stdout.readline, b''):
                n = line.find('Video')
                if n != -1:
                    resolution = re.findall("(\d+x\d+,)", line)[0].split('x')[0]
                    print(line)
                    print(resolution)
                    break
            s.stdout.close()
            if not compres:
                if int(resolution) <= 2000:
                    command = f'c:\\Converter\\bin\\ffmpeg.exe -hwaccel qsv -i {path} -c:v libx265  -preset ultrafast -b:v 1000k -y -c:a aac -b:a 128k {only_path}.mp4'
                else:
                    #s = subprocess.Popen(f'c:\\Converter\\bin\\ffmpeg.exe -i {path} -preset ultrafast -crf 35 -y -c:a aac -b:a 128k {only_path}.mp4',
                    command = f'c:\\Converter\\bin\\ffmpeg.exe -hwaccel qsv -i {path} -c:v libx265  -preset ultrafast -b:v 1300k -y -c:a aac -b:a 128k {only_path}.mp4'
            else:
                if int(resolution) <= 2000:
                    command = f'c:\\Converter\\bin\\ffmpeg.exe -hwaccel qsv -i {path} -preset ultrafast -b:v 2700k -y -c:a aac -b:a 128k {only_path}.mp4'
                else:
                    command = f'c:\\Converter\\bin\\ffmpeg.exe -hwaccel qsv -i {path} -preset ultrafast -b:v 1900k -y -c:a aac -b:a 128k {only_path}.mp4'
        else:
            if not compres:
                command = f'c:\\Converter\\bin\\ffmpeg.exe -hwaccel qsv -i {path} -c:v libx265  -preset ultrafast -b:v 700k -s 1280x720 -y -c:a aac -b:a 128k {only_path}.mp4'
            else:
                command = f'c:\\Converter\\bin\\ffmpeg.exe -hwaccel qsv -i {path} -preset ultrafast -b:v 1200k -s 1280x720 -y -c:a aac -b:a 128k {only_path}.mp4'


        s = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        sec = 0
        for line in iter(s.stdout.readline, b''):
            print(line)
            if s.poll() == 0 and line == '':
                cs.value = -1
                break
            n = line.find('time')
            if n != -1:
                time = line[n + 5:n + 16]
                time_s = time.split('.')
                time = time_s[0].split(':')
                sec = (int(time[-3])*3600)+(int(time[-2])*60)+(int(time[-1]))
            cs.value = sec
        s.stdout.close()
    else:
        cs.value = -1


def telegram (path, st):
    if os.path.isdir("c:\\Converter\\") and os.path.exists("c:\\Converter\\config.txt"):
        with open('c:\\Converter\\config.txt', 'r', encoding="utf-8") as f:
            config_array = json.loads(f.read())
        api_hash = config_array['telegram']['token']
        api_id = config_array['telegram']['id_client1']
        resive_name = config_array['telegram']['id_client2']

        new_path = path.split('.')[0]+'.mp4'
        temp = new_path.split('\\')[-1].split('_')
        temp_date = temp[1].split('-')
        camera_namber = temp[0]
        start_date = f'{temp_date[0][6:8]}-{temp_date[0][4:6]}-{temp_date[0][0:4]}'
        time_interval = f'{temp_date[1][0:2]}:{temp_date[1][2:4]}:{temp_date[1][4:6]}-{temp_date[-1][0:2]}:{temp_date[-1][2:4]}:{temp_date[-1][4:6]}'
        camera_with_time = f'{camera_namber}  {start_date}   {time_interval}'
        
        def callback(current, total):
            print('Uploaded', current, 'out of', total,
                  'bytes: {:.2%}'.format(current / total))
            print(int(current/(total/100)))
            st.value = int(current/(total/100))
        
        try:
            #api_id = 17526613
            #api_hash = '72bd0764fc7d834d34181db4c125feb4'
            async def tel():
                async with TelegramClient('Session', api_id, api_hash) as client:
                    await client.send_file(resive_name,
                                           new_path,
                                           video_note=True,  progress_callback=callback, caption=camera_with_time)
            asyncio.run(tel())
        except:
            st.value = -2
        else:
            st.value = -1
        os.remove(new_path)
    
def proc_manager(path, mode, compres=False, out_res=False):
    if mode == 'converter':
        global STATUS
        STATUS = multiprocessing.Value('i', 0)
        a = multiprocessing.Process(target=mul, args=(path,STATUS,compres, out_res))
        a.start()
    if mode == 'telegram':
        global T_STATUS
        T_STATUS = multiprocessing.Value('i',0)
        a = multiprocessing.Process(target=telegram, args=(path, T_STATUS))
        a.start()


KV = '''
MDBoxLayout:
    id: MainBox
    orientation: 'vertical'
    MDToolbar:
        pos_hint: {"top": 1}
        title: "Отправка видео в телeграм"
        left_action_items: [['menu', lambda x: app.button_config()]]
        right_action_items: [["folder", lambda x: app.file_manager_open()]]
        elevation: 10
    MDBoxLayout:
        pos_hint: {'top': 1}
        orientation: 'vertical'
        size_hint_y: None
        height: 10
        MDProgressBar:
            id: Progress
            value: 0
            color: 1,0,0,0.6
    MDBoxLayout:
        id: File_box
        pos_hint: {'top': 1}
        orientation: 'vertical'


<File_to_send>
    OneLineAvatarIconListItem:
        pos_hint: {'top': 1}
        text: root.file_name
        IconLeftWidget:
            icon: "movie-open-remove"
            on_release: app.button_del_file(root)
        IconRightWidget:
            icon: "send"
            on_release: app.button_send(root, self)
            theme_text_color: "Custom"
            text_color: "#311021"
<Config_Box>
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    MDTextField:
        id: token
        size_hint_y: None
        height: 70
        #multiline: True
        hint_text: "Введите api hash"
    MDTextField:
        size_hint_y: None
        height: 70
        id: id_client1
        hint_text: "Введите api id"
    MDTextField:
        size_hint_y: None
        height: 70
        id: id_client2
        hint_text: "Введитя имя получателя"
    MDLabel:
        text: "Настройка кодирования видео \\n(по умолчанию H265, оригинальное разрешение)"
        #bold: True
        #font_style: "H5"
        adaptive_size: True
        spacing: "8dp"

    MDBoxLayout:
        id: chip_box
        adaptive_size: True
        padding: 20
        spacing: "8dp"

        MDChip:
            id: compres
            #selected_chip_color: app.theme_cls.primary_color
            text: "H264"
            active: False
            md_bg_color: app.theme_cls.primary_light
            on_release: app.press_property(self)
            elevation: 12
                
        MDChip:
            id: resolution
            text: "HD"
            check: True
            active: False
            md_bg_color: app.theme_cls.primary_light
            on_release: app.press_property(self)
            elevation: 12

        
                    

<Button_ok>
    text: 'OK'
    on_release: app.save_config(root.instance)

<Button_cancel>
    text: 'ОТМЕНА'
    on_release: app.dialog.dismiss()
'''

if __name__ == '__main__':
    class Button_ok(MDFlatButton):
        instance = ObjectProperty()


    class Button_cancel(MDFlatButton):
        pass

    class File_to_send (BoxLayout):
        file_name = StringProperty()
        file_path = StringProperty()

    class Config_Box (BoxLayout):
        config_array = StringProperty()

    class ConverterApp(MDApp):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.config_array = 0
            self.choose_file = 0
            self.interval = 0
            self.loop = 0
            self.dialog = None
            self.menu = None

            Window.bind(on_keyboard=self.events)
            self.manager_open = False
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.select_path,

            )

        def build(self):
            return Builder.load_string(KV)


        def update_status(self, *args):
            global STATUS
            global T_STATUS
            if STATUS != '':
                if STATUS.value !=-1:
                    self.root.ids.Progress.color = (1,0,0,1)
                    print(STATUS.value)
                    print(self.interval)
                    value_progress = (STATUS.value*100)/self.interval
                    print(value_progress)
                    self.root.ids.Progress.value = value_progress
                    if value_progress >= 98:
                        toast("Конвертация видео закончена")
                else:
                    self.root.ids.Progress.value = 100

                    if T_STATUS == 0:
                        self.root.ids.Progress.value = 0
                        self.root.ids.Progress.color = self.theme_cls.primary_color
                        toast("Начало отправки видео в телеграм")
                        proc_manager(self.choose_file, 'telegram')
                    elif T_STATUS.value == -1:
                        self.root.ids.Progress.value = 100
                        self.loop.cancel()
                        toast("Отправка выполнена")
                        self.root.ids.File_box.clear_widgets()
                        self.root.ids.Progress.value = 0
                        self.choose_file = 0
                        self.interval = 0
                        T_STATUS = 0
                        STATUS = ''
                    elif T_STATUS.value == -2:
                        STATUS = ''
                        T_STATUS = 0
                        self.root.ids.Progress.value = 0
                        toast("Нет интернета")
                    else:
                        self.root.ids.Progress.value = T_STATUS.value


        def button_config(self):
            self.dialog = MDDialog(
                type="custom",
                title= 'Настройки для телеграм',
                content_cls=Config_Box(),
                text="Config",
                buttons=[
                    Button_ok(instance=self.dialog),
                    Button_cancel(),
                ],
            )
            if os.path.exists("c:\\Converter\\config.txt"):
                self.dialog.content_cls.ids.token.text = self.config_array['telegram']['token']
                self.dialog.content_cls.ids.id_client1.text = self.config_array['telegram']['id_client1']
                self.dialog.content_cls.ids.id_client2.text = self.config_array['telegram']['id_client2']
                if self.config_array['compres']:
                    self.dialog.content_cls.ids.compres.active = self.config_array['compres']
                    self.dialog.content_cls.ids.compres.md_bg_color = self.theme_cls.primary_color
                if self.config_array['resolution']:
                    self.dialog.content_cls.ids.resolution.active = self.config_array['resolution']
                    self.dialog.content_cls.ids.resolution.md_bg_color = self.theme_cls.primary_color
            self.dialog.open()


        def save_config(self, instance):
            print(self.dialog.content_cls.ids.token.text)
            if not os.path.isdir("c:\\Converter\\"):
                os.mkdir("c:\\Converter\\")
            if not os.path.exists("c:\\Converter\\config.txt"):
                config_array = {'current_path': self.config_array['current_path'],
                                'telegram' : {'token': self.dialog.content_cls.ids.token.text,
                                            'id_client1': self.dialog.content_cls.ids.id_client1.text,
                                            'id_client2': self.dialog.content_cls.ids.id_client2.text},
                                'compres' : self.dialog.content_cls.ids.compres.active,
                                'resolution': self.dialog.content_cls.ids.resolution.active
                                }
                with open('c:\\Converter\\config.txt', 'w', encoding="utf-8") as f:
                    json.dump(config_array, f, ensure_ascii=False)
            else:
                with open('c:\\Converter\\config.txt', 'r', encoding="utf-8") as f:
                    config_array = json.loads(f.read())
                config_array['telegram'] = {'token': self.dialog.content_cls.ids.token.text,
                                            'id_client1': self.dialog.content_cls.ids.id_client1.text,
                                            'id_client2': self.dialog.content_cls.ids.id_client2.text}
                config_array['compres'] = self.dialog.content_cls.ids.compres.active
                config_array['resolution'] = self.dialog.content_cls.ids.resolution.active

                with open('c:\\Converter\\config.txt', 'w', encoding="utf-8") as f:
                    json.dump(config_array, f, ensure_ascii=False)
            self.on_start()
            self.dialog.dismiss()

        def button_del_file(self, instance):
            self.root.ids.File_box.clear_widgets()
            self.root.ids.Progress.value = 0
            self.choose_file = 0
            self.interval = 0

        def button_send(self, instance, icon):
            time = instance.file_name.split('.')[0].split('_')[1].split('-')
            toast("Начало конвертации видео")
            icon.text_color = self.theme_cls.primary_color
            start_time = time[1]
            end_time = time[-1]
            self.interval = (int(end_time[0:2])*3600+int(end_time[2:4])*60+int(end_time[4:6]))-(int(start_time[0:2])*3600+int(start_time[2:4])*60+int(start_time[4:6]))
            self.choose_file = instance.file_path
            proc_manager(instance.file_path, 'converter', self.config_array['compres'], self.config_array['resolution'])
            self.loop = Clock.schedule_interval(self.update_status, 1)

        def on_start(self):
            if os.path.isdir("c:\\Converter\\") and os.path.exists("c:\\Converter\\config.txt"):
                with open('c:\\Converter\\config.txt', 'r', encoding="utf-8") as f:
                    self.config_array = json.loads(f.read())
                api_hash = self.config_array['telegram']['token']
                api_id = self.config_array['telegram']['id_client1'] 
                async def tel():
                    async with TelegramClient('Session', api_id, api_hash) as client:
                        await client.connect()
                asyncio.run(tel())
            else:
                self.config_array = {'current_path':"d:\\"}



        def on_stop(self):
            if not os.path.isdir("c:\\Converter\\"):
                os.mkdir("c:\\Converter\\")
            if not os.path.exists("c:\\Converter\\config.txt"):
                config_array = {'current_path': self.file_manager.current_path,
                                'telegram':''}
                with open('c:\\Converter\\config.txt', 'w', encoding="utf-8") as f:
                    json.dump(config_array, f, ensure_ascii=False)
            else:
                with open('c:\\Converter\\config.txt', 'r', encoding="utf-8") as f:
                    config_array = json.loads(f.read())
                config_array['current_path'] = self.file_manager.current_path
                with open('c:\\Converter\\config.txt', 'w', encoding="utf-8") as f:
                    json.dump(config_array, f, ensure_ascii=False)

        def file_manager_open(self):

            self.file_manager.show(self.config_array['current_path'])  # output manager to the screen
            self.manager_open = True

        def select_path(self, path):
            '''It will be called when you click on the file name
            or the catalog selection button.

            :type path: str;
            :param path: path to the selected directory or file;
            '''
            try:
                extention_file = path.split('.')[1]
            except:
                self.exit_manager()
            else:
                if extention_file == 'avi':
                    self.exit_manager()
                    self.root.ids.File_box.clear_widgets()
                    self.root.ids.File_box.add_widget(File_to_send(file_name=path.split('\\')[-1], file_path=path))
                else:
                    toast('Файл не поддерживается')

        def exit_manager(self, *args):
            '''Called when the user reaches the root of the directory tree.'''

            self.manager_open = False
            self.file_manager.close()

        def events(self, instance, keyboard, keycode, text, modifiers):
            '''Called when buttons are pressed on the mobile device.'''

            if keyboard in (1001, 27):
                if self.manager_open:
                    self.file_manager.back()
            return True

        def press_property(self, instance):
            if  instance.active:
                
                #instance.active = True
                instance.md_bg_color = self.theme_cls.primary_color
                
            else:
                instance.md_bg_color = self.theme_cls.primary_light
                #instance.active = False
                
               


if __name__ == '__main__':
    ConverterApp().run()