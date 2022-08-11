from gtts import gTTS

text = "루루야 참치먹자아"

tts = gTTS(text=text, lang='ko')
tts.save("1.mp3")