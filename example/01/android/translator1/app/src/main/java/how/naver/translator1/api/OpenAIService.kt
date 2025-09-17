package how.naver.translator1.api

import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

class OpenAIService {
    private val client = OkHttpClient()
    private val gson = Gson()
    private val apiKey = "RdbRK_ESgSTpEyx2T2KlkHU30KGKjFJx540swA" //TODO: plz input yours
    
    suspend fun getCompletion(userQuestion: String, ragContext: String = ""): Result<String> {
        return withContext(Dispatchers.IO) {
            try {
                val systemPrompt = if (ragContext.isNotEmpty()) {
                    "You are a helpful AI assistant. Use the following context to answer questions. Context: $ragContext"
                } else {
                    "You are a helpful AI assistant."
                }
                
                val messages = listOf(
                    Message("system", systemPrompt),
                    Message("user", userQuestion)
                )
                
                val request = OpenAIRequest(
                    model = "gpt-3.5-turbo",
                    messages = messages,
                    maxTokens = 1000,
                    temperature = 0.7
                )
                
                val json = gson.toJson(request)
                val body = json.toRequestBody("application/json".toMediaType())
                
                val httpRequest = Request.Builder()
                    .url("https://api.openai.com/v1/chat/completions")
                    .addHeader("Authorization", "Bearer $apiKey")
                    .addHeader("Content-Type", "application/json")
                    .post(body)
                    .build()
                
                val response = client.newCall(httpRequest).execute()
                
                if (response.isSuccessful) {
                    val responseBody = response.body?.string() ?: ""
                    val openAIResponse = gson.fromJson(responseBody, OpenAIResponse::class.java)
                    val reply = openAIResponse.choices.firstOrNull()?.message?.content ?: "No response"
                    Result.success(reply)
                } else {
                    Result.failure(Exception("API Error: ${response.code} ${response.message}"))
                }
            } catch (e: IOException) {
                Result.failure(e)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}