import { API_BASE_URL } from '../config';

export interface MissedReplay {
  filename: string;
  file_path: string;
  file_size: number;
  modified_time: number;
}

interface MissedReplaysResponse {
  success: boolean;
  count: number;
  replays: MissedReplay[];
}

interface ScheduleReplayResponse {
  success: boolean;
  post_id: number;
  scheduled_time: string;
  video_path: string;
  metadata: {
    title: string;
    description?: string;
    hashtags?: string;
  };
}

interface ScheduleBatchResponse {
  success: boolean;
  total: number;
  successful: number;
  failed: number;
  results: Array<{
    video_path: string;
    success: boolean;
    post_id?: number;
    scheduled_time?: string;
    metadata?: {
      title: string;
      description?: string;
      hashtags?: string;
    };
    error?: string;
  }>;
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const missedReplaysApi = {
  /**
   * Get list of unprocessed videos in watch directory
   */
  getMissedReplays: async (): Promise<MissedReplay[]> => {
    const response = await fetch(`${API_BASE_URL}/api/missed-replays`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch missed replays: ${response.statusText}`);
    }
    
    const data: MissedReplaysResponse = await response.json();
    return data.replays || [];
  },

  /**
   * Schedule a single missed replay for posting
   * @param videoPath - Path to the video file
   * @param scheduledTime - Optional ISO datetime string. If not provided, schedules for next available slot
   * @param platforms - Optional array of platforms. If not provided, uses configured platforms
   */
  scheduleReplay: async (
    videoPath: string, 
    scheduledTime?: string,
    platforms?: string[]
  ): Promise<ScheduleReplayResponse> => {
    const body: any = { video_path: videoPath };
    
    if (scheduledTime) {
      body.scheduled_time = scheduledTime;
    }
    
    if (platforms && platforms.length > 0) {
      body.platforms = platforms;
    }
    
    const response = await fetch(`${API_BASE_URL}/api/schedule-replay`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || 'Failed to schedule replay');
    }
    
    return await response.json();
  },

  /**
   * Schedule multiple missed replays at once, spaced 1 hour apart
   * @param videoPaths - Array of video file paths
   * @param platforms - Optional array of platforms. If not provided, uses configured platforms
   */
  scheduleBatch: async (
    videoPaths: string[],
    platforms?: string[]
  ): Promise<ScheduleBatchResponse> => {
    const body: any = { video_paths: videoPaths };
    
    if (platforms && platforms.length > 0) {
      body.platforms = platforms;
    }
    
    const response = await fetch(`${API_BASE_URL}/api/schedule-replays-batch`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || 'Failed to schedule batch');
    }
    
    return await response.json();
  }
};

