package how.naver.translator1.utils

import android.content.Context
import android.net.Uri
import java.io.BufferedReader
import java.io.InputStreamReader

class FileManager {
    
    fun readTextFile(context: Context, uri: Uri): String? {
        return try {
            val inputStream = context.contentResolver.openInputStream(uri)
            val reader = BufferedReader(InputStreamReader(inputStream))
            val content = reader.readText()
            reader.close()
            inputStream?.close()
            content
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}