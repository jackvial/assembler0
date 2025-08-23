import axios from 'axios';
import { JointInfo } from '../types';

const API_BASE = '/api';

export const api = {
  async getStatus() {
    const response = await axios.get(`${API_BASE}/status`);
    return response.data;
  },

  async getJoints(): Promise<{ joints: JointInfo[] }> {
    const response = await axios.get(`${API_BASE}/joints`);
    return response.data;
  },
};
