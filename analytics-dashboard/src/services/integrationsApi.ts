import { API_BASE_URL } from '../config';

export interface DiscordWebhook {
  id: string;
  name: string;
  url: string;
  platforms: string[];
}

export interface DiscordWebhookCreateRequest {
  name: string;
  url: string;
  platforms: string[];
}

export interface DiscordWebhookUpdateRequest {
  name?: string;
  url?: string;
  platforms?: string[];
}

export interface DiscordWebhookTestRequest {
  webhook_url: string;
}

export interface DiscordWebhooksResponse {
  webhooks: DiscordWebhook[];
  count: number;
}

export interface ApiResponse {
  success: boolean;
  message: string;
  webhook_id?: string;
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
};

export const integrationsApi = {
  // Discord webhook management
  listDiscordWebhooks: async (): Promise<DiscordWebhooksResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/integrations/discord`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch Discord webhooks');
    return response.json();
  },

  createDiscordWebhook: async (webhook: DiscordWebhookCreateRequest): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/integrations/discord`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(webhook)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create Discord webhook');
    }
    return response.json();
  },

  updateDiscordWebhook: async (webhookId: string, updates: DiscordWebhookUpdateRequest): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/integrations/discord/${webhookId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(updates)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update Discord webhook');
    }
    return response.json();
  },

  deleteDiscordWebhook: async (webhookId: string): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/integrations/discord/${webhookId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete Discord webhook');
    }
    return response.json();
  },

  testDiscordWebhook: async (webhookUrl: string): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/integrations/discord/test`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ webhook_url: webhookUrl })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to test Discord webhook');
    }
    return response.json();
  }
};
