package com.kabilan108.vlmClient

import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil.compose.rememberAsyncImagePainter

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            VLMClientApp()
        }
    }
}

//@Preview
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VLMClientApp() {
    var selectedImageUri by remember { mutableStateOf<Uri?>(null) }
    var ocrResult by remember { mutableStateOf("") }

    val imagePicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent(),
        onResult = { uri: Uri? ->
            selectedImageUri = uri
        }
    )

    MaterialTheme {
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("VLM Client") }
                )
            }
        ) { innerPadding ->
            Column(
                modifier = Modifier
                    .padding(innerPadding)
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Button(
                    onClick = { imagePicker.launch("image/*") },
                    modifier = Modifier.padding(bottom = 16.dp)
                ) {
                    Text("Select Image")
                }

                selectedImageUri?.let { uri ->
                    Image(
                        painter = rememberAsyncImagePainter(uri),
                        contentDescription = "Selected image",
                        modifier = Modifier
                            .size(200.dp)
                            .padding(bottom = 16.dp),
                        contentScale = ContentScale.Fit
                    )
                }

                Button(
                    onClick = {
                        // TODO: Implement OCR processing
                        ocrResult = "OCR result will be displayed here"
                    },
                    enabled = selectedImageUri != null,
                    modifier = Modifier.padding(bottom = 16.dp)
                ) {
                    Text("Process Image")
                }

                Text(
                    text = ocrResult,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 16.dp)
                )
            }
        }
    }
}