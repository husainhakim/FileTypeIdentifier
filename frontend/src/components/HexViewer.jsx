import React from 'react';

export default function HexViewer({ hexDump }) {
  if (!hexDump || hexDump.length === 0) return null;

  return (
    <div className="hex-viewer">
      {hexDump.map((line, idx) => (
        <div key={idx} className="hex-line">
          <span className="hex-offset">{line.offset}</span>
          <span className="hex-bytes">{line.hex}</span>
          <span className="hex-ascii">{line.ascii}</span>
        </div>
      ))}
    </div>
  );
}
