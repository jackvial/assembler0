import { useEffect, useState } from 'react';
import { Card, Slider, Typography, Space, Row, Col, Spin } from 'antd';
import { JointInfo } from '../types';
import { api } from '../services/api';

const { Text } = Typography;

interface JointControlsProps {
  onControlChange: (controls: Record<string, number>) => void;
}

export const JointControls: React.FC<JointControlsProps> = ({
  onControlChange,
}) => {
  const [joints, setJoints] = useState<JointInfo[]>([]);
  const [jointValues, setJointValues] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadJoints();
  }, []);

  const loadJoints = async () => {
    try {
      const data = await api.getJoints();
      setJoints(data.joints);

      // Initialize joint values
      const initialValues: Record<string, number> = {};
      data.joints.forEach((joint) => {
        initialValues[joint.name] = joint.current_value;
      });
      setJointValues(initialValues);
    } catch (error) {
      console.error('Failed to load joints:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleJointChange = (jointName: string, value: number) => {
    const newValues = { ...jointValues, [jointName]: value };
    setJointValues(newValues);
    onControlChange(newValues);
  };

  if (loading) {
    return (
      <Card title='Joint Controls'>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size='large' />
        </div>
      </Card>
    );
  }

  return (
    <Card title='Joint Controls'>
      <Space direction='vertical' style={{ width: '100%' }} size='large'>
        {joints.map((joint) => (
          <div key={joint.name}>
            <Row align='middle' gutter={16}>
              <Col span={6}>
                <Text strong>{joint.name}</Text>
              </Col>
              <Col span={14}>
                <Slider
                  min={joint.min}
                  max={joint.max}
                  step={0.01}
                  value={jointValues[joint.name] || 0}
                  onChange={(value) => handleJointChange(joint.name, value)}
                  tooltip={{ formatter: (value) => value?.toFixed(2) }}
                />
              </Col>
              <Col span={4}>
                <Text>{(jointValues[joint.name] || 0).toFixed(2)}</Text>
              </Col>
            </Row>
          </div>
        ))}
      </Space>
    </Card>
  );
};
