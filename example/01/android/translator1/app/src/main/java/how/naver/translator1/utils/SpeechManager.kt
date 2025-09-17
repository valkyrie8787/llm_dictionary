package how.naver.translator1.utils

import android.content.Context
import android.content.Intent
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.os.Bundle
import java.util.*

class SpeechManager(
    private val context: Context,
    private val onResult: (String) -> Unit,
    private val onError: (String) -> Unit
) {
    
    private var speechRecognizer: SpeechRecognizer? = null
    private var textToSpeech: TextToSpeech? = null
    private var isListening = false
    
    init {
        initializeTTS()
    }
    
    private fun initializeTTS() {
        textToSpeech = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                textToSpeech?.language = Locale.ENGLISH
            }
        }
    }
    
    fun startListening(language: String) {
        if (isListening) {
            stopListening()
            return
        }
        
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
        
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, getLocaleForLanguage(language))
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
        }
        
        speechRecognizer?.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                isListening = true
            }
            
            override fun onBeginningOfSpeech() {
                // Speech input has begun
            }
            
            override fun onRmsChanged(rmsdB: Float) {
                // RMS value has changed - can be used for volume indication
            }
            
            override fun onBufferReceived(buffer: ByteArray?) {
                // Audio buffer received
            }
            
            override fun onEndOfSpeech() {
                isListening = false
            }
            
            override fun onError(error: Int) {
                isListening = false
                val errorMessage = when (error) {
                    SpeechRecognizer.ERROR_AUDIO -> "Audio recording error"
                    SpeechRecognizer.ERROR_CLIENT -> "Client side error"
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Insufficient permissions"
                    SpeechRecognizer.ERROR_NETWORK -> "Network error"
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
                    SpeechRecognizer.ERROR_NO_MATCH -> "No speech input"
                    SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "RecognitionService busy"
                    SpeechRecognizer.ERROR_SERVER -> "Server error"
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech input"
                    else -> "Unknown error"
                }
                onError("Speech recognition error: $errorMessage")
            }
            
            override fun onResults(results: Bundle?) {
                isListening = false
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!matches.isNullOrEmpty()) {
                    onResult(matches[0])
                } else {
                    onError("No speech recognized")
                }
            }
            
            override fun onPartialResults(partialResults: Bundle?) {
                // Handle partial results if needed
            }
            
            override fun onEvent(eventType: Int, params: Bundle?) {
                // Handle recognition events
            }
        })
        
        speechRecognizer?.startListening(intent)
    }
    
    fun stopListening() {
        isListening = false
        speechRecognizer?.stopListening()
        speechRecognizer?.destroy()
        speechRecognizer = null
    }
    
    fun speak(text: String, language: String) {
        val locale = Locale.forLanguageTag(getLocaleForLanguage(language))
        textToSpeech?.language = locale
        textToSpeech?.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
    }
    
    fun isCurrentlyListening(): Boolean = isListening
    
    private fun getLocaleForLanguage(language: String): String {
        return when (language) {
            "English" -> "en-US"
            "Korean" -> "ko-KR"
            "Japanese" -> "ja-JP"
            "Chinese" -> "zh-CN"
            "Spanish" -> "es-ES"
            "French" -> "fr-FR"
            "German" -> "de-DE"
            "Italian" -> "it-IT"
            "Portuguese" -> "pt-PT"
            "Russian" -> "ru-RU"
            else -> "en-US"
        }
    }
    
    fun destroy() {
        stopListening()
        textToSpeech?.stop()
        textToSpeech?.shutdown()
    }
}