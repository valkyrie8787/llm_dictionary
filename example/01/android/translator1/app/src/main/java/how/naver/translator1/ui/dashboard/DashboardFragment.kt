package how.naver.translator1.ui.dashboard

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import how.naver.translator1.R
import how.naver.translator1.data.RAGContextManager
import how.naver.translator1.databinding.FragmentDashboardBinding
import how.naver.translator1.utils.SpeechManager

class DashboardFragment : Fragment() {

    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!
    
    private lateinit var dashboardViewModel: DashboardViewModel
    private lateinit var speechManager: SpeechManager
    
    private val languages = arrayOf(
        "English", "Korean", "Japanese", "Chinese", "Spanish", 
        "French", "German", "Italian", "Portuguese", "Russian"
    )

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            startListening()
        } else {
            Toast.makeText(requireContext(), "Microphone permission is required", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        dashboardViewModel = ViewModelProvider(this)[DashboardViewModel::class.java]
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        
        setupSpeechManager()
        setupLanguageSpinners()
        setupObservers()
        setupClickListeners()
        
        return binding.root
    }
    
    private fun setupSpeechManager() {
        speechManager = SpeechManager(
            context = requireContext(),
            onResult = { recognizedText ->
                binding.tvQuestionText.text = recognizedText
                dashboardViewModel.setQuestionText(recognizedText)
                processWithRAG(recognizedText)
            },
            onError = { error ->
                Toast.makeText(requireContext(), error, Toast.LENGTH_SHORT).show()
                binding.btnListen.text = getString(R.string.listen)
            }
        )
    }
    
    private fun setupLanguageSpinners() {
        val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_item, languages)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        
        binding.spinnerMyLanguage.adapter = adapter
        binding.spinnerTargetLanguage.adapter = adapter
        
        // Set default selections (English and Korean)
        binding.spinnerMyLanguage.setSelection(0) // English
        binding.spinnerTargetLanguage.setSelection(1) // Korean
    }
    
    private fun setupObservers() {
        dashboardViewModel.questionText.observe(viewLifecycleOwner) { question ->
            binding.tvQuestionText.text = question
        }
        
        dashboardViewModel.answerText.observe(viewLifecycleOwner) { answer ->
            binding.tvAnswerText.text = answer
            binding.btnPlay.isEnabled = answer.isNotEmpty() && answer != "Processing..."
        }
        
        dashboardViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            binding.btnListen.isEnabled = !isLoading
        }
        
        dashboardViewModel.errorMessage.observe(viewLifecycleOwner) { error ->
            if (error.isNotEmpty()) {
                Toast.makeText(requireContext(), error, Toast.LENGTH_LONG).show()
            }
        }
    }
    
    private fun setupClickListeners() {
        binding.btnListen.setOnClickListener {
            if (speechManager.isCurrentlyListening()) {
                stopListening()
            } else {
                checkPermissionAndStartListening()
            }
        }
        
        binding.btnPlay.setOnClickListener {
            playAnswer()
        }
    }
    
    private fun checkPermissionAndStartListening() {
        when {
            ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.RECORD_AUDIO
            ) == PackageManager.PERMISSION_GRANTED -> {
                startListening()
            }
            else -> {
                requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
        }
    }
    
    private fun startListening() {
        val targetLanguage = binding.spinnerTargetLanguage.selectedItem.toString()
        binding.btnListen.text = getString(R.string.listening)
        speechManager.startListening(targetLanguage)
    }
    
    private fun stopListening() {
        speechManager.stopListening()
        binding.btnListen.text = getString(R.string.listen)
    }
    
    private fun playAnswer() {
        val answer = dashboardViewModel.getCurrentAnswer()
        val myLanguage = binding.spinnerMyLanguage.selectedItem.toString()
        
        if (answer.isNotEmpty()) {
            speechManager.speak(answer, myLanguage)
        }
    }
    
    private fun processWithRAG(question: String) {
        val myLanguage = binding.spinnerMyLanguage.selectedItem.toString()
        val targetLanguage = binding.spinnerTargetLanguage.selectedItem.toString()
        
        dashboardViewModel.setLanguages(myLanguage, targetLanguage)
        
        // Get RAG context from RAGContextManager
        val ragContext = RAGContextManager.getContext()
        dashboardViewModel.processQuestionWithRAG(question, ragContext)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        speechManager.destroy()
        _binding = null
    }
}