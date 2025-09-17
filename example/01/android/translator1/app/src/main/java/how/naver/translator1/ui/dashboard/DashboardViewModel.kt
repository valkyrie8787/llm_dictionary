package how.naver.translator1.ui.dashboard

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import how.naver.translator1.api.OpenAIService
import kotlinx.coroutines.launch

class DashboardViewModel : ViewModel() {

    private val openAIService = OpenAIService()

    private val _questionText = MutableLiveData<String>()
    val questionText: LiveData<String> = _questionText

    private val _answerText = MutableLiveData<String>()
    val answerText: LiveData<String> = _answerText

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String>()
    val errorMessage: LiveData<String> = _errorMessage

    private val _myLanguage = MutableLiveData<String>()
    val myLanguage: LiveData<String> = _myLanguage

    private val _targetLanguage = MutableLiveData<String>()
    val targetLanguage: LiveData<String> = _targetLanguage

    init {
        _myLanguage.value = "English"
        _targetLanguage.value = "Korean"
        _questionText.value = ""
        _answerText.value = ""
        _isLoading.value = false
    }

    fun setLanguages(myLang: String, targetLang: String) {
        _myLanguage.value = myLang
        _targetLanguage.value = targetLang
    }

    fun setQuestionText(question: String) {
        _questionText.value = question
    }

    fun processQuestionWithRAG(question: String, ragContext: String) {
        _isLoading.value = true
        _answerText.value = "Processing..."

        viewModelScope.launch {
            try {
                val enhancedPrompt = "Please answer the following question in ${_myLanguage.value}. " +
                        "The question was originally asked in ${_targetLanguage.value}: $question"

                val result = openAIService.getCompletion(enhancedPrompt, ragContext)
                
                result.onSuccess { response ->
                    _answerText.value = response
                    _isLoading.value = false
                }.onFailure { error ->
                    _errorMessage.value = error.message ?: "Unknown error occurred"
                    _answerText.value = "Error: ${error.message}"
                    _isLoading.value = false
                }
            } catch (e: Exception) {
                _errorMessage.value = e.message ?: "Unknown error occurred"
                _answerText.value = "Error: ${e.message}"
                _isLoading.value = false
            }
        }
    }

    fun getCurrentAnswer(): String {
        return _answerText.value ?: ""
    }
}