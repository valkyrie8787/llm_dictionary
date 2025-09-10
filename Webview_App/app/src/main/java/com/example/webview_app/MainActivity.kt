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

        // WebViewClient 설정: html이 완전히 로드된 후 JS 함수 호출
        webView.webViewClient = object : android.webkit.WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                val jsonString = assets.open("multilingual_dict.json").bufferedReader().use { it.readText() }
                // window.processAndLoadData로 전달
                webView.evaluateJavascript(
                    "window.processAndLoadData(" + org.json.JSONObject(jsonString).toString() + ")", null
                )
            }
        }

        webView.loadUrl("file:///android_asset/multilingual_dictionary.html")
    }
}