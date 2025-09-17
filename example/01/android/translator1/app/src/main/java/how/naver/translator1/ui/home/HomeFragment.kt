package how.naver.translator1.ui.home

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import how.naver.translator1.data.RAGContextManager
import how.naver.translator1.databinding.FragmentHomeBinding
import how.naver.translator1.utils.FileManager

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    
    private lateinit var homeViewModel: HomeViewModel
    private lateinit var fileManager: FileManager
    private lateinit var filePickerLauncher: ActivityResultLauncher<Intent>

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        homeViewModel = ViewModelProvider(this)[HomeViewModel::class.java]
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        
        fileManager = FileManager()
        
        setupFilePickerLauncher()
        setupObservers()
        setupClickListeners()
        
        return binding.root
    }
    
    private fun setupFilePickerLauncher() {
        filePickerLauncher = registerForActivityResult(
            ActivityResultContracts.StartActivityForResult()
        ) { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                result.data?.data?.let { uri ->
                    handleFileSelection(uri)
                }
            }
        }
    }
    
    private fun setupObservers() {
        homeViewModel.fileStatus.observe(viewLifecycleOwner) { status ->
            binding.tvFileStatus.text = status
        }
        
        homeViewModel.fileContent.observe(viewLifecycleOwner) { content ->
            binding.tvFileContent.text = content
            // Update the global RAG context
            RAGContextManager.setContext(content)
        }
    }
    
    private fun setupClickListeners() {
        binding.btnImportFile.setOnClickListener {
            openFilePicker()
        }
    }
    
    private fun openFilePicker() {
        val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "text/plain"
            addCategory(Intent.CATEGORY_OPENABLE)
        }
        filePickerLauncher.launch(Intent.createChooser(intent, "Select a text file"))
    }
    
    private fun handleFileSelection(uri: Uri) {
        val content = fileManager.readTextFile(requireContext(), uri)
        if (content != null) {
            val fileName = getFileName(uri)
            homeViewModel.setFileContent(content, fileName)
            Toast.makeText(requireContext(), "File imported successfully", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(requireContext(), "Error reading file", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun getFileName(uri: Uri): String {
        return uri.lastPathSegment ?: "Unknown file"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
    
    fun getRAGContext(): String {
        return homeViewModel.getContextForRAG()
    }
}