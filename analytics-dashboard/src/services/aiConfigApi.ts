/**
 * AI Configuration API Service
 */

import { API_BASE_URL } from '../config';

export interface AITemplate {
  id: number;
  name: string;
  prompt_text: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTemplateData {
  name: string;
  prompt_text: string;
  is_active?: boolean;
}

export interface UpdateTemplateData {
  name?: string;
  prompt_text?: string;
}

export interface TestPromptData {
  prompt_text: string;
  filename: string;
  game_context?: string;
}

export const aiConfigApi = {
  /**
   * Get all AI prompt templates
   */
  getTemplates: async (): Promise<AITemplate[]> => {
    const response = await fetch(`${API_BASE_URL}/api/ai/templates`);
    if (!response.ok) {
      throw new Error('Failed to fetch templates');
    }
    const data = await response.json();
    return data.templates;
  },

  /**
   * Get the currently active template
   */
  getActiveTemplate: async (): Promise<AITemplate | null> => {
    const response = await fetch(`${API_BASE_URL}/api/ai/templates/active`);
    if (!response.ok) {
      throw new Error('Failed to fetch active template');
    }
    const data = await response.json();
    return data.template;
  },

  /**
   * Create a new template
   */
  createTemplate: async (data: CreateTemplateData): Promise<{ success: boolean; template_id: number; message: string }> => {
    const response = await fetch(`${API_BASE_URL}/api/ai/templates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to create template');
    }
    return response.json();
  },

  /**
   * Update an existing template
   */
  updateTemplate: async (templateId: number, data: UpdateTemplateData): Promise<{ success: boolean; message: string }> => {
    const response = await fetch(`${API_BASE_URL}/api/ai/templates/${templateId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to update template');
    }
    return response.json();
  },

  /**
   * Delete a template
   */
  deleteTemplate: async (templateId: number): Promise<{ success: boolean; message: string }> => {
    const response = await fetch(`${API_BASE_URL}/api/ai/templates/${templateId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete template');
    }
    return response.json();
  },

  /**
   * Activate a template (deactivates all others)
   */
  activateTemplate: async (templateId: number): Promise<{ success: boolean; message: string }> => {
    const response = await fetch(`${API_BASE_URL}/api/ai/templates/${templateId}/activate`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to activate template');
    }
    return response.json();
  },

  /**
   * Test a prompt with sample data
   */
  testPrompt: async (data: TestPromptData): Promise<{ success: boolean; metadata: any }> => {
    const response = await fetch(`${API_BASE_URL}/api/ai/test-prompt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to test prompt');
    }
    return response.json();
  },
};

