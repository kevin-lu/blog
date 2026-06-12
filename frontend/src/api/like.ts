import { apiClient } from '@/utils/api';

export interface LikeResponse {
  success: boolean;
  like_count: number;
  liked: boolean;
}

export interface ErrorResponse {
  error: string;
  message?: string;
}

/**
 * Generate or get session ID for anonymous users
 */
const getSessionId = (): string => {
  let sessionId = sessionStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
    sessionStorage.setItem('session_id', sessionId);
  }
  return sessionId;
};

/**
 * Like an article
 */
export const likeArticle = async (articleId: number): Promise<LikeResponse> => {
  const sessionId = getSessionId();
  const response = await apiClient.post<LikeResponse>(
    `/articles/${articleId}/like`,
    {},
    {
      headers: {
        'X-Session-ID': sessionId,
      },
    }
  );
  return response;
};

/**
 * Unlike an article
 */
export const unlikeArticle = async (articleId: number): Promise<LikeResponse> => {
  const sessionId = getSessionId();
  const response = await apiClient.delete<LikeResponse>(
    `/articles/${articleId}/unlike`,
    {
      headers: {
        'X-Session-ID': sessionId,
      },
    }
  );
  return response;
};

/**
 * Get article like status (for initial load)
 */
export const getLikeStatus = async (articleId: number): Promise<{ liked: boolean; like_count: number }> => {
  // For now, we'll get this from the article detail API
  // This is a placeholder for future dedicated endpoint
  return {
    liked: false,
    like_count: 0,
  };
};
