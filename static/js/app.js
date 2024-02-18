// document.addEventListener('DOMContentLoaded', function() {
//   // Check if the browser supports the required APIs
//   if (!navigator.mediaDevices || !window.MediaRecorder) {
//       alert('Your browser does not support the required media APIs.');
//       return;
//   }

//   let mediaRecorder;
//   let audioChunks = [];

//   document.getElementById('startRecording').addEventListener('click', function() {
//       navigator.mediaDevices.getUserMedia({ audio: true, video: false })
//           .then(stream => {
//               if (mediaRecorder) {
//                   // If a mediaRecorder instance already exists, stop any ongoing recording and release the previous stream
//                   if (mediaRecorder.state === 'recording') {
//                       mediaRecorder.stop();
//                   }
//                   stream.getTracks().forEach(track => track.stop());
//               }

//               mediaRecorder = new MediaRecorder(stream);
//               audioChunks = [];

//               mediaRecorder.addEventListener('dataavailable', event => {
//                   audioChunks.push(event.data);
//               });

//               mediaRecorder.addEventListener('stop', () => {
//                   const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
//                   const formData = new FormData();
//                   formData.append('audio', audioBlob);

//                   axios.post('http://127.0.0.1:5000/whisper', formData, {
//                       headers: {
//                           'Content-Type': 'multipart/form-data'
//                       }
//                   })
//                   .then(response => {
//                       console.log('Server response:', response.data);
//                       // Here you can update the UI with the transcription result or any response from the server
//                   })
//                   .catch(error => console.error('Error sending audio to the server:', error));
//               });

//               // Use the Hark library to detect when the user starts and stops speaking
//               const speechEvents = hark(stream, {});

//               speechEvents.on('speaking', function() {
//                   console.log('Speaking started');
//                   mediaRecorder.start();
//               });

//               speechEvents.on('stopped_speaking', function() {
//                   console.log('Speaking stopped');
//                   if (mediaRecorder.state === 'recording') {
//                       mediaRecorder.stop();
//                   }
//               });
//           })
//           .catch(error => {
//               console.error('Error accessing the microphone:', error);
//               alert('Could not access the microphone. Please ensure it is connected and permission is granted.');
//           });
//   });
// });

// Ensure the DOM is fully loaded before executing the script
document.addEventListener('DOMContentLoaded', function() {
  let isProcessing = false; // Flag to indicate whether the backend is currently processing audio
  let mediaRecorder; // Global variable to hold the MediaRecorder instance

  // Initializes and starts the microphone recording based on speech detection
  function initRecording() {
      // Check if the browser supports necessary APIs and if not currently processing audio
      if (navigator.mediaDevices && window.MediaRecorder && !isProcessing) {
          navigator.mediaDevices.getUserMedia({ audio: true, video: false })
              .then(stream => {
                  // Initialize hark with the audio stream and optional configurations
                  const options = {}; // Placeholder for hark options if needed
                  const speechEvents = hark(stream, options);

                  // Initialize MediaRecorder with the audio stream
                  mediaRecorder = new MediaRecorder(stream);
                  let audioChunks = []; // Array to store chunks of audio data

                  // Event listener for when audio data is available
                  mediaRecorder.ondataavailable = event => {
                      // Collect audio data chunks
                      audioChunks.push(event.data);
                  };

                  // Event listener for when recording stops
                  mediaRecorder.onstop = () => {
                      // Combine audio chunks into a single Blob
                      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                      // Send the audio blob to the server for processing
                      sendAudioToServer(audioBlob);
                      // Clear the audioChunks array for the next recording
                      audioChunks = [];
                  };

                  // Hark event when speech is detected
                  speechEvents.on('speaking', function() {
                      // Start recording if not currently processing audio
                      if (!isProcessing) {
                          mediaRecorder.start();
                          console.log('Started recording');
                      }
                  });

                  // Hark event when speech stops
                  speechEvents.on('stopped_speaking', function() {
                      // Stop recording if it's currently active
                      if (mediaRecorder.state === 'recording') {
                          mediaRecorder.stop();
                          console.log('Stopped recording');
                          // Indicate that audio is being processed
                          isProcessing = true;
                      }
                  });
              })
              .catch(error => {
                  // Handle errors, such as user denying microphone access
                  console.error('Error accessing the microphone:', error);
              });
      }
  }

  // Sends the recorded audio to the server and manages the response
  function sendAudioToServer(audioBlob) {
      // Prepare the audio file for sending using FormData
      const formData = new FormData();
      formData.append('audio', audioBlob);

      // Send the audio to the server using axios
      axios.post('http://127.0.0.1:5000/handle_question', formData)
          .then(response => {
              // Handle server response, possibly with transcription data
              console.log('Server response:', response.data);

              // Show the audio player and set the source to the generated audio file
              const audioPlayer = document.getElementById('responseAudio');
              audioPlayer.hidden = false; // Make the player visible
              const timestamp = new Date().getTime(); // Get current timestamp
              audioPlayer.src = `${response.data.speech_url}?t=${timestamp}`; // Update the src with the timestamp
              audioPlayer.load(); // Reload the source
              audioPlayer.play(); // Play the audio file

              audioPlayer.onended = () => {
                console.log("Audio playback finished. Restarting microphone ..."); 
                // Reset the processing flag to indicate ready for next recording
                isProcessing = false;
              
                // Reactivate recording to start listening for speech again
                initRecording();
              }
          })
          .catch(error => {
              // Handle any errors during the send process
              console.error('Error sending audio to the server:', error);
              // Ensure the system is ready for another recording attempt even if there was an error
              isProcessing = false;
              // Reactivate recording
              initRecording();
          });
  }

  // Kick off the recording process when everything is set up
  initRecording();
});
