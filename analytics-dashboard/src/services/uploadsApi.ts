import { API_BASE_URL } from '../config';

export interface ScheduledPost {
  id: number;
  video_path: string;
  metadata: {
    title: string;
    caption?: string;
    hashtags?: string;
  };
  platforms: string[];
  scheduled_time: string;
  status: string;
  created_at: string;
  processed_at?: string;
  error_message?: string;
  retry_count: number;
}

export interface FailedUpload {
  key: string;
  video_path: string;
  platform: string;
  metadata: {
    title: string;
    caption?: string;
    hashtags?: string;
  };
  error: string;
  timestamp: string;
  retry_count: number;
}

export interface CompletedUpload {
  id: number;
  video_path: string;
  metadata: {
    title: string;
    caption?: string;
    hashtags?: string;
  };
  platforms: string[];
  platform_urls?: Record<string, {
    video_id: string;
    url: string;
  }>;
  scheduled_time: string;
  processed_at: string;
  status: string;
}

interface FailedUploadsResponse {
  success: boolean;
  failed_uploads: FailedUpload[];
  count: number;
}

interface CompletedUploadsResponse {
  posts: CompletedUpload[];
  count: number;
}

interface RetryUploadResponse {
  success: boolean;
  platform: string;
  url?: string;
  video_id?: string;
  error?: string;
}

interface RetryAllResponse {
  success: boolean;
  total: number;
  successful: number;
  failed: number;
  message: string;
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const uploadsApi = {
  /**
   * Get upcoming scheduled posts
   */
  getUpcoming: async (hours: number = 48): Promise<ScheduledPost[]> => {
    const response = await fetch(`${API_BASE_URL}/api/schedule/upcoming?hours=${hours}`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch scheduled posts: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.posts || [];
  },

  /**
   * Get a specific scheduled post by ID
   */
  getPost: async (postId: number): Promise<ScheduledPost> => {
    const response = await fetch(`${API_BASE_URL}/api/schedule/post/${postId}`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch post: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.post;
  },

  /**
   * Force a scheduled post to post immediately
   */
  forcePostNow: async (postId: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/schedule/post/${postId}/force`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Failed to force post: ${response.statusText}`);
    }
  },

  /**
   * Cancel a scheduled post
   */
  cancelPost: async (postId: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/schedule/post/${postId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Failed to cancel post: ${response.statusText}`);
    }
  },

  /**
   * Update metadata for a scheduled post
   */
  updateMetadata: async (
    postId: number,
    metadata: {
      title?: string;
      caption?: string;
      hashtags?: string;
      platforms?: string[];
    }
  ): Promise<void> => {
    const params = new URLSearchParams();
    if (metadata.title !== undefined) params.append('title', metadata.title);
    if (metadata.caption !== undefined) params.append('caption', metadata.caption);
    if (metadata.hashtags !== undefined) params.append('hashtags', metadata.hashtags);
    if (metadata.platforms) {
      metadata.platforms.forEach(p => params.append('platforms', p));
    }
    
    const response = await fetch(
      `${API_BASE_URL}/api/schedule/post/${postId}/metadata?${params.toString()}`,
      {
        method: 'PATCH',
        headers: getAuthHeaders()
      }
    );
    
    if (!response.ok) {
      throw new Error(`Failed to update metadata: ${response.statusText}`);
    }
  },

  /**
   * Get all failed uploads
   */
  getFailedUploads: async (): Promise<FailedUploadsResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/uploads/failed`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch failed uploads: ${response.statusText}`);
    }
    
    return await response.json();
  },

  /**
   * Retry a single failed upload
   */
  retryUpload: async (uploadKey: string): Promise<RetryUploadResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/uploads/retry/${uploadKey}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || 'Failed to retry upload');
    }
    
    return await response.json();
  },

  /**
   * Retry all failed uploads
   */
  retryAll: async (): Promise<RetryAllResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/uploads/retry-all`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Failed to retry all uploads: ${response.statusText}`);
    }
    
    return await response.json();
  },

  /**
   * Remove a failed upload from the retry queue
   */
  removeFailedUpload: async (uploadKey: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/uploads/failed/${uploadKey}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Failed to remove upload: ${response.statusText}`);
    }
  },

  /**
   * Get completed uploads from the last N days
   */
  getCompleted: async (days: number = 7): Promise<CompletedUpload[]> => {
    const response = await fetch(`${API_BASE_URL}/api/schedule/completed?days=${days}`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch completed uploads: ${response.statusText}`);
    }
    
    const data: CompletedUploadsResponse = await response.json();
    return data.posts || [];
  },

  /**
   * Get video URL for playback
   */
  getVideoUrl: (postId: number): string => {
    return `${API_BASE_URL}/api/video/serve/${postId}`;
  }
};

