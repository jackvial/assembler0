import React, { useState, useEffect } from 'react';
import { Card, Select, Space, Typography, Spin, message } from 'antd';
import { RobotOutlined } from '@ant-design/icons';

const { Text } = Typography;
const { Option } = Select;

interface ArmConfig {
  id: string;
  name: string;
  description: string;
  dof: number;
}

interface ArmSelectorProps {
  onArmChange?: (armId: string) => void;
}

export const ArmSelector: React.FC<ArmSelectorProps> = ({ onArmChange }) => {
  const [arms, setArms] = useState<ArmConfig[]>([]);
  const [currentArm, setCurrentArm] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [switching, setSwitching] = useState(false);

  // Fetch available arms on mount
  useEffect(() => {
    fetchArms();
  }, []);

  const fetchArms = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://${window.location.hostname}:1337/api/arms`
      );
      const data = await response.json();
      setArms(data.arms || []);
      setCurrentArm(data.current || '');
    } catch (error) {
      console.error('Failed to fetch arms:', error);
      message.error('Failed to load arm configurations');
    } finally {
      setLoading(false);
    }
  };

  const handleArmChange = async (armId: string) => {
    if (armId === currentArm) return;

    setSwitching(true);
    try {
      const response = await fetch(
        `http://${window.location.hostname}:1337/api/arms/${armId}`,
        { method: 'POST' }
      );

      if (response.ok) {
        const data = await response.json();
        setCurrentArm(armId);
        message.success(`Switched to ${data.arm.name}`);

        // Notify parent component
        if (onArmChange) {
          onArmChange(armId);
        }

        // Give the backend a moment to reload
        setTimeout(() => {
          window.location.reload();
        }, 500);
      } else {
        const error = await response.json();
        message.error(error.error || 'Failed to switch arm');
      }
    } catch (error) {
      console.error('Failed to switch arm:', error);
      message.error('Failed to switch arm configuration');
    } finally {
      setSwitching(false);
    }
  };

  return (
    <Card
      title={
        <Space>
          <RobotOutlined />
          <span>Robot Arm Configuration</span>
        </Space>
      }
      size='small'
    >
      <Space direction='vertical' style={{ width: '100%' }} size='small'>
        <div>
          <Text
            type='secondary'
            style={{ fontSize: '11px', display: 'block', marginBottom: '4px' }}
          >
            Select robot arm model
          </Text>
          <Select
            value={currentArm}
            onChange={handleArmChange}
            style={{ width: '100%' }}
            loading={loading || switching}
            disabled={loading || switching}
            placeholder='Select a robot arm'
          >
            {arms.map((arm) => (
              <Option key={arm.id} value={arm.id}>
                {arm.name}
              </Option>
            ))}
          </Select>
        </div>

        {switching && (
          <Space>
            <Spin size='small' />
            <Text type='secondary' style={{ fontSize: '12px' }}>
              Switching arm configuration...
            </Text>
          </Space>
        )}

        {currentArm && (
          <div
            style={{
              padding: '8px',
              background: 'rgba(24, 144, 255, 0.1)',
              borderRadius: '4px',
              border: '1px solid rgba(24, 144, 255, 0.3)',
            }}
          >
            <Text style={{ fontSize: '11px' }}>
              <strong>Control Mapping:</strong>
            </Text>
            <div
              style={{ fontSize: '11px', marginTop: '4px', lineHeight: '1.5' }}
            >
              {currentArm === 'low_cost_6dof_screwdriver' ? (
                <>
                  • Left Stick: Base rotation (X), Shoulder (Y)
                  <br />
                  • Right Stick: Elbow (Y), Wrist pitch (X)
                  <br />
                  • D-Pad Left/Right: Wrist roll
                  <br />
                  • L2/R2 Triggers: Screwdriver CCW/CW rotation
                  <br />• RB: Precision mode (hold for slower movement)
                </>
              ) : currentArm === 'low_cost_6dof' ? (
                <>
                  • Left Stick: Base rotation (X), Shoulder (Y)
                  <br />
                  • Right Stick: Elbow (Y), Wrist pitch (X)
                  <br />
                  • D-Pad Left/Right: Wrist roll
                  <br />
                  • Triggers: Gripper open/close
                  <br />• RB: Precision mode (hold for slower movement)
                </>
              ) : currentArm === 'low_cost_5dof' ? (
                <>
                  • Left Stick: Base rotation (X), Shoulder (Y)
                  <br />
                  • Right Stick: Elbow (Y), Wrist rotation (X)
                  <br />
                  • Triggers: Gripper open/close
                  <br />• RB: Precision mode (hold for slower movement)
                </>
              ) : currentArm === 'assembler0_dual_arm' ? (
                <>
                  • <strong>Controlling: Screwdriver Arm (Left)</strong>
                  <br />
                  • Left Stick: Base rotation (X), Shoulder (Y)
                  <br />
                  • Right Stick: Elbow (Y), Wrist pitch (X)
                  <br />
                  • D-Pad Left/Right: Wrist roll
                  <br />
                  • L2/R2 Triggers: Screwdriver CCW/CW rotation
                  <br />
                  • RB: Precision mode (hold for slower movement)
                  <br />• <em>Note: Gripper arm control coming soon</em>
                </>
              ) : (
                <>
                  • Left Stick: Base rotation (X), Shoulder (Y)
                  <br />
                  • Right Stick: Elbow/Wrist (Y), Wrist rotation (X)
                  <br />
                  • Triggers: Gripper open/close
                  <br />• RB: Precision mode (hold for slower movement)
                </>
              )}
            </div>
          </div>
        )}
      </Space>
    </Card>
  );
};
