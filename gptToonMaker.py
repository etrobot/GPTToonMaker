import pygame
import cv2
import os,csv
from datetime import datetime
import azure.cognitiveservices.speech as speechsdk
from mutagen.mp3 import MP3
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')


def generate_dict(path:str) -> dict:
    '''
    iter the img folder and make a dict of images path
    :param path:
    :return {
        folder_name(charater):
            {sub_folder_name(body_or_face):
                {sub_sub_folder_name(action_type):[frame1, frame2,...]}
            }
        }:
    '''
    result = {}
    for name in os.listdir(path):
        if name.endswith('.DS_Store'):
            continue
        subpath = os.path.join(path, name)
        if os.path.isdir(subpath):
            result[name] = generate_dict(subpath)
        else:
            result =[pygame.image.load(os.path.join(path, x)).convert_alpha() for x in os.listdir(path) if not x.endswith('.DS_Store')]
            break
    return result

def dealScript() -> list:
    '''
    deal the scripts for the animation
    :param script csv path:
    :return [character, start frame, direction to L or R, end frame,body action, face action,]:
    '''
    result = []

    with open('script.csv', 'r') as file:
        script = csv.reader(file)

        voices={'A':'zh-CN-XiaoshuangNeural','B':'zh-CN-XiaoyouNeural'}
        frameNum = 0
        gap = 20
        facing=1
        for line in script:
            if len(line)==8:
                result.append(line)
                continue
            line.insert(1, 'idle')
            line.insert(1,facing)
            facing=-1
            # if len(line[-1])<2:
            #     continue
            audioFile = 'audio/'+str(int(datetime.now().timestamp()))+".mp3"
            text2voice(line[-1],voices[line[0]],audioFile)
            line.append(audioFile)
            audioLen = round(MP3(audioFile).info.length-1,1)
            print(audioLen)
            frameNum += gap
            line.insert(1,frameNum)
            frameNum = int(frameNum + audioLen*gap)
            line.insert(2, frameNum)
            result.append(line)

    with open('script.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in result:
            writer.writerow(row)

    return result


def text2voice(text:str,voice:str,filename='audio/result.mp3'):
    speech_config = speechsdk.SpeechConfig(subscription=os.environ["TTS"], region="eastasia")
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = voice
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_synthesizer.speak_text_async(text).get()
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized to speaker for text [{}]".format(text))
        stream = speechsdk.AudioDataStream(result)
        stream.save_to_wav_file(filename)
    return filename


if __name__ == '__main__':

    width, height = 720, 720
    BACKGROUND_IMAGE = pygame.image.load('bg.png')
    frames = dealScript()
    print(frames)

    screen = pygame.display.set_mode((width, height))
    imgs = generate_dict('img')
    pos = {
        'A': [400, 400, 1],
        'B':[100,400,-1]
    }


    frame={
        'A': {'body':pygame.image.load('img/A/body/idle/shadiao1.png'),'face':pygame.image.load('img/A/face/peace/女-0002.png')},
        'B': {'body':pygame.image.load('img/B/body/idle/shadiao2.png'),'face':pygame.image.load('img/B/face/peace/女-0002.png')}
    }

    run = True
    video_writer = cv2.VideoWriter('game_video.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))
    current_frame = 0

    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    pygame.mixer.init()

    voices={}
    while current_frame<int(frames[-1][2]):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                run = True
            if event.type == pygame.QUIT:
                run = False

        screen.fill((0, 0, 0))

        # display the background image
        screen.blit(BACKGROUND_IMAGE, (0, 0))

        if run:
            playingAudio = ''
            for v in frames:
                k=v[0]
                if k not in voices.keys():
                    voices[v[-1]] = pygame.mixer.Sound(v[-1])
                if current_frame == int(v[1]):
                    if not pygame.mixer.get_busy():
                        voices[v[-1]].play()
                if current_frame>=int(v[1]) and current_frame<=int(v[2]):
                    facing = int(v[3])
                    bodyImgs=imgs[k]['body'][v[4]]
                    faceImgs=imgs[k]['face'][v[5]]
                    body = bodyImgs[int(current_frame/2) % len(bodyImgs)]
                    face = faceImgs[int(current_frame/2) % len(faceImgs)]
                    if facing == -1:
                        body = pygame.transform.flip(body, True, False)
                        face = pygame.transform.flip(face, True, False)
                    frame[k]['body']=body
                    frame[k]['face']=face
                    # print(current_frame,body,face,playingAudio)
                screen.blit(frame[k]['body'], (pos[k][0], pos[k][1]))
                screen.blit(frame[k]['face'], (pos[k][0], pos[k][1]-70))

            current_frame+=1

        # Update the display after each iteration of the while loop
        pygame.display.update()
        pygame_image = pygame.surfarray.array3d(screen)
        cv2_image = cv2.cvtColor(pygame_image, cv2.COLOR_RGB2BGR)
        rotated_frame = cv2.rotate(cv2_image, cv2.ROTATE_90_CLOCKWISE)
        video_writer.write(rotated_frame)

    # Quit the program
    pygame.quit()
    video_writer.release()