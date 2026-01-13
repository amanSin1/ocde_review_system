import React, { useState } from 'react';
import { createSubmissionAPI } from '../../services/api';
import VideoRecorder from './VideoRecorder';

export default function CreateSubmissionView({ onViewChange, onSubmissionCreated }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    code_content: '',
    language: 'python',
    tags: ''
  });
  
  const [videoBlob, setVideoBlob] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    // Validation
    if (!formData.title || formData.title.length > 200) {
      alert('Title required (max 200 chars)');
      return;
    }
    if (!formData.description || formData.description.length > 2000) {
      alert('Description required (max 2000 chars)');
      return;
    }
    if (!formData.code_content) {
      alert('Code content required');
      return;
    }

    setIsSubmitting(true);

    try {
      // Parse tags
      const tagList = formData.tags
        .split(',')
        .map(t => t.trim())
        .filter(Boolean);

      // Create FormData for multipart/form-data
      const submitFormData = new FormData();
      submitFormData.append('title', formData.title);
      submitFormData.append('description', formData.description);
      submitFormData.append('code_content', formData.code_content);
      submitFormData.append('language', formData.language);
      submitFormData.append('tags', JSON.stringify(tagList));

      // Add video if recorded
      if (videoBlob) {
        submitFormData.append('video', videoBlob, 'walkthrough.webm');
      }

      // Submit to backend
      await createSubmissionAPI(submitFormData);

      // Reset form
      setFormData({ 
        title: '', 
        description: '', 
        code_content: '', 
        language: 'python', 
        tags: '' 
      });
      setVideoBlob(null);
      
      alert('Submission created successfully! 🎉');
      onSubmissionCreated();

    } catch (err) {
      console.error('Submission error:', err);
      alert(err.message || 'Failed to create submission');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Create New Submission</h2>
        
        <div className="space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              placeholder="e.g., React Authentication System"
              maxLength={200}
            />
            <p className="text-xs text-slate-500 mt-1">
              {formData.title.length}/200 characters
            </p>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              rows={3}
              placeholder="Describe what you're building..."
              maxLength={2000}
            />
            <p className="text-xs text-slate-500 mt-1">
              {formData.description.length}/2000 characters
            </p>
          </div>

          {/* Language and Tags */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Language <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                list="languages"
                value={formData.language}
                onChange={(e) => setFormData({...formData, language: e.target.value})}
                className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                placeholder="e.g., python, javascript"
              />
              <datalist id="languages">
                <option value="python" />
                <option value="javascript" />
                <option value="typescript" />
                <option value="java" />
                <option value="cpp" />
                <option value="c" />
                <option value="csharp" />
                <option value="go" />
                <option value="rust" />
                <option value="ruby" />
                <option value="php" />
                <option value="swift" />
                <option value="kotlin" />
                <option value="scala" />
                <option value="r" />
                <option value="matlab" />
                <option value="sql" />
                <option value="html" />
                <option value="css" />
              </datalist>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Tags (comma-separated)
              </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({...formData, tags: e.target.value})}
                className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                placeholder="react, auth, security"
              />
            </div>
          </div>

          {/* Code Content */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Code <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.code_content}
              onChange={(e) => setFormData({...formData, code_content: e.target.value})}
              className="w-full px-4 py-3 border border-slate-300 rounded-xl font-mono text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all bg-slate-50"
              rows={12}
              placeholder="Paste your code here..."
            />
          </div>

          {/* Video Recorder */}
          <VideoRecorder onVideoReady={setVideoBlob} />

          {/* Action Buttons */}
          <div className="flex space-x-4 pt-4">
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex-1 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:shadow-lg hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Submitting...
                </span>
              ) : (
                'Submit for Review'
              )}
            </button>
            
            <button
              type="button"
              onClick={() => onViewChange('submissions')}
              disabled={isSubmitting}
              className="px-6 py-3 border border-slate-300 text-slate-700 rounded-xl font-semibold hover:bg-slate-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}