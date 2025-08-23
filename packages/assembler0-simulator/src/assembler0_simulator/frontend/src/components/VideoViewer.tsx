import { useRef, useEffect, useState } from 'react';
import { Card, Tag } from 'antd';
import { SimulationState, CameraParams } from '../types';

interface VideoViewerProps {
  imageData?: string;
  state?: SimulationState;
  connected: boolean;
  onCameraChange?: (params: Partial<CameraParams>) => void;
  currentCamera?: CameraParams;
}

export const VideoViewer: React.FC<VideoViewerProps> = ({
  imageData,
  state,
  connected,
  onCameraChange,
  currentCamera,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [cameraStart, setCameraStart] = useState({
    azimuth: 180,
    elevation: -20,
  });

  // Draw image to canvas when imageData changes
  useEffect(() => {
    if (!canvasRef.current || !imageData) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      // Set canvas size to match image
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
    };
    img.src = `data:image/jpeg;base64,${imageData}`;
  }, [imageData]);

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX, y: e.clientY });
    setCameraStart({
      azimuth: currentCamera?.azimuth || 180,
      elevation: currentCamera?.elevation || -20,
    });
    e.preventDefault();
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging || !onCameraChange) return;

    const deltaX = e.clientX - dragStart.x;
    const deltaY = e.clientY - dragStart.y;

    // Calculate new camera angles based on mouse movement
    const sensitivity = 0.5;
    const newAzimuth = (cameraStart.azimuth - deltaX * sensitivity + 360) % 360;
    const newElevation = Math.max(
      -90,
      Math.min(90, cameraStart.elevation + deltaY * sensitivity)
    );

    onCameraChange({
      azimuth: newAzimuth,
      elevation: newElevation,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    if (!onCameraChange || !currentCamera) return;

    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.1 : -0.1;
    const currentDistance = currentCamera.distance || 1.5;
    const newDistance = Math.max(0.5, Math.min(3, currentDistance + delta));

    onCameraChange({
      distance: newDistance,
    });
  };
  return (
    <Card
      title='Simulation View'
      extra={
        <Tag color={connected ? 'green' : 'red'}>
          {connected ? 'Connected' : 'Disconnected'}
        </Tag>
      }
    >
      <div style={{ position: 'relative' }}>
        {imageData ? (
          <canvas
            ref={canvasRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseLeave}
            onWheel={handleWheel}
            style={{
              width: '100%',
              height: 'auto',
              cursor: isDragging ? 'grabbing' : 'grab',
              userSelect: 'none',
            }}
          />
        ) : (
          <div
            style={{
              width: '100%',
              height: '480px',
              background:
                'linear-gradient(135deg, rgba(10, 10, 30, 0.8) 0%, rgba(30, 10, 50, 0.8) 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#70c0c0',
              fontSize: '14px',
              fontFamily: 'monospace',
              textTransform: 'uppercase',
              letterSpacing: '2px',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundImage: `
                linear-gradient(rgba(64, 169, 169, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(64, 169, 169, 0.05) 1px, transparent 1px)
              `,
                backgroundSize: '20px 20px',
                animation: 'gridMove 10s linear infinite',
              }}
            />
            <span
              style={{
                textShadow: '0 0 10px #40a9a9',
                animation: 'neonPulse 2s ease-in-out infinite',
                position: 'relative',
                zIndex: 1,
              }}
            >
              Loading...
            </span>
          </div>
        )}
        {state && (
          <div
            style={{
              position: 'absolute',
              top: 10,
              left: 10,
              background:
                'linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(0, 20, 40, 0.9) 100%)',
              color: '#70c0c0',
              padding: '8px 12px',
              borderRadius: '0',
              fontSize: '11px',
              pointerEvents: 'none',
              fontFamily: 'monospace',
              border: '1px solid rgba(64, 169, 169, 0.5)',
              boxShadow: '0 0 20px rgba(64, 169, 169, 0.3)',
              textTransform: 'uppercase',
              letterSpacing: '1px',
            }}
          >
            <div style={{ color: '#a940a9', marginBottom: '4px' }}>
              [SYS::TIME]{' '}
              <span style={{ color: '#40a970' }}>{state.time.toFixed(2)}s</span>
            </div>
            <div style={{ fontSize: '10px', color: '#70c0c0', opacity: 0.9 }}>
              → DRAG: ROTATE_CAM
            </div>
            <div style={{ fontSize: '10px', color: '#70c0c0', opacity: 0.9 }}>
              → SCROLL: ZOOM_CTRL
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
