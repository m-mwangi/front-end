let uploadedFilePath = 'new_data.csv'; // Fixed file name used by the backend

// Handle file upload
async function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a file first.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Send the file to the FastAPI backend
        const response = await fetch('https://matern-ai-1.onrender.com/upload/', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message); // Show success message
            console.log('File uploaded successfully for retraining.');
            document.getElementById('retrainButton').disabled = false; // Enable retrain button
        } else {
            alert('Error uploading data: ' + (result.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error during file upload:', error);
        alert('An error occurred while uploading the file.');
    }
}

// Handle the retrain process
async function retrainModel() {
    console.log('Starting model retraining with file:', uploadedFilePath);

    // Disable retrain button to prevent multiple clicks
    document.getElementById('retrainButton').disabled = true;
    document.getElementById('retrainButton').innerText = 'Retraining...';

    try {
        // Send request to retrain the model using the fixed file name
        const response = await fetch(`https://matern-ai-1.onrender.com/retrain/?file_path=${uploadedFilePath}`, {
            method: 'POST',
            headers: { 'Accept': 'application/json' },
        });

        const result = await response.json();

        if (response.ok) {
            alert(`Model retrained successfully! Accuracy: ${result.accuracy}, Model Version: ${result.new_model_version}`);
        } else {
            alert('Error retraining model: ' + (result.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error during model retraining:', error);
        alert('An error occurred while retraining the model.');
    }

    // Reset button state
    document.getElementById('retrainButton').innerText = 'Retrain Model';
    document.getElementById('retrainButton').disabled = false;
}

// Handle file input clearing
function clearFileInput() {
    document.getElementById('file-upload').value = '';
    document.getElementById('retrainButton').disabled = true;
    document.getElementById('retrainButton').innerText = 'Retrain Model';
}
