package how.naver.translator1.api

import com.google.gson.annotations.SerializedName

data class OpenAIRequest(
    val model: String = "gpt-3.5-turbo",
    val messages: List<Message>,
    @SerializedName("max_tokens") val maxTokens: Int = 1000,
    val temperature: Double = 0.7
)

data class Message(
    val role: String,
    val content: String
)

data class OpenAIResponse(
    val choices: List<Choice>
)

data class Choice(
    val message: Message
)