import { Card, Slider, Typography, Space, Row, Col } from 'antd';
import { CameraParams } from '../types';

const { Text } = Typography;

interface CameraControlsProps {
  onCameraChange: (params: CameraParams) => void;
  cameraParams: CameraParams;
  onParamsUpdate: (params: CameraParams) => void;
}

export const CameraControls: React.FC<CameraControlsProps> = ({
  onCameraChange,
  cameraParams,
  onParamsUpdate,
}) => {
  const handleParamChange = (param: keyof CameraParams, value: number) => {
    const newParams = { ...cameraParams, [param]: value };
    onParamsUpdate(newParams);
    onCameraChange(newParams);
  };

  return (
    <Card title='Camera Controls'>
      <Space direction='vertical' style={{ width: '100%' }}>
        <Row align='middle' gutter={16}>
          <Col span={6}>
            <Text>Distance</Text>
          </Col>
          <Col span={14}>
            <Slider
              min={0.5}
              max={3}
              step={0.1}
              value={cameraParams.distance}
              onChange={(value) => handleParamChange('distance', value)}
              tooltip={{ formatter: (value) => value?.toFixed(1) }}
            />
          </Col>
          <Col span={4}>
            <Text>{cameraParams.distance?.toFixed(1)}</Text>
          </Col>
        </Row>

        <Row align='middle' gutter={16}>
          <Col span={6}>
            <Text>Elevation</Text>
          </Col>
          <Col span={14}>
            <Slider
              min={-90}
              max={90}
              step={5}
              value={cameraParams.elevation}
              onChange={(value) => handleParamChange('elevation', value)}
              tooltip={{ formatter: (value) => `${value}°` }}
            />
          </Col>
          <Col span={4}>
            <Text>{cameraParams.elevation}°</Text>
          </Col>
        </Row>

        <Row align='middle' gutter={16}>
          <Col span={6}>
            <Text>Azimuth</Text>
          </Col>
          <Col span={14}>
            <Slider
              min={0}
              max={360}
              step={5}
              value={cameraParams.azimuth}
              onChange={(value) => handleParamChange('azimuth', value)}
              tooltip={{ formatter: (value) => `${value}°` }}
            />
          </Col>
          <Col span={4}>
            <Text>{cameraParams.azimuth}°</Text>
          </Col>
        </Row>
      </Space>
    </Card>
  );
};
