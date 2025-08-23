import { useEffect, useState } from 'react';
import {
  Layout,
  Row,
  Col,
  Typography,
  Space,
  ConfigProvider,
  theme,
} from 'antd';
import { THEME_COLORS } from './constants/theme';
import { VideoViewer } from './components/VideoViewer';
import { JointControls } from './components/JointControls';
import { CameraControls } from './components/CameraControls';
import { ArmSelector } from './components/ArmSelector';
import { GamepadVisualizer } from './components/Gamepad/GamepadVisualizer';
import { GamepadStatus } from './components/Gamepad/GamepadStatus';
import { useGamepad } from './hooks/useGamepad';
import { useGamepadControl } from './hooks/useGamepadControl';
import { DEFAULT_GAMEPAD_CONFIG } from './types/gamepad';
import { SimulatorWebSocket } from './services/websocket';
import { SimulationState, CameraParams } from './types';

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  const [ws, setWs] = useState<SimulatorWebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [imageData, setImageData] = useState<string>();
  const [state, setState] = useState<SimulationState>();
  const [cameraParams, setCameraParams] = useState<CameraParams>({
    distance: 1.5,
    elevation: -20,
    azimuth: 180,
  });
  const [gamepadConfig] = useState(DEFAULT_GAMEPAD_CONFIG);

  const gamepadState = useGamepad(gamepadConfig);
  useGamepadControl(gamepadState, gamepadConfig);

  useEffect(() => {
    // Initialize WebSocket connection
    const websocket = new SimulatorWebSocket(
      `ws://${window.location.hostname}:1337/ws`
    );

    websocket.onMessage((message) => {
      if (message.type === 'frame') {
        setImageData(message.image);
        setState(message.state);
      }
    });

    websocket
      .connect()
      .then(() => {
        setConnected(true);
      })
      .catch((error) => {
        console.error('Failed to connect:', error);
        setConnected(false);
      });

    setWs(websocket);

    return () => {
      websocket.disconnect();
    };
  }, []);

  const handleControlChange = (controls: Record<string, number>) => {
    if (ws) {
      ws.sendControl(controls);
    }
  };

  const handleCameraChange = (params: CameraParams) => {
    if (ws) {
      ws.sendCamera(params);
    }
  };

  const handleMouseCameraChange = (partialParams: Partial<CameraParams>) => {
    const newParams = { ...cameraParams, ...partialParams };
    setCameraParams(newParams);
    if (ws) {
      ws.sendCamera(newParams);
    }
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: THEME_COLORS.PRIMARY,
          colorSuccess: THEME_COLORS.SUCCESS,
          colorWarning: THEME_COLORS.WARNING,
          colorError: THEME_COLORS.ERROR,
          colorInfo: THEME_COLORS.PRIMARY,
          borderRadius: 2,
          colorBgContainer: THEME_COLORS.BG_SECONDARY,
          colorBgElevated: THEME_COLORS.BG_ELEVATED,
          colorBorder: THEME_COLORS.BORDER,
        },
        components: {
          Card: {
            colorBorderSecondary: THEME_COLORS.BORDER,
            colorBgContainer: THEME_COLORS.BG_SECONDARY,
          },
          Slider: {
            trackBg: THEME_COLORS.PRIMARY_30,
            railBg: THEME_COLORS.BORDER,
            handleColor: THEME_COLORS.PRIMARY,
            trackHoverBg: THEME_COLORS.PRIMARY_50,
          },
        },
      }}
    >
      <div
        style={{
          minHeight: '100vh',
          background: THEME_COLORS.BG_PRIMARY,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Subtle grid background */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: `
            linear-gradient(${THEME_COLORS.BORDER_10} 1px, transparent 1px),
            linear-gradient(90deg, ${THEME_COLORS.BORDER_10} 1px, transparent 1px)
          `,
            backgroundSize: '50px 50px',
            pointerEvents: 'none',
          }}
        />

        <style>{`
          .simulator-title {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            font-weight: 600;
            color: ${THEME_COLORS.TEXT_PRIMARY} !important;
          }
          .ant-card {
            border: 1px solid ${THEME_COLORS.BORDER} !important;
            background: ${THEME_COLORS.BG_SECONDARY} !important;
          }
          .ant-card-head {
            border-bottom: 1px solid ${THEME_COLORS.BORDER} !important;
            background: ${THEME_COLORS.BG_SECONDARY} !important;
          }
          .ant-slider-handle::after {
            box-shadow: 0 0 8px ${THEME_COLORS.PRIMARY_50} !important;
          }
          .ant-tag-green {
            background: ${THEME_COLORS.SUCCESS_20} !important;
            border: 1px solid ${THEME_COLORS.SUCCESS} !important;
            color: ${THEME_COLORS.SUCCESS} !important;
          }
          .ant-tag-red {
            background: ${THEME_COLORS.ERROR_20} !important;
            border: 1px solid ${THEME_COLORS.ERROR} !important;
            color: ${THEME_COLORS.ERROR} !important;
          }
        `}</style>

        <Layout
          style={{
            minHeight: '100vh',
            background: 'transparent',
            position: 'relative',
          }}
        >
          <Header
            style={{
              background: THEME_COLORS.BG_SECONDARY,
              padding: '0 24px',
              borderBottom: `1px solid ${THEME_COLORS.BORDER}`,
            }}
          >
            <Title
              level={3}
              className='simulator-title'
              style={{ margin: '16px 0' }}
            >
              Assembler 0 Simulator
            </Title>
          </Header>
          <Content style={{ padding: '24px', background: 'transparent' }}>
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={16}>
                <VideoViewer
                  imageData={imageData}
                  state={state}
                  connected={connected}
                  onCameraChange={handleMouseCameraChange}
                  currentCamera={cameraParams}
                />
              </Col>
              <Col xs={24} lg={8}>
                <Space
                  direction='vertical'
                  style={{ width: '100%' }}
                  size='large'
                >
                  <ArmSelector />
                  <JointControls onControlChange={handleControlChange} />
                  <CameraControls
                    onCameraChange={handleCameraChange}
                    cameraParams={cameraParams}
                    onParamsUpdate={setCameraParams}
                  />
                  <GamepadVisualizer gamepadState={gamepadState} show={true} />
                </Space>
              </Col>
            </Row>
          </Content>
        </Layout>
        <GamepadStatus gamepadState={gamepadState} />
      </div>
    </ConfigProvider>
  );
}

export default App;
