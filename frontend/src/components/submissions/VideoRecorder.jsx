import React, { useState, useRef } from 'react';

export default function VideoRecorder({ onVideoReady }) {
  const [status, setStatus] = useState('idle'); // idle, recording, stopped
  const [mediaBlobUrl, setMediaBlobUrl] = useState(null);
  const [error, setError] = useState(null);
  const [audioSources, setAudioSources] = useState({ mic: false, system: false });
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);

  const startRecording = async () => {
    try {
      setError(null);
      setAudioSources({ mic: false, system: false });
      
      // Request screen capture
      const displayStream = await navigator.mediaDevices.getDisplayMedia({
        video: { 
          mediaSource: 'screen',
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      });

      // Request microphone for voice
      let micStream;
      try {
        micStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        });
      } catch (micError) {
        console.warn('Microphone access denied, continuing without mic:', micError);
      }

      // Combine screen video + both audio tracks
      const combinedStream = new MediaStream();
      
      // Add video track from screen
      const videoTrack = displayStream.getVideoTracks()[0];
      if (videoTrack) {
        combinedStream.addTrack(videoTrack);
      }

      // Add system audio from screen (if available)
      const systemAudioTrack = displayStream.getAudioTracks()[0];
      if (systemAudioTrack) {
        combinedStream.addTrack(systemAudioTrack);
        setAudioSources(prev => ({ ...prev, system: true }));
      }

      // Add microphone audio (if available)
      if (micStream) {
        const micAudioTrack = micStream.getAudioTracks()[0];
        if (micAudioTrack) {
          combinedStream.addTrack(micAudioTrack);
          setAudioSources(prev => ({ ...prev, mic: true }));
        }
      }

      streamRef.current = combinedStream;
      chunksRef.current = [];

      // Check supported MIME types and use the best one
      let mimeType = 'video/webm;codecs=vp8,opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'video/webm';
      }

      // Create MediaRecorder with combined stream
      const mediaRecorder = new MediaRecorder(combinedStream, {
        mimeType: mimeType,
        videoBitsPerSecond: 2500000, // 2.5 Mbps for good quality
        audioBitsPerSecond: 128000   // 128 kbps for audio
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        setMediaBlobUrl(url);
        onVideoReady(blob); // Pass blob to parent
        setStatus('stopped');
        
        // Clean up all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        if (micStream) {
          micStream.getTracks().forEach(track => track.stop());
        }
        displayStream.getTracks().forEach(track => track.stop());
      };

      // Handle user stopping screen share
      videoTrack.onended = () => {
        if (status === 'recording') {
          stopRecording();
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(1000); // Capture in 1-second chunks for better recovery
      setStatus('recording');

    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to start recording. Please allow screen sharing and microphone access.');
      setStatus('idle');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && status === 'recording') {
      mediaRecorderRef.current.stop();
    }
  };

  const clearRecording = () => {
    if (mediaBlobUrl) {
      URL.revokeObjectURL(mediaBlobUrl);
    }
    setMediaBlobUrl(null);
    onVideoReady(null);
    setStatus('idle');
    setAudioSources({ mic: false, system: false });
    chunksRef.current = [];
  };

  return (
    <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 bg-slate-50">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-slate-900 mb-1">
            📹 Record Code Walkthrough (Optional)
          </h3>
          <p className="text-sm text-slate-600">
            Explain your approach, challenges, and areas you want feedback on
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {status === 'idle' && (
          <button
            type="button"
            onClick={startRecording}
            className="px-6 py-3 bg-blue-500 text-white rounded-xl font-medium hover:bg-blue-600 transition-all hover:shadow-lg"
          >
            🎬 Start Recording
          </button>
        )}

        {status === 'recording' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-slate-700">Recording...</span>
              </div>
              <div className="flex items-center space-x-3 text-xs">
                {audioSources.mic && (
                  <span className="flex items-center space-x-1 text-green-600">
                    <span>🎤</span>
                    <span>Microphone</span>
                  </span>
                )}
                {audioSources.system && (
                  <span className="flex items-center space-x-1 text-blue-600">
                    <span>🔊</span>
                    <span>System Audio</span>
                  </span>
                )}
                {!audioSources.mic && !audioSources.system && (
                  <span className="text-amber-600">⚠️ No audio detected</span>
                )}
              </div>
            </div>
            <button
              type="button"
              onClick={stopRecording}
              className="px-6 py-3 bg-red-500 text-white rounded-xl font-medium hover:bg-red-600 transition-all hover:shadow-lg"
            >
              ⏹️ Stop Recording
            </button>
          </div>
        )}

        {status === 'stopped' && mediaBlobUrl && (
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-green-600 font-medium">
              <span>✅</span>
              <span>Video recorded successfully!</span>
            </div>
            
            <video 
              src={mediaBlobUrl} 
              controls 
              className="w-full max-w-2xl rounded-lg border-2 border-slate-300 shadow-md"
            />
            
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={startRecording}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-all text-sm"
              >
                🔄 Re-record
              </button>
              <button
                type="button"
                onClick={clearRecording}
                className="px-4 py-2 bg-slate-300 text-slate-700 rounded-lg font-medium hover:bg-slate-400 transition-all text-sm"
              >
                🗑️ Remove Video
              </button>
            </div>
          </div>
        )}

        <div className="text-xs text-slate-500 space-y-1">
          <p>💡 <strong>Tips for a great walkthrough:</strong></p>
          <ul className="list-disc list-inside ml-2 space-y-0.5">
            <li>Allow microphone access when prompted for voice narration</li>
            <li>Share your screen with the code visible</li>
            <li>Speak clearly while explaining your thought process and design decisions</li>
            <li>Highlight areas where you want specific feedback</li>
            <li>Keep it concise (2-5 minutes is ideal)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}