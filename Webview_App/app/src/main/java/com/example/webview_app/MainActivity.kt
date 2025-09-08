package com.example.webview_app

import android.os.Bundle
import android.webkit.WebView
import androidx.activity.ComponentActivity

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        setContentView(webView)

        // index.html 로드
        webView.loadUrl("file:///android_asset/index.html")

        // assets 폴더의 JSON 파일 읽기
        val jsonString = assets.open("llm_dictionary_2letter_20250812_000751.json").bufferedReader().use { it.readText() }

        // index.html이 로드된 후 JS 함수 호출하여 데이터 전달
        webView.post {
            webView.evaluateJavascript(
                "processAndLoadData(" +
                        org.json.JSONArray(org.json.JSONObject(jsonString).getJSONArray("entries").toString()).toString() +
                        ")", null
            )
        }
    }
}