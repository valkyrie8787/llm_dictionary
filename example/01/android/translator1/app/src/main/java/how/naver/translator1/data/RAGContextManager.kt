package how.naver.translator1.data

object RAGContextManager {
    private var currentContext: String = ""
    
    fun setContext(context: String) {
        currentContext = context
    }
    
    fun getContext(): String {
        return currentContext
    }
    
    fun hasContext(): Boolean {
        return currentContext.isNotEmpty()
    }
}