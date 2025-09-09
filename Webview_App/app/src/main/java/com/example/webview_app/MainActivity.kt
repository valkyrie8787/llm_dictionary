package com.example.webview_app

import android.os.Bundle
import android.webkit.WebView
import androidx.activity.ComponentActivity
import android.content.Context
import android.webkit.JavascriptInterface
import java.io.BufferedReader
import java.io.InputStreamReader

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        setContentView(webView)

        // 자바스크립트 인터페이스 추가
        webView.addJavascriptInterface(DictionaryInterface(this), "Android")

        // dictionary_Multi.html만 로드
        webView.loadUrl("file:///android_asset/dictionary_Multi.html")
    }
}

class DictionaryInterface(private val context: Context) {
    @JavascriptInterface
    fun getDictionary(type: String): String {
        val filename = when (type) {
            "en-ko" -> "dict_ko_2letter_20250905_220620_with_wordkr_v2.json"
            "en-de" -> "dict_de_2letter_20250905_220120_with_wordde_v2.json"
            "en-ja" -> "dict_ja_alpha_with_wordja_v3.json"
            else -> return "{}"
        }
        return try {
            val inputStream = context.assets.open(filename)
            val reader = BufferedReader(InputStreamReader(inputStream))
            val sb = StringBuilder()
            var line: String? = reader.readLine()
            while (line != null) {
                sb.append(line)
                line = reader.readLine()
            }
            reader.close()
            sb.toString()
        } catch (e: Exception) {
            "{}"
        }
    }
}