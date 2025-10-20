const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data: T;
  error?: string;
}

interface AnalyticsOverview {
  total_uploads: number;
  successful_uploads: number;
  failed_uploads: number;
  uploads_by_platform: Record<string, number>;
  recent_uploads: Upload[];
}

interface Upload {
  id: number;
  platform: string;
  filename: string;
  video_id: string | null;
  video_url: string | null;
  status: string;
  created_at: string;
}

interface AnalyticsSummary {
  total_videos: number;
  total_views: number;
  total_likes: number;
  total_shares: number;
  total_comments: number;
  platforms: {
    youtube: PlatformStats;
    instagram: PlatformStats;
    tiktok: PlatformStats;
  };
  top_videos: VideoStats[];
}

interface PlatformStats {
  videos: number;
  views: number;
  likes: number;
  shares: number;
  comments: number;
  engagement_rate: number;
  most_popular: {
    title: string;
    views: number;
    likes: number;
    url: string;
  };
}

interface VideoStats {
  video_id: string;
  title: string;
  platform: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  platform_url: string;
}

class AnalyticsApi {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    try {
      const token = this.getToken();
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          this.clearToken();
          throw new Error('Unauthorized - please login again');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication
  async login(email: string, password: string): Promise<{ access_token: string; api_key: string }> {
    return this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, password: string): Promise<any> {
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  // Analytics endpoints (new backend API)
  async getAnalyticsOverview(days: number = 30): Promise<AnalyticsOverview> {
    return this.request(`/api/v1/analytics/overview?days=${days}`);
  }

  async getVideos(platform?: string, limit: number = 50, offset: number = 0): Promise<any> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (platform) {
      params.append('platform', platform);
    }
    return this.request(`/api/v1/analytics/videos?${params}`);
  }

  async getPlatformStats(days: number = 30): Promise<Record<string, any>> {
    return this.request(`/api/v1/analytics/platforms?days=${days}`);
  }

  // Legacy endpoints (for backward compatibility with old local API)
  async getAggregatedStats(): Promise<AnalyticsSummary> {
    return this.request<AnalyticsSummary>('/analytics/summary');
  }

  async getTotalViews(): Promise<{ total_views: number }> {
    return this.request<{ total_views: number }>('/channels/total-views');
  }

  async getChannelStats(): Promise<AnalyticsSummary> {
    return this.request<AnalyticsSummary>('/channels/stats');
  }

  async syncChannels(): Promise<{ message: string; synced_videos: number }> {
    return this.request<{ message: string; synced_videos: number }>('/channels/sync');
  }

  async getTopVideosWithMetrics(limit: number = 10, platform?: string): Promise<VideoStats[]> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (platform) {
      params.append('platform', platform);
    }
    return this.request<VideoStats[]>(`/videos/top-with-metrics?${params}`);
  }

  // Mock data for development when API is not available
  async getMockData(): Promise<AnalyticsSummary> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          total_videos: 59,
          total_views: 54179,
          total_likes: 3520,
          total_shares: 1,
          total_comments: 1117,
          platforms: {
            youtube: {
              videos: 32,
              views: 32500,
              likes: 1625,
              shares: 0,
              comments: 650,
              engagement_rate: 7.0,
              most_popular: {
                title: "we just embarrassed them at armagetron 😂💀",
                views: 5500,
                likes: 275,
                url: "https://youtube.com/watch?v=um_C6JLUJs8"
              }
            },
            instagram: {
              videos: 18,
              views: 14000,
              likes: 1400,
              shares: 0,
              comments: 463,
              engagement_rate: 13.3,
              most_popular: {
                title: "We rode the longest and heaviest train on earth across the sahara desert...",
                views: 2300,
                likes: 230,
                url: "https://www.instagram.com/p/Bxp5yPqhGzn/"
              }
            },
            tiktok: {
              videos: 9,
              views: 7679,
              likes: 495,
              shares: 1,
              comments: 4,
              engagement_rate: 0.0,
              most_popular: {
                title: "#UploadManager",
                views: 6297,
                likes: 456,
                url: "https://www.tiktok.com/@synarma/video/7559626577441541398"
              }
            }
          },
          top_videos: [
            {
              video_id: "7559626577441541398",
              title: "#UploadManager",
              platform: "TikTok",
              views: 6297,
              likes: 456,
              comments: 0,
              shares: 0,
              platform_url: "https://www.tiktok.com/@synarma/video/7559626577441541398"
            },
            {
              video_id: "um_C6JLUJs8",
              title: "we just embarrassed them at armagetron 😂💀",
              platform: "YouTube",
              views: 5500,
              likes: 275,
              comments: 110,
              shares: 0,
              platform_url: "https://youtube.com/watch?v=um_C6JLUJs8"
            },
            {
              video_id: "RMqojsE-GBQ",
              title: "we just obliterated them in armagetron 😂💀",
              platform: "YouTube",
              views: 5000,
              likes: 250,
              comments: 100,
              shares: 0,
              platform_url: "https://youtube.com/watch?v=RMqojsE-GBQ"
            },
            {
              video_id: "LqEBWPcXAB8",
              title: "Test Upload",
              platform: "YouTube",
              views: 4500,
              likes: 225,
              comments: 90,
              shares: 0,
              platform_url: "https://youtube.com/watch?v=LqEBWPcXAB8"
            },
            {
              video_id: "D5q1lAs2Ths",
              title: "Video Replay 2025-10-08 14-09-00_shorts",
              platform: "YouTube",
              views: 4000,
              likes: 200,
              comments: 80,
              shares: 0,
              platform_url: "https://youtube.com/watch?v=D5q1lAs2Ths"
            }
          ]
        });
      }, 1000);
    });
  }
}

export const analyticsApi = new AnalyticsApi();
