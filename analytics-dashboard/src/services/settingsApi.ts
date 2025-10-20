import { API_BASE_URL } from '../config';

export interface SettingsData {
  upload_platforms: {
    instagram: boolean;
    youtube: boolean;
    tiktok: boolean;
  };
  directories: {
    watch_dir: string;
    processed_dir: string;
  };
  scheduling: {
    auto_schedule: boolean;
    schedule_spacing_hours: number;
    default_post_time_offset: number;
  };
  user: {
    username: string;
    email: string;
    role: string;
  };
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
};

export const settingsApi = {
  getSettings: async (): Promise<SettingsData> => {
    const response = await fetch(`${API_BASE_URL}/api/settings`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch settings');
    return response.json();
  },

  updateSettings: async (settings: Partial<SettingsData>): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/settings`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(settings)
    });
    if (!response.ok) throw new Error('Failed to update settings');
  },

  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/settings/change-password`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to change password');
    }
  }
};
