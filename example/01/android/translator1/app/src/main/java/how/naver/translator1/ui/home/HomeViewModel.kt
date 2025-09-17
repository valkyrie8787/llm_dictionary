package how.naver.translator1.ui.home

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class HomeViewModel : ViewModel() {

    private val _fileContent = MutableLiveData<String>()
    val fileContent: LiveData<String> = _fileContent

    private val _fileStatus = MutableLiveData<String>()
    val fileStatus: LiveData<String> = _fileStatus

    init {
        _fileStatus.value = "No file selected"
        _fileContent.value = "File content will appear here..."
    }

    fun setFileContent(content: String, fileName: String) {
        _fileContent.value = content
        _fileStatus.value = "File loaded: $fileName"
    }

    fun getContextForRAG(): String {
        return _fileContent.value ?: ""
    }
}