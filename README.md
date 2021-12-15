# IPA-To-Speech
 Ein konkatenatives Synthesesystem der deutschen Aussprache.
 
 The IPA-To-Speech-system is a speech synthesis system. It is capable of converting transcriptions of the International Phonetic Alphabet to speech sounds. The IPA-To-Speech-system works best for transcriptions of German words, it also has limited capabilities for English and French.
 
 # Requirements
 The following python package versions were used during the implementation, there's no guarantee that it works with other versions. It was tested on windows with Python 3.8 and 3.9.
 * AMFM-decompy ver. 1.0.11
 * Librosa ver 0.8.0
 * matplotlib ver. 3.4.3
 * numpy ver. 1.19.5
 * psola ver 0.0.1
 * pydub ver. 0.25.1
 * pygame ver. 2.0.1
 * SoundFile ver. 0.10.3
 * Tkinter ver 8.6


# How-to start
* run the user_interface.py-script
* paste the IPA-transcription of your word in the input box
* choose the concatenation and smoothing method
* click "Synthesize!"
* to listen to your word, click "Play IPA"
