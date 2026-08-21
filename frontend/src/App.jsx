import { useState, useRef } from 'react';
import HexViewer from './components/HexViewer';
import './index.css';

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (file) => {
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze file');
      }
      
      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const onFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="container">
      <div className="panel-left">
        <h2>FileIdentifier</h2>
        <p>Magic Number / File Signature Analysis</p>

        <div 
          className={`upload-box ${isDragging ? 'drag-active' : ''}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <p>[ DROP FILE HERE OR CLICK TO BROWSE ]</p>
          <input 
            type="file" 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            onChange={onFileSelect}
          />
        </div>

        {error && (
          <div className="alert-box">
            ERROR: {error}
          </div>
        )}

        {analysis && analysis.is_spoofed && (
          <div className="alert-box">
            {analysis.spoof_alert}
          </div>
        )}

        {analysis && (
          <div className="results-box">
            <h3>Analysis Results</h3>
            <br/>
            <p><strong>Filename:</strong> {analysis.filename}</p>
            <br/>
            <h4>Detected Signatures:</h4>
            <br/>
            {analysis.matches.map((match, idx) => (
              <div key={idx} style={{ marginBottom: '10px' }}>
                <p>Type: .{match.ext.toUpperCase()}</p>
                <p>Desc: {match.description}</p>
                <p>Confidence: {(match.confidence * 100).toFixed(0)}%</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="panel-right">
        <h3>Hex Dump (First 256 Bytes)</h3>
        <br/>
        {analysis ? (
          <HexViewer hexDump={analysis.hex_dump} />
        ) : (
          <div className="hex-viewer" style={{ color: 'var(--muted-text)' }}>
            Awaiting file input...
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
